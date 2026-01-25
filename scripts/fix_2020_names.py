import os
import shutil
import yaml
import re

def clean_name(name):
    # Convert "snake_case_name" to "Snake Case Name"
    # Convert "Mixed Case Name" to "Mixed Case Name"
    # Keeps already title cased names
    if '_' in name:
        return name.replace('_', ' ').strip().title()
    return name

def main():
    base_dir = "data/statistics/2020/datasets"
    manifest_path = "data/statistics/2020/data_hierarchy_2020.yaml"
    
    if not os.path.exists(base_dir):
        print(f"Directory {base_dir} not found.")
        return

    print("Renaming folders...")
    
    renames = {}
    
    for folder_name in os.listdir(base_dir):
        path = os.path.join(base_dir, folder_name)
        if not os.path.isdir(path):
            continue
            
        new_name = clean_name(folder_name)
        if new_name != folder_name:
            print(f"Renaming: '{folder_name}' -> '{new_name}'")
            new_path = os.path.join(base_dir, new_name)
            
            # Handle potential collision if Title Name already exists?
            if os.path.exists(new_path):
                print(f"Warning: Target {new_path} already exists! Skipping rename.")
            else:
                shutil.move(path, new_path)
                renames[folder_name] = new_name

    print("Updating manifest...")
    
    if not os.path.exists(manifest_path):
        print(f"Manifest {manifest_path} not found.")
        return

    # Update manifest by string replacement to preserve structure/comments if possible
    # But usually simpler to load/dump if we don't care about comments.
    # The user asked to just move the folder, but the manifest points to specific paths.
    
    with open(manifest_path, 'r') as f:
        content = f.read()

    new_content = content
    for old, new in renames.items():
        # Path in manifest is datasets/Old_Name
        old_str = f"datasets/{old}"
        new_str = f"datasets/{new}"
        new_content = new_content.replace(old_str, new_str)
        
    with open(manifest_path, 'w') as f:
        f.write(new_content)
        
    print("Done.")

if __name__ == "__main__":
    main()
