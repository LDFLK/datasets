# Sri Lanka Government Datasets (2019-2023)

This repository contains cleaned datasets from various Sri Lankan government public sources, organized by year, ministry, and department for application development.

## 📁 Data Structure Overview

The data is organized in a hierarchical structure: `Year → Country/Government → Leader → Ministry → Department → Data Categories`

## 📅 Year-by-Year Structure Guide

### 🗓️ **2019** - Complex Structure with (AS_CATEGORY) System
**Government:** Government(government)  
**Leader:** Gotabaya Rajapaksha(citizen)

**Ministries & Departments:**
- **Minister of Foreign Affairs(minister)**
  - Basic data: diplomatic_missions, human_resources, org_structure
  - Official communications with complex nested structure:
    - ministry_news → Media Releases from Ministry of Foreign Affairs
    - mission_news → Media Releases from Ministry of Foreign Affairs  
    - news_from_other_sources → Media Releases from Ministry of Foreign Affairs

- **Minister of Internal and Home Affairs and Provincial Councils and Local Government(minister)**
  - Department of Immigration and Emigration(department)
    - asylum_seekers, deported_foreign_nationals, fake_passports
    - fraudulent_visa, refugees, refused_foreign_entry

- **Minister of Telecommunication, Foreign Employment and Sports(minister)**
  - Sri Lanka Foreign Employment Bureau(department)
    - Basic services: complaints_received/settled, legal_division_performance
    - Statistics: local_arrivals/departures, monthly_foreign_exchange_earnings
    - Operations: org_structure, raids_conducted, remittances_by_country, workers_remittances
    - Complex SLBFE registration system:
      - by_country → SLBFE_registration_by_country
      - by_gender → SLBFE_registration_by_gender
      - by_manpower_level → SLBFE_registration_by_manpower_level

- **Minister of Tourism Development, Wildlife and Christian Religious Affairs(minister)**
  - Sri Lanka Tourism Development Authority(department)
    - Simple data: annual_tourism_receipts, location_vs_revenue_vs_visitors_count, org_structure, top_10_source_markets
    - Complex accommodation system:
      - by_district → accommodation_capacity_by_district
      - by_province → accommodation_capacity_by_resort_region
    - Complex arrivals system:
      - by_age → tourist_arrivals_by_age_group
      - by_carrier → tourist_arrivals_by_carrier
      - by_country → tourist_arrivals_by_country_of_residence
      - by_month → tourist_arrivals_by_month
      - by_port → tourist_arrivals_by_port
      - by_purpose → tourist_arrivals_by_purpose_of_visit
      - by_sex → tourist_arrivals_by_gender
      - month_vs_country → tourist_arrivals_by_country_and_month
    - Complex occupancy rate system:
      - by_district → occupancy_rates_by_district
      - by_month → occupancy_rates_by_month
      - by_region → occupancy_rates_by_resort_region

---

### 🗓️ **2020** - Simplified Structure
**Country:** Sri Lanka  
**Government:** Government  
**Leader:** Gotabaya Rajapaksa

**Ministries & Departments:**
- **Minister of Foreign Relations**
  - Basic data: diplomatic_missions, human_resources, org_structure
  - Official communications with subdirectories

- **Minister of Tourism and Civil Aviation**
  - Sri Lanka Tourism Development Authority
    - Simple data: annual_tourism_receipts, location_vs_revenue_vs_visitors_count, org_structure, top_10_source_markets
    - Accommodations: by_district, by_province
    - Arrivals: by_age, by_carrier, by_country, by_month, by_port, by_purpose, by_sex, month_vs_country
    - Occupancy rates: by_district, by_month, by_region

- **State Minister of Foreign Employment Promotion and Market Diversification**
  - Sri Lanka Foreign Employment Bureau
    - Basic services: complaints_received/settled, legal_division_performance
    - Statistics: local_arrivals/departures, monthly_foreign_exchange_earnings
    - Operations: org_structure, raids_conducted, workers_remittances
    - Remittances: by_country, by_region
    - SLBFE registration: by_age, by_age_vs_manpower_level, by_country, by_country_vs_manpower_level, by_district_vs_manpower_level_vs_gender, by_gender, by_gender_vs_source, by_manpower_level, by_manpower_level_vs_gender, by_source, by_source_vs_country

- **State Minister of Internal Security, Home affairs and Disaster Management**
  - Department of Immigration and Emigration
    - asylum_seekers, deported_foreign_nationals, fake_passports
    - fraudulent_visa, refugees, refused_foreign_entry

---

### 🗓️ **2021** - Similar to 2020 Structure
**Country:** Sri Lanka  
**Government:** Government  
**Leader:** Gotabaya Rajapaksa

**Note:** Similar structure to 2020 with same ministries and departments.

---

### 🗓️ **2022** - Restructured Government
**Country:** Government of Sri Lanka(government)  
**Leader:** Ranil Wickremesinghe(citizen)

**Special Portfolio Notes:**
- Minister of Foreign Employment is in portfolio with Minister of Labour
- Minister of Tourism is in portfolio with Minister of Lands  
- Department of Immigration and Emigration is under Minister of Investment Planning

**Ministries & Departments:**
- **Minister of Foreign Affairs(minister)**
- **Minister of Investment Planning(minister)**
  - Department of Immigration and Emigration(department)
- **Minister of Labour and Foreign Employment(minister)**
  - Sri Lanka Foreign Employment Bureau(department)
- **Minister of Tourism and Lands(minister)**
  - Sri Lanka Tourism Development Authority(department)

---

### 🗓️ **2023** - Consistent with 2022 Structure
**Country:** Sri Lanka  
**Government:** Government  
**Leader:** Ranil Wickremesinghe

**Note:** Similar ministerial structure to 2022 but with cleaner path organization.

## 📊 Data Categories Available

### Immigration & Security
- Asylum seekers data
- Deported foreign nationals
- Fake passports incidents
- Fraudulent visa cases
- Refugee statistics
- Refused foreign entry records

### Foreign Employment
- Worker complaints (received & settled)
- Legal division performance
- Local arrivals & departures
- Monthly foreign exchange earnings
- Organizational structure
- Raids conducted
- Remittances (by country/region)
- SLBFE registration statistics
- Workers' remittances

### Tourism
- Accommodation capacity (by district/province/region)
- Annual tourism receipts
- Tourist arrivals (by age/carrier/country/month/port/purpose/sex)
- Occupancy rates
- Top source markets
- Location vs revenue vs visitor count

### Foreign Affairs
- Diplomatic missions
- Human resources
- Official communications
- Organizational structure

## 🔧 Technical Notes

### File Structure
- Each data category contains `data.json` and `metadata.json` files
- All JSON files are cleaned and standardized for application development
- Complex nested structures use specific naming conventions for final data directories

### Path Encoding
- Special characters in folder names are URL-encoded in links
- Parentheses notation like `(government)`, `(citizen)`, `(minister)`, `(department)` indicates entity types
- 2019 uses `(AS_CATEGORY)` system for complex nested structures

### Access
- Browse interactively using the [index.md](docs/index.md) file
- All links are verified and functional
- Data spans 2019-2023 with consistent JSON format across years

## 📈 Data Quality

- **2019:** Most complex structure with nested categorical systems
- **2020-2021:** Simplified, clean hierarchical organization  
- **2022-2023:** Restructured government with updated ministerial portfolios
- **All years:** 100% verified functional links to data files