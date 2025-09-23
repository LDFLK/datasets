#!/usr/bin/env python3
"""
Generate static HTML with CSS-only collapsible sections
No JavaScript needed - pure HTML/CSS solution
"""

import os
import json
from pathlib import Path
from urllib.parse import quote

def get_emoji_for_type(folder_name):
    """Return appropriate emoji based on folder name"""
    emoji_map = {
        'diplomatic_missions': '📊',
        'human_resoruces': '👥',
        'org_structure': '🏢',
        'official_communications': '📰',
        'asylum_seekers': '🏃',
        'deported_foreign_nationals': '✈️',
        'fake_passports': '🆔',
        'fraudulent_visa': '📋',
        'refugees': '🏠',
        'refused_foreign_entry': '🚫',
        'complaints_recieved': '📝',
        'complaints_settled': '✅',
        'legal_division_performance': '⚖️',
        'local_arrivals': '🛬',
        'local_departures': '🛫',
        'monthly_foreign_exchange_earnings': '💰',
        'raids_conducted': '🔍',
        'remittances_by_country': '💸',
        'workers_remittances': '💼',
        'slbfe_registration': '📋',
        'annual_tourism_receipts': '💵',
        'location_vs_revenue_vs_visitors_count': '📍',
        'top_10_source_markets': '🏆',
        'accommodations': '🏨',
        'arrivals': '✈️',
        'occupancy_rate': '📈',
        'remittances': '💸',
        'ministry_news': '📰',
        'mission_news': '📰',
        'news_from_other_sources': '📰',
        'special_notices': '📢'
    }
    return emoji_map.get(folder_name, '📁')

def get_emoji_for_level(level):
    """Return emoji based on hierarchy level"""
    if level == 0:  # Year
        return '🗓️'
    elif level == 1:  # Government
        return '🏛️'
    elif level == 2:  # President
        return '👤'
    elif level == 3:  # Ministry
        return '🏛️'
    elif level == 4:  # Department
        return '🏢'
    else:
        return '📁'

def clean_name(name):
    """Clean folder names for display"""
    name = name.replace('(AS_CATEGORY)', '')
    name = name.replace('(government)', '')
    name = name.replace('(citizen)', '')
    name = name.replace('(minister)', '')
    name = name.replace('(department)', '')
    name = name.replace('_', ' ')
    return name.title()

def generate_css():
    """Generate CSS link for external stylesheet"""
    return """<link rel="stylesheet" href="styles.css">"""

def scan_data_folder(data_path="data"):
    """Scan the data folder and generate the structure"""
    if not os.path.exists(data_path):
        print(f"Error: {data_path} folder not found!")
        return ""
    
    def process_folder(folder_path, level=0, relative_path=""):
        """Recursively process folder structure"""
        content = []
        
        try:
            items = sorted(os.listdir(folder_path))
        except PermissionError:
            return ""
        
        for item in items:
            item_path = os.path.join(folder_path, item)
            item_relative_path = os.path.join(relative_path, item) if relative_path else item
            
            if os.path.isdir(item_path):
                emoji = get_emoji_for_level(level)
                clean_display_name = clean_name(item)
                css_class = ""
                
                if level == 0:
                    css_class = "year-section"
                elif level == 1 or level == 2:
                    css_class = "president-section"
                elif level == 3:
                    css_class = "ministry-section"
                elif level == 4:
                    css_class = "department-section"
                else:
                    css_class = "sub-section"  # For deeper levels
                
                content.append(f'<details class="details {css_class}">')
                content.append(f'<summary class="summary">{emoji} {clean_display_name}</summary>')
                content.append(process_folder(item_path, level + 1, item_relative_path))
                content.append('</details>')
            else:
                if item == "data.json":
                    metadata_path = os.path.join(folder_path, "metadata.json")
                    if os.path.exists(metadata_path):
                        parent_name = os.path.basename(folder_path)
                        data_url = quote(f"../data/{item_relative_path}")
                        metadata_url = quote(f"../data/{item_relative_path.replace('data.json', 'metadata.json')}")
                        
                        emoji = get_emoji_for_type(parent_name)
                        clean_display_name = clean_name(parent_name)
                        
                        content.append(f'''<div class="dataset-item">
  <span class="dataset-name">{emoji} {clean_display_name}</span>
  <div class="dataset-links">
    <a href="{data_url}" target="_blank">data.json</a>
    <a href="{metadata_url}" target="_blank">metadata.json</a>
  </div>
</div>''')
        
        return "\n".join(content)
    
    return process_folder(data_path)

def count_datasets(data_path="data"):
    """Count total datasets"""
    count = 0
    for root, dirs, files in os.walk(data_path):
        if "data.json" in files:
            count += 1
    return count

def main():
    """Main function to generate static HTML"""
    print("🔍 Scanning data folder...")
    
    css = generate_css()
    data_structure = scan_data_folder()
    dataset_count = count_datasets()
    
    content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sri Lanka Government Datasets (2019–2023)</title>
    <meta name="description" content="Browse cleaned public datasets by year, ministry, and department.">
    {css}
</head>
<body>
    <div class="container">
        <header>
            <h1>Sri Lanka Government Datasets (2019–2023)</h1>
            <p>Browse by folder hierarchy or jump to year pages. Links point into <code>data/</code> where the JSON lives.</p>
        </header>

        <div class="stats">
            <h3>📊 Dataset Statistics</h3>
            <p><strong>Total Years:</strong> 5 (2019-2023) | <strong>Total Datasets:</strong> {dataset_count} files | <strong>Ministries:</strong> 4 main categories</p>
        </div>

        <main>
            <h2>📊 Interactive Data Browser</h2>
            <p><em>Click on any section to expand/collapse it</em></p>
            {data_structure}
        </main>

        <footer>
            <h2>About</h2>
            <p>This documentation is automatically generated from the data folder structure.</p>
            <p>To update this page, run: <code>python generate_static_html.py</code></p>
            <p>Project notes: <a href="../README.md">README.md</a></p>
        </footer>
    </div>
</body>
</html>"""
    
    output_path = "docs/index.html"
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Generated {output_path}")
    print(f"📊 Found {dataset_count} datasets")
    print("🚀 Ready for GitHub Pages deployment!")
    print("💡 No JavaScript needed - pure HTML/CSS with collapsible sections!")

if __name__ == "__main__":
    main()
