# 🇱🇰 Sri Lanka Government Datasets (2019-2023)

> **Clean, structured datasets from Sri Lankan government sources**

## 📊 What's Inside

**5 Years of Data** | **4 Key Ministries** | **Multiple Departments**
- Foreign Affairs & Relations
- Immigration & Emigration  
- Foreign Employment
- Tourism Development

## 🗂️ Data Categories

- **🏛️ Foreign Affairs:** Diplomatic missions, communications, organizational data
- **🛂 Immigration:** Asylum seekers, visas, passports, refugee statistics
- **💼 Employment:** Worker complaints, remittances, registration data, legal performance
- **🏖️ Tourism:** Arrivals, accommodations, occupancy rates, revenue statistics


## 📋 Data Matrix

| Data Source | Dataset Category | Years Available | Collection Status | Verification Status |
|-------------|------------------|-----------------|-------------------|---------------------|
| M. Foreign Affairs | Diplomatic Missions | 2019-2023 | ✅ Collected | ⚠️ Pending |
| M. Foreign Affairs | Official Communications | 2019-2023 | ✅ Collected | ⚠️ Pending |
| Dept. Immigration | Asylum Seekers & Refugees | 2019-2023 | ✅ Collected | ⚠️ Pending |
| Dept. Immigration | Visas & Passports | 2019-2023 | ✅ Collected | ⚠️ Pending |
| Bur. Foreign Employment | Worker Complaints | 2019-2023 | ✅ Collected | ⚠️ Pending |
| Bur. Foreign Employment | Remittances & Earnings | 2019-2023 | ✅ Collected | ⚠️ Pending |
| Bur. Foreign Employment | Registrations (SLBFE) | 2019-2023 | ✅ Collected | ⚠️ Pending |
| Tourism Authority | Tourist Arrivals | 2019-2023 | ✅ Collected | ✅ Verified |
| Tourism Authority | Accommodations & Occupancy | 2019-2023 | ✅ Collected | ✅ Verified |
| Tourism Authority | Revenue Statistics | 2019-2023 | ✅ Collected | ✅ Verified |

## 📅 Years Available

- **2019** 
- **2020-2021**   
- **2022-2023** 

## 🚀 Quick Start

📖 **[Browse all data interactively →](docs/index.md)**

🌐 **[View online at GitHub Pages →](https://ldflk.github.io/datasets/docs/)**

All datasets are in clean JSON format with metadata .

This repository contains cleaned and organized datasets from various Sri Lankan government public sources, compiled by the Lanka Data Foundation. The data spans from 2019 to 2023 and covers multiple ministries and departments.

## 📊 Dataset Overview

- **Total Years:** 5 (2019-2023)
- **Total Datasets:** 175+ JSON files
- **Ministries Covered:** 4 main categories
- **Data Sources:** Public government sources

## 🏗️ Repository Structure

```
datasets/
├── data/                           # Main data directory
│   ├── 2019/                      # Year-based organization
│   ├── 2020/
│   ├── 2021/
│   ├── 2022/
│   └── 2023/
├── generate_static_html.py         # HTML generator script
├── index.html                      # Generated static HTML
├── styles.css                      # CSS stylesheet
└── README.md                       # This file
```

## 📁 Data Organization

Data is organized hierarchically:
- **Year** → **Government** → **President** → **Ministry** → **Department** → **Data Files**

### Data File Structure
Each dataset contains:
- `data.json` - The main dataset
- `metadata.json` - Metadata about the dataset (optional)

## 🔄 How to Update Data and Regenerate HTML

### 1. Adding New Data

#### Adding Data for a New Year
1. Create a new folder under `data/` (e.g., `data/2024/`)
2. Follow the existing folder structure:
   ```
   data/2024/
   └── Government of Sri Lanka(government)/
       └── [President Name](citizen)/
           └── [Ministry Name](minister)/
               └── [Department Name](department)/
                   ├── [category]/
                   │   ├── data.json
                   │   └── metadata.json (optional)
   ```

#### Adding Data to Existing Year
1. Navigate to the appropriate year folder in `data/`
2. Follow the existing hierarchy to find the correct ministry/department
3. Add your `data.json` and optional `metadata.json` files

#### Data File Requirements
- **data.json**: Must contain valid JSON data
- **metadata.json**: Optional, should contain dataset metadata (description, source, etc.)
- Files must be placed in appropriately named folders with category indicators

### 2. Update the Website (Optional)

The API documentation website is built with Jekyll on GitHub Pages. The data listing is auto-generated and injected into `docs/index.md`.

To update the data listing:

1.  Run the update script:
    ```bash
    python3 update_dataset_index.py
    ```
2.  This will:
    *   Scan the `data/` directory.
    *   Generate ZIP files for each year.
    *   Inject the file listing into `docs/index.md`.
3.  Commit and push changes to `main` branch.

### 3. What Gets Generated

#### ZIP Files
- Automatically created for each year folder
- Contains all JSON files from that year
- Named as `[YEAR]_Data.zip` (e.g., `2019_Data.zip`)

#### HTML Features
- Interactive collapsible sections
- Download buttons for yearly ZIP files
- In-browser JSON viewer with copy/download functionality
- Responsive design with CSS styling

### 4. Folder Structure Guidelines

#### Special Naming Conventions
- Use `(government)`, `(citizen)`, `(minister)`, `(department)` suffixes for proper categorization
- Use `(AS_CATEGORY)` for sub-categories
- Underscores in folder names will be converted to spaces in display

### 5. Customization

#### Adding New Emojis
Edit the `get_emoji_for_type()` function in `generate_static_html.py`:
```python
emoji_map = {
    'your_category': '🎯',
    # ... existing mappings
}
```

#### Modifying CSS
Edit `styles.css` to customize the appearance:
- Colors, fonts, spacing
- Responsive breakpoints
- Modal styling for JSON viewer

#### Updating Statistics
The script automatically counts datasets, but you can manually update the description in the `main()` function.

## 🚀 Deployment

The generated `index.html` is ready for deployment on:
- GitHub Pages
- Any static hosting service
- Local web servers

## 📞 Contact

For any enquiries please contact: [contact@datafoundation.lk](mailto:contact@datafoundation.lk)

Codebase at: [https://github.com/LDFLK/datasets](https://github.com/LDFLK/datasets)

## 📄 License

See [LICENSE](LICENSE) file for details.
