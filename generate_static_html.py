#!/usr/bin/env python3
"""
Generate static HTML with CSS-only collapsible sections
No JavaScript needed - pure HTML/CSS solution
"""

import os
import json
import zipfile
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

def create_zip_for_section(section_path, section_name, output_dir="docs"):
    """Create a ZIP file for a specific section"""
    zip_filename = f"{section_name.replace(' ', '_').replace('(', '').replace(')', '')}_Data.zip"
    zip_path = os.path.join(output_dir, zip_filename)
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(section_path):
            for file in files:
                if file.endswith('.json'):
                    file_path = os.path.join(root, file)
                    # Create relative path from the section root
                    arcname = os.path.relpath(file_path, section_path)
                    zipf.write(file_path, arcname)
    
    return zip_filename

def generate_all_zips(data_path="data", output_dir="."):
    """Generate ZIP files for all major sections"""
    zip_files = {}
    
    if not os.path.exists(data_path):
        return zip_files
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate ZIP for each year
    for year in sorted(os.listdir(data_path)):
        year_path = os.path.join(data_path, year)
        if os.path.isdir(year_path):
            zip_filename = create_zip_for_section(year_path, year, output_dir)
            zip_files[year] = zip_filename
            print(f"📦 Generated {zip_filename}")
    
    return zip_files

def scan_data_folder(data_path="data", zip_files=None):
    """Scan the data folder and generate the structure"""
    if not os.path.exists(data_path):
        print(f"Error: {data_path} folder not found!")
        return ""
    
    def process_folder(folder_path, level=0, relative_path="", zip_files=None):
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
                
                # Add download button for year-level sections
                download_button = ""
                if level == 0 and zip_files and item in zip_files:
                    zip_filename = zip_files[item]
                    download_button = f' <a href="{zip_filename}" class="download-btn" download>📦 Download All {item} Data</a>'
                
                content.append(f'<summary class="summary">{emoji} {clean_display_name}{download_button}</summary>')
                content.append(process_folder(item_path, level + 1, item_relative_path, zip_files))
                content.append('</details>')
            else:
                if item == "data.json":
                    parent_name = os.path.basename(folder_path)
                    data_url = quote(f"data/{item_relative_path}")
                    
                    emoji = get_emoji_for_type(parent_name)
                    clean_display_name = clean_name(parent_name)
                    
                    # Check if metadata.json exists
                    metadata_path = os.path.join(folder_path, "metadata.json")
                    metadata_exists = os.path.exists(metadata_path)
                    
                    if metadata_exists:
                        metadata_url = quote(f"data/{item_relative_path.replace('data.json', 'metadata.json')}")
                        content.append(f'''<div class="dataset-item">
  <span class="dataset-name">{emoji} {clean_display_name}</span>
  <div class="dataset-links">
    <a href="#" onclick="showJsonData('{data_url}', 'data.json')" class="file-link">📄 data.json</a>
    <a href="#" onclick="showJsonData('{metadata_url}', 'metadata.json')" class="file-link">📄 metadata.json</a>
  </div>
</div>''')
                    else:
                        content.append(f'''<div class="dataset-item">
  <span class="dataset-name">{emoji} {clean_display_name}</span>
  <div class="dataset-links">
    <a href="#" onclick="showJsonData('{data_url}', 'data.json')" class="file-link">📄 data.json</a>
  </div>
</div>''')
        
        return "\n".join(content)
    
    return process_folder(data_path, zip_files=zip_files)

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
    
    # Generate ZIP files first
    print("📦 Generating ZIP files...")
    zip_files = generate_all_zips()
    
    css = generate_css()
    data_structure = scan_data_folder(zip_files=zip_files)
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
            <h1>Sri Lanka Government Statistics Datasets (2019–2023)</h1>
            <p>Browse by folder hierarchy, download all data for a year, or view and download a specific dataset.</p>
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
            <p>This data was collected and compiled by <em>Lanka Data Foundation</em> from public sources.</p>
            <p>For any inquiries please contact: <a href="mailto:contact@datafoundation.lk">contact@datafoundation.lk</a></p>
            <p>Codebase at: <a href="https://github.com/LDFLK/datasets" target="_blank" rel="noopener">https://github.com/LDFLK/datasets</a></p>
        </footer>
    </div>

    <!-- JSON Data Modal -->
    <div id="jsonModal" class="modal">
        <div class="modal-content">
            <div class="modal-header">
                <h3 id="modalTitle">JSON Data</h3>
                <span class="close">&times;</span>
            </div>
            <div class="modal-body">
                <pre id="jsonContent">Loading...</pre>
            </div>
            <div class="modal-footer">
                <button onclick="copyToClipboard()" class="copy-btn">📋 Copy to Clipboard</button>
                <button onclick="downloadJson()" class="download-btn">⬇️ Download</button>
            </div>
        </div>
    </div>

    <script>
        let currentJsonUrl = '';
        
        function showJsonData(url, filename) {{
            currentJsonUrl = url;
            document.getElementById('modalTitle').textContent = filename;
            document.getElementById('jsonContent').textContent = 'Loading...';
            document.getElementById('jsonModal').style.display = 'block';
            
            fetch(url)
                .then(response => response.json())
                .then(data => {{
                    document.getElementById('jsonContent').textContent = JSON.stringify(data, null, 2);
                }})
                .catch(error => {{
                    document.getElementById('jsonContent').textContent = 'Error loading data: ' + error.message;
                }});
        }}
        
        function copyToClipboard() {{
            const content = document.getElementById('jsonContent').textContent;
            navigator.clipboard.writeText(content).then(() => {{
                alert('Copied to clipboard!');
            }});
        }}
        
        function downloadJson() {{
            if (currentJsonUrl) {{
                const link = document.createElement('a');
                link.href = currentJsonUrl;
                link.download = '';
                link.click();
            }}
        }}
        
        // Close modal when clicking X
        document.querySelector('.close').onclick = function() {{
            document.getElementById('jsonModal').style.display = 'none';
        }}
        
        // Close modal when clicking outside
        window.onclick = function(event) {{
            const modal = document.getElementById('jsonModal');
            if (event.target == modal) {{
                modal.style.display = 'none';
            }}
        }}
    </script>
</body>
</html>"""
    
    output_path = "index.html"
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Generated {output_path}")
    print(f"📊 Found {dataset_count} datasets")
    print("🚀 Ready for GitHub Pages deployment!")

if __name__ == "__main__":
    main()
