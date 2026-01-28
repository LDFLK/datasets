import os
import requests
from bs4 import BeautifulSoup
import re

from urllib.parse import quote



BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SOURCES_DIR = os.path.join(BASE_DIR, "data", "sources")
SLTDA_DIR = os.path.join(SOURCES_DIR, "statistics", "sltda")
SLBFE_DIR = os.path.join(SOURCES_DIR, "statistics", "slbfe")
TREASURY_DIR = os.path.join(SOURCES_DIR, "treasury", "budget")

GITHUB_RAW_BASE = "https://github.com/LDFLK/datasets/raw/main/data/sources"
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

def get_sltda_map():
    print("Fetching SLTDA links...")
    url = "https://www.sltda.gov.lk/en/annual-statistical-report"
    mapping = {} # Year -> Source URL
    try:
        response = requests.get(url, headers=HEADERS)
        soup = BeautifulSoup(response.content, 'html.parser')
        links = soup.find_all('a', href=True)
        for link in links:
            text = link.get_text().strip()
            href = link['href']
            year_match = re.search(r'20\d{2}', text)
            text_lower = text.lower()
            if year_match and ("statistical" in text_lower or "year in review" in text_lower or "review" in text_lower):
                year = year_match.group(0)
                if not href.startswith('http'):
                     href = "https://www.sltda.gov.lk" + href if href.startswith('/') else "https://www.sltda.gov.lk/" + href
                mapping[year] = href
    except Exception as e:
        print(f"Error fetching SLTDA map: {e}")
    return mapping

def get_slbfe_map():
    print("Fetching SLBFE links...")
    url = "https://www.slbfe.lk/annual-reports/"
    mapping = {} # Year_Lang -> Source URL (Lang: english, sinhala, tamil)
    try:
        response = requests.get(url, headers=HEADERS)
        soup = BeautifulSoup(response.content, 'html.parser')
        links = soup.find_all('a', href=True)
        for link in links:
            href = link['href']
            if not href.lower().endswith('.pdf'): continue
            
            filename_from_url = os.path.basename(href).lower()
            text = link.get_text().strip().lower()

            # Year extraction
            year_match = re.search(r'20\d{2}', filename_from_url)
            if not year_match: year_match = re.search(r'20\d{2}', text)
            
            if year_match:
                year = year_match.group(0)
                lang = "unknown"
                full_str = (filename_from_url + " " + text).lower()
                if "english" in full_str: lang = "english"
                elif "sinhala" in full_str: lang = "sinhala"
                elif "tamil" in full_str: lang = "tamil"
                
                key = f"{year}_{lang}"
                mapping[key] = href
    except Exception as e:
        print(f"Error fetching SLBFE map: {e}")
    return mapping

def get_treasury_map():
    # Hardcoded from fetch_sources.py
    links_data = [
        {"year": "2025", "title": "English | Volume I", "url": "/api/file/fdf51693-6d93-4c85-b3d3-0e0e3353f7d9"},
        {"year": "2025", "title": "English | Volume II", "url": "/api/file/9fa040f5-f2be-424d-bad5-c90c90e23bff"},
        {"year": "2025", "title": "English | Volume III", "url": "/api/file/84d93cbc-da57-47cc-a45d-ed421c7892da"},
        {"year": "2024", "title": "English | Volume I", "url": "/api/file/7c6696fa-7764-469a-89ca-f7fbdf976527"},
        {"year": "2024", "title": "English | Volume II", "url": "/api/file/9fdc8882-9602-4b71-9252-09497e5b611f"},
        {"year": "2024", "title": "English | Volume III", "url": "/api/file/0c9a5957-c817-43f1-b1dc-e7708eaef605"},
        {"year": "2023", "title": "English | Volume I", "url": "/api/file/e286b9e4-59b1-406f-b324-12f2b46969f2"},
        {"year": "2023", "title": "English | Volume II", "url": "/api/file/f99d5173-a204-4acc-a684-e4581d0828ea"},
        {"year": "2023", "title": "English | Volume III", "url": "/api/file/02b4cd04-ddc5-449c-8809-90b8bb790954"},
        {"year": "2022", "title": "English | Volume I", "url": "/api/file/1d617e1d-482c-4adb-b652-1c58b4007895"},
        {"year": "2022", "title": "English | Volume II", "url": "/api/file/8842770a-0ed6-4d20-ac75-4ef40f8295c7"},
        {"year": "2022", "title": "English | Volume III", "url": "/api/file/e0e5c360-e254-4a48-8a95-137f271ac613"},
        {"year": "2022 Revised", "title": "English | Volume I", "url": "/api/file/33df4007-66d2-4b70-9aa7-e0b1e15bc0dc"},
        {"year": "2022 Revised", "title": "English | Volume II", "url": "/api/file/31da7494-54c9-4d97-b194-06921821bb64"},
        {"year": "2022 Revised", "title": "English | Volume III", "url": "/api/file/8372c7fe-5cfd-40ef-a0e6-eee682bef6ba"},
        {"year": "2021", "title": "English | Volume I", "url": "/api/file/249a21e4-3cfc-4d4d-8b4f-266faad40f4a"},
        {"year": "2021", "title": "English | Volume II", "url": "/api/file/c2110cb6-23a0-433f-8839-9ab864d38eb4"},
        {"year": "2021", "title": "English | Volume III", "url": "/api/file/316657bf-9737-4827-9c49-1d25ba400a62"}
    ]
    base_url = "https://www.treasury.gov.lk"
    mapping = {} # Key -> Source URL. Key: Year_Vol (e.g., 2025_1, 2022_Revised_1)
    
    for item in links_data:
        title = item['title'].lower()
        year = item['year']
        url = item['url']
        if not url.startswith("http"): url = base_url + url
        
        vol = "unknown"
        if "volume i" in title and "volume ii" not in title and "volume iii" not in title: vol = "1"
        elif "volume ii" in title and "volume iii" not in title: vol = "2"
        elif "volume iii" in title: vol = "3"
        
        is_revised = "revised" in year.lower()
        year_clean = year.split()[0]
        
        key_parts = [year_clean]
        if is_revised: key_parts.append("revised")
        key_parts.append(vol)
        
        key = "_".join(key_parts)
        mapping[key] = url
        
    return mapping

def generate_sltda_table(mapping):
    rows = []
    if not os.path.exists(SLTDA_DIR): return ""
    
    files = sorted([f for f in os.listdir(SLTDA_DIR) if f.endswith('.pdf')])
    for f in files:
        # File: sltda_annual_report_2020.pdf
        try:
            year = f.split('_')[-1].replace('.pdf', '')
            source_url = mapping.get(year, "N/A")
            if source_url != "N/A":
                source_url = quote(source_url, safe=':/')
            archive_url = f"{GITHUB_RAW_BASE}/statistics/sltda/{f}"
            
            rows.append(f"| {year} | Annual Report {year} | [Source]({source_url}) | [Archive]({archive_url}) |")
        except Exception as e:
            print(f"Error processing SLTDA file {f}: {e}")
            
    header = "| Year | Report Name | Source URL | Archive URL |\n|---|---|---|---|\n"
    return header + "\n".join(rows)

def generate_slbfe_table(mapping):
    rows = []
    if not os.path.exists(SLBFE_DIR): return ""
    
    files = sorted([f for f in os.listdir(SLBFE_DIR) if f.endswith('.pdf')])
    for f in files:
        # File: slbfe_annual_report_2020_english.pdf
        try:
            parts = f.replace('.pdf', '').split('_')
            year = parts[3]
            lang = parts[4]
            if lang != "english": continue
            
            key = f"{year}_{lang}"
            source_url = mapping.get(key, "N/A")
            if source_url != "N/A":
                 source_url = quote(source_url, safe=':/')
            archive_url = f"{GITHUB_RAW_BASE}/statistics/slbfe/{f}"
            
            rows.append(f"| {year} | Annual Report {year} ({lang.capitalize()}) | [Source]({source_url}) | [Archive]({archive_url}) |")
        except Exception as e:
            print(f"Error processing SLBFE file {f}: {e}")

    # Add 2024 N/A entry
    rows.append("| 2024 | Annual Report 2024 | N/A | N/A |")

    header = "| Year | Report Name | Source URL | Archive URL |\n|---|---|---|---|\n"
    return header + "\n".join(rows)

def generate_treasury_table(mapping):
    rows = []
    if not os.path.exists(TREASURY_DIR): return ""
    
    files = sorted([f for f in os.listdir(TREASURY_DIR) if f.startswith('treasury_budget_est_') and f.endswith('.pdf')])
    
    # Sort files naturally? standard sort is okay for now
    
    for f in files:
        # File: treasury_budget_est_2022_revised_vol_1.pdf or treasury_budget_est_2021_vol_1.pdf
        try:
            parts = f.replace('.pdf', '').split('_')
            # ['treasury', 'budget', 'est', '2021', 'vol', '1']
            # ['treasury', 'budget', 'est', '2022', 'revised', 'vol', '1']
            
            year = parts[3]
            is_revised = "revised" in parts
            vol = parts[-1]
            
            key_parts = [year]
            if is_revised: key_parts.append("revised")
            key_parts.append(vol)
            key = "_".join(key_parts)
            
            source_url = mapping.get(key, "N/A")
            if source_url != "N/A":
                source_url = quote(source_url, safe=':/')
            archive_url = f"{GITHUB_RAW_BASE}/treasury/budget/{f}"
            
            report_name = f"Budget Estimates {year} Volume {vol}"
            if is_revised: report_name += " (Revised)"
            
            rows.append(f"| {year} | {report_name} | [Source]({source_url}) | [Archive]({archive_url}) |")
        except Exception as e:
            print(f"Error processing Treasury file {f}: {e}")

    header = "| Year | Report Name | Source URL | Archive URL |\n|---|---|---|---|\n"
    return header + "\n".join(rows)

def get_treasury_activity_map():
    # Hardcoded from user request
    return {
        "2025_english": "https://www.treasury.gov.lk/api/file/57784431-d651-4f0f-bcca-5e4f940cd511",
        "2024_english": "https://www.treasury.gov.lk/api/file/27690ebf-87e9-47a3-84c2-23ec84e857b6",
        "2023_english": "https://www.treasury.gov.lk/api/file/817341f9-142b-44cc-a649-0e24000e49b0",
        "2022_english": "https://www.treasury.gov.lk/api/file/cfc0d87b-28ad-4041-8db6-3d84bb02aa4e",
        "2021_sinhala": "https://www.treasury.gov.lk/api/file/3dc5c10a-ef02-40f9-8bd0-4b72f7d643b2"
    }

def generate_treasury_activity_table(mapping):
    rows = []
    if not os.path.exists(TREASURY_DIR): return ""
    
    files = sorted([f for f in os.listdir(TREASURY_DIR) if f.startswith('activity_budget_') and f.endswith('.pdf')])
    
    # Add 2020 Not Found row at the start (or where appropriate)
    rows_data = [] # (year, string_row)
    
    # Add explicit entry for 2020
    rows_data.append((2020, "| 2020 | No Activity Budget document published | N/A | N/A |"))
    
    for f in files:
        # File: activity_budget_2025_english.pdf
        try:
            parts = f.replace('.pdf', '').split('_')
            # ['activity', 'budget', '2025', 'english']
            year = parts[2]
            lang = parts[3]
            
            key = f"{year}_{lang}"
            source_url = mapping.get(key, "N/A")
            if source_url != "N/A":
                source_url = quote(source_url, safe=':/')
            archive_url = f"{GITHUB_RAW_BASE}/treasury/budget/{f}"
            
            report_name = f"Activity Budget Estimates {year} ({lang.capitalize()})"
            
            rows_data.append((int(year), f"| {year} | {report_name} | [Source]({source_url}) | [Archive]({archive_url}) |"))
        except Exception as e:
            print(f"Error processing Treasury Activity file {f}: {e}")

    # Sort by year
    rows_data.sort(key=lambda x: x[0])
    
    final_rows = [r[1] for r in rows_data]

    header = "| Year | Report Name | Source URL | Archive URL |\n|---|---|---|---|\n"
    return header + "\n".join(final_rows)

def main():
    sltda_map = get_sltda_map()
    slbfe_map = get_slbfe_map()
    treasury_map = get_treasury_map()
    treasury_activity_map = get_treasury_activity_map()
    
    content = "# Data Sources\n\n"
    
    content += "## SLTDA Reports\n"
    content += generate_sltda_table(sltda_map) + "\n\n"
    
    content += "## SLBFE Reports\n"
    content += generate_slbfe_table(slbfe_map) + "\n\n"
    
    content += "## Treasury Budget Estimates\n"
    content += generate_treasury_table(treasury_map) + "\n\n"

    content += "## Treasury Activity Budget Estimates\n"
    content += generate_treasury_activity_table(treasury_activity_map) + "\n"
    
    with open(os.path.join(SOURCES_DIR, "README.md"), "w") as f:
        f.write(content)
    
    print("README.md updated successfully.")

if __name__ == "__main__":
    main()
