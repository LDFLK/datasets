import os
import requests
from bs4 import BeautifulSoup
import re


# SSL Verification is enabled by default in requests


# Constants for paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SLTDA_PATH = os.path.join(BASE_DIR, "data", "sources", "statistics", "sltda")
SLBFE_PATH = os.path.join(BASE_DIR, "data", "sources", "statistics", "slbfe")
TREASURY_PATH = os.path.join(BASE_DIR, "data", "sources", "treasury", "budget")

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

def ensure_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

def download_file(url, folder, filename):
    ensure_dir(folder)
    filepath = os.path.join(folder, filename)
    
    if os.path.exists(filepath):
        print(f"File already exists: {filename}")
        return

    print(f"Downloading {filename} from {url}...")
    try:
        response = requests.get(url, headers=HEADERS, stream=True)
        response.raise_for_status()
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"Successfully downloaded: {filename}")
    except Exception as e:
        print(f"Failed to download {filename}: {e}")

def fetch_sltda():
    print("\n--- Fetching SLTDA Reports ---")
    url = "https://www.sltda.gov.lk/en/annual-statistical-report"
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
                clean_title = re.sub(r'[^\w\s-]', '', text).strip().lower().replace(' ', '_').replace('__', '_')
                filename = f"{year}_{clean_title}.pdf"
                
                if not href.startswith('http'):
                     href = "https://www.sltda.gov.lk" + href if href.startswith('/') else "https://www.sltda.gov.lk/" + href

                if href.lower().endswith('.pdf'):
                     download_file(href, SLTDA_PATH, filename)

    except Exception as e:
        print(f"Error fetching SLTDA: {e}")

def fetch_slbfe():
    print("\n--- Fetching SLBFE Reports ---")
    url = "https://www.slbfe.lk/annual-reports/"
    try:
        response = requests.get(url, headers=HEADERS)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        links = soup.find_all('a', href=True)
        
        for link in links:
             href = link['href']
             if not href.lower().endswith('.pdf'):
                 continue
                 
             filename_from_url = os.path.basename(href).lower()
             year_match = re.search(r'20\d{2}', filename_from_url)
             if not year_match:
                 text = link.get_text().strip()
                 year_match = re.search(r'20\d{2}', text)
            
             if year_match:
                 year = year_match.group(0)
                 clean_name = filename_from_url.replace('.pdf', '')
                 if not clean_name.startswith(year):
                     clean_name = f"{year}_{clean_name}"
                 
                 final_filename = f"{clean_name}.pdf"
                 download_file(href, SLBFE_PATH, final_filename)

    except Exception as e:
        print(f"Error fetching SLBFE: {e}")

def fetch_treasury():
    print("\n--- Fetching Treasury Budget Estimates ---")
    base_url = "https://www.treasury.gov.lk"
    
    # Download links extracted via browser automation
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
    
    for item in links_data:
        title = item['title']
        year = item['year']
        url = item['url']
        

        
        if not url.startswith("http"):
            url = base_url + url
            
        clean_title = title.lower().replace('|', '').replace(' ', '_').replace('__', '_').strip('_')
        clean_year = year.lower().replace(' ', '_')
        
        filename = f"{clean_year}_{clean_title}.pdf"
        download_file(url, TREASURY_PATH, filename)

if __name__ == "__main__":
    fetch_sltda()
    fetch_slbfe()
    fetch_treasury()
