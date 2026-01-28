import os
import re

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SLTDA_PATH = os.path.join(BASE_DIR, "data", "sources", "statistics", "sltda")
SLBFE_PATH = os.path.join(BASE_DIR, "data", "sources", "statistics", "slbfe")
TREASURY_PATH = os.path.join(BASE_DIR, "data", "sources", "treasury", "budget")

def rename_sltda():
    print("\n--- Renaming SLTDA Files ---")
    if not os.path.exists(SLTDA_PATH):
        print(f"Directory not found: {SLTDA_PATH}")
        return

    for filename in os.listdir(SLTDA_PATH):
        if not filename.endswith(".pdf"):
            continue
            
        # Match year at start
        year_match = re.search(r'(20\d{2})', filename)
        if year_match:
            year = year_match.group(1)
            new_name = f"sltda_annual_report_{year}.pdf"
            
            if new_name != filename:
                old_path = os.path.join(SLTDA_PATH, filename)
                new_path = os.path.join(SLTDA_PATH, new_name)
                os.rename(old_path, new_path)
                print(f"Renamed: {filename} -> {new_name}")
            else:
                print(f"Skipped (already correct): {filename}")

def rename_slbfe():
    print("\n--- Renaming SLBFE Files ---")
    if not os.path.exists(SLBFE_PATH):
        print(f"Directory not found: {SLBFE_PATH}")
        return

    for filename in os.listdir(SLBFE_PATH):
        if not filename.endswith(".pdf"):
            continue

        filename_lower = filename.lower()
        
        # Extract Year
        year_match = re.search(r'20\d{2}', filename)
        if not year_match:
            print(f"Could not extract year from: {filename}")
            continue
        year = year_match.group(0)

        # Extract Language
        lang = "unknown"
        if "english" in filename_lower:
            lang = "english"
        elif "sinhala" in filename_lower:
            lang = "sinhala"
        elif "tamil" in filename_lower:
            lang = "tamil"
        
        new_name = f"slbfe_annual_report_{year}_{lang}.pdf"
        
        if new_name != filename:
            old_path = os.path.join(SLBFE_PATH, filename)
            new_path = os.path.join(SLBFE_PATH, new_name)
            os.rename(old_path, new_path)
            print(f"Renamed: {filename} -> {new_name}")
        else:
            print(f"Skipped (already correct): {filename}")

def rename_treasury():
    print("\n--- Renaming Treasury Files ---")
    if not os.path.exists(TREASURY_PATH):
        print(f"Directory not found: {TREASURY_PATH}")
        return

    for filename in os.listdir(TREASURY_PATH):
        if not filename.endswith(".pdf"):
            continue
        
        filename_lower = filename.lower()

        # Extract Year
        year_match = re.search(r'(20\d{2})', filename)
        if not year_match:
             print(f"Could not extract year from: {filename}")
             continue
        year = year_match.group(1)

        # Check Revised
        is_revised = "revised" in filename_lower

        # Extract Volume
        if "activity_budget" in filename_lower:
             continue

        # Extract Volume
        vol_num = "unknown"
        if "volume_iii" in filename_lower:
             vol_num = "3"
        elif "volume_ii" in filename_lower:
             vol_num = "2"
        elif "volume_i" in filename_lower:
             vol_num = "1"
        elif "vol_1" in filename_lower:
             vol_num = "1"
        elif "vol_2" in filename_lower:
             vol_num = "2"
        elif "vol_3" in filename_lower:
             vol_num = "3"
        
        # Construct new name
        # treasury_budget_est_<YYYY>_<REV>_vol_<NUM>.pdf
        parts = ["treasury_budget_est", year]
        if is_revised:
            parts.append("revised")
        parts.append(f"vol_{vol_num}")
        
        new_name = "_".join(parts) + ".pdf"

        if new_name != filename:
            old_path = os.path.join(TREASURY_PATH, filename)
            new_path = os.path.join(TREASURY_PATH, new_name)
            os.rename(old_path, new_path)
            print(f"Renamed: {filename} -> {new_name}")
        else:
            print(f"Skipped (already correct): {filename}")

if __name__ == "__main__":
    rename_sltda()
    rename_slbfe()
    rename_treasury()
