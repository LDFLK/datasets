import argparse
import os
import shutil
import json
import yaml
import re

def parse_args():
    parser = argparse.ArgumentParser(description="Replicate flat structure and generate manifest for a given year.")
    parser.add_argument("year", type=str, help="The year to process (e.g., 2019)")
    return parser.parse_args()

def extract_hierarchy(path, src_root):
    # Relativize path from src_root
    rel_path = os.path.relpath(path, src_root)
    parts = rel_path.split(os.sep)
    
    hierarchy = {}
    
    # Iterate through parts to find hierarchy components
    # We expect structure roughly like:
    # .../Name(minister)/[Name(department)]/Name(AS_CATEGORY)/...
    
    # Helper to clean name
    def clean_name(name_part):
        return re.sub(r'\(.*?\)$', '', name_part).strip()

    categories = []
    
    for part in parts:
        if '(minister)' in part:
            hierarchy['minister'] = clean_name(part)
        elif '(department)' in part:
            hierarchy['department'] = clean_name(part)
        elif '(AS_CATEGORY)' in part:
            categories.append(clean_name(part))
            
    hierarchy['categories'] = categories
    return hierarchy

def build_manifest_structure(manifest_list, hierarchy, dataset_path, dataset_name):
    """
    Recursively builds the manifest structure list.
    """
    
    # 1. Find or Create Minister
    minister_name = hierarchy.get('minister')
    if not minister_name:
        # Fallback or error if no minister found? 
        # For now, let's assume valid structure requires a minister.
        return 

    minister_entry = next((item for item in manifest_list if item.get('name') == minister_name), None)
    if not minister_entry:
        minister_entry = {'name': minister_name}
        manifest_list.append(minister_entry)
        
    current_context = minister_entry
    
    # 2. Handle Department (Optional)
    department_name = hierarchy.get('department')
    if department_name:
        if 'department' not in current_context:
            current_context['department'] = []
        
        dept_list = current_context['department']
        dept_entry = next((item for item in dept_list if item.get('name') == department_name), None)
        if not dept_entry:
            dept_entry = {'name': department_name}
            dept_list.append(dept_entry)
        current_context = dept_entry

    # 3. Handle Categories (Recursive subcategories)
    cats = hierarchy.get('categories', [])
    
    for cat_name in cats:
        if 'category' not in current_context and 'subcategory' not in current_context:
             # If we are under minister/department, map likely starts with 'category'
             # If we are already in a category, nested ones might be 'subcategory'
             # Based on manifest_2020.yaml observation:
             # Minister -> category (official_communications) -> subcategory (news)
             # Minister -> department -> category -> subcategory
             
             # Heuristic: First level is 'category', subsequent are 'subcategory'
             # But checks existing keys to decide.
             pass

        # To simplify, let's look at where we are.
        # If current_context has 'category', we search there.
        # If current_context has 'subcategory', we search there.
        # But wait, a node can have multiple categories.
        
        # We need a unified list to search in.
        # In manifest_2020:
        # Top level (Minister/Dept) has 'category': [...]
        # Inside 'category' node, we have 'subcategory': [...]
        
        list_key = 'category' if ('name' in current_context and ('Minister' in current_context.get('name', '') or department_name == current_context.get('name', ''))) else 'subcategory'
        
        # Check if we are physically inside a department or minister node (which use 'category')
        # vs a category node (which uses 'subcategory')
        # Actually manifest 2020 uses:
        # Minister -> category
        # Minister -> subcategory (Wait, lines 4-5: category -> subcategory)
        # Minister -> department -> category -> subcategory
        
        # So: Minister/Department use 'category'. Category uses 'subcategory'.
        
        # Let's enforce this logic:
        # If we are at Minister or Department level, look for 'category' list.
        # Else look for 'subcategory' list.
        
        # Exception: A Minister might assume direct categories? Yes.
        
        # Simple distinct check:
        # If current_context is Minister or Department (has 'department' key or is root item?), use 'category'
        # But root item is list. 'current_context' is a dict.
        
        # We can imply level by checking if we just processed a dept or minister.
        # However, recursive step is easier if we just look at the object.
        # A category object has 'name' and 'subcategory' or 'datasets'.
        # A minister/dept object has 'name' and 'category' (or 'department' for minister).
        
        # Let's try to detect if we are in a "container" (Minister/Dept) or "Category".
        # We can default to 'category' if the list doesn't exist, unless we are deep.
        # Actually, simpler: The first item in `cats` list corresponds to 'category' under Minister/Dept.
        # Subsequent items in `cats` are 'subcategory'.
        
        target_list_key = 'category' if cat_name == cats[0] else 'subcategory'
        
        if target_list_key not in current_context:
            current_context[target_list_key] = []
        
        cat_list = current_context[target_list_key]
        cat_entry = next((item for item in cat_list if item.get('name') == cat_name), None)
        if not cat_entry:
            cat_entry = {'name': cat_name}
            cat_list.append(cat_entry)
        current_context = cat_entry

    # 4. Add Dataset
    if 'datasets' not in current_context:
        current_context['datasets'] = []
    
    # Avoid duplicates
    if dataset_path not in current_context['datasets']:
        current_context['datasets'].append(dataset_path)


def clean_folder_name(name):
    """
    Cleans a folder name for filesystem and readability.
    e.g. "by_age(AS_CATEGORY)" -> "by_age"
    """
    # Remove metadata tags like (AS_CATEGORY)
    name = re.sub(r'\(.*?\)$', '', name).strip()
    return name

def format_name(name):
    """
    Formats a name to be more title-like if it looks snake_case
    e.g. "news_from_other_sources" -> "News From Other Sources"
    """
    if '_' in name:
        return name.replace('_', ' ').title()
    return name

def main():
    args = parse_args()
    year = args.year
    
    src_dir = f"data/{year}"
    base_dst_dir = f"data/statistics/{year}"
    dst_datasets_dir = os.path.join(base_dst_dir, "datasets")
    
    if not os.path.exists(src_dir):
        print(f"Error: Source directory {src_dir} does not exist.")
        return

    print(f"Scanning datasets in {src_dir}...")
    
    # 1. Collect all potential datasets
    datasets = []
    
    for root, dirs, files in os.walk(src_dir):
        if 'data.json' in files:
            # Found a dataset
            
            # Read metadata
            meta_path = os.path.join(root, 'metadata.json')
            dataset_name = "Unknown Dataset"
            if os.path.exists(meta_path):
                try:
                    with open(meta_path, 'r') as f:
                        meta = json.load(f)
                        dataset_name = meta.get('dataset_name', dataset_name)
                except Exception as e:
                    print(f"Warning: Could not read metadata at {meta_path}: {e}")
            
            # Initial Safe Name
            safe_name = "".join([c for c in dataset_name if c.isalpha() or c.isdigit() or c in (' ', '-', '_')]).strip()
            # Enforce Title Case conversion for safe_name too
            safe_name = format_name(clean_folder_name(safe_name))

            if not safe_name:
                safe_name = os.path.basename(root)
            
            datasets.append({
                'path': root,
                'meta_dataset_name': dataset_name,
                'safe_name': safe_name,
                'meta_path': meta_path
            })

    # 2. Resolve Collisions
    # Group by safe_name
    name_map = {}
    for d in datasets:
        name = d['safe_name']
        if name not in name_map:
            name_map[name] = []
        name_map[name].append(d)
        
    final_processing_list = []
    
    for name, conflict_list in name_map.items():
        if len(conflict_list) == 1:
            # No collision
            d = conflict_list[0]
            d['final_name'] = name
            final_processing_list.append(d)
        else:
            # Collision detected
            print(f"Collision detected for '{name}': {len(conflict_list)} datasets.")
            for d in conflict_list:
                # Disambiguate using parent folder name
                # Hierarchy: .../Parent/Current
                path_parts = d['path'].split(os.sep)
                
                # Current folder is likely the one containing data.json
                # Parent is path_parts[-2] if available
                # But typically structure is .../Category/DateasetName
                # Let's try to find a meaningful parent.
                
                # Check parents in reverse order, looking for categories
                disambiguator = ""
                for part in reversed(path_parts[:-1]): # skip current folder
                     if '(AS_CATEGORY)' in part:
                         disambiguator = clean_folder_name(part)
                         break
                
                if not disambiguator:
                    # Fallback to immediate parent
                    disambiguator = clean_folder_name(path_parts[-2])
                
                # Format disambiguator
                disambiguator = format_name(disambiguator)
                
                # New name: Disambiguator (matches 2020 style better for News)
                # Or "Dataset Name - Disambiguator"
                # For "Media Releases...", parent was "Mission News". 
                # If we just use "Mission News", it matches 2020.
                
                print(f"  Resolving collision for {d['path']} -> Using '{disambiguator}'")
                d['final_name'] = disambiguator
                final_processing_list.append(d)
                
    # Check for collisions AGAIN after resolution?
    # In rare cases, disambiguation might still collide (e.g. if parents are same? Impossible given paths are unique)
    # But "clean_folder_name" might map distinct folders to same name.
    # Let's do a simple unique check/append
    
    used_names = {}
    
    print(f"Refining final names...")
    manifest_list = []

    for d in final_processing_list:
        final_name = d['final_name']
        original_final_name = final_name
        counter = 1
        while final_name in used_names:
             final_name = f"{original_final_name}_{counter}"
             counter += 1
        
        used_names[final_name] = True
        d['final_name'] = final_name
        
        # Now Execute Copy
        src_root = d['path']
        target_path = os.path.join(dst_datasets_dir, final_name)
        os.makedirs(target_path, exist_ok=True)
        
        shutil.copy2(os.path.join(src_root, 'data.json'), os.path.join(target_path, 'data.json'))
        if os.path.exists(d['meta_path']):
             shutil.copy2(d['meta_path'], os.path.join(target_path, 'metadata.json'))
             
        # Build Manifest
        manifest_dataset_path = f"datasets/{final_name}"
        hierarchy = extract_hierarchy(src_root, src_dir)
        dataset_name = d['meta_dataset_name'] # Use original meta name for display/logic if needed, or final_name?
        # Manifest usually uses directory structure keys, but the 'datasets' list points to the path.
        
        build_manifest_structure(manifest_list, hierarchy, manifest_dataset_path, dataset_name)
        print(f"Processed: {dataset_name} ({d['safe_name']}) -> {target_path}")

    # Write Manifest
    manifest_path = os.path.join(base_dst_dir, f"data_hierarchy_{year}.yaml")
    with open(manifest_path, 'w') as f:
        yaml.dump(manifest_list, f, sort_keys=False, default_flow_style=False)
        
    print(f"Generated manifest at {manifest_path}")

if __name__ == "__main__":
    main()
