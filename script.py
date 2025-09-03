import os
import copy

BASE_DIR = "data"

# Template for ministries
TEMPLATES = {
    "foreign_affairs": [
        "org_structure",
        "diplomatic_missions",
        "official_communications",
        "human_resoruces",
    ],
    "immigration": [
        "refused_foreign_entry",
        "deported_foreign_nationals",
        "asylum_seekers",
        "refugees",
        "fraudulent_visa",
        "fake_passports",
    ],
    "foreign_employment": [
        "org_structure",
        "legal_division_performance",
        "complaints_recieved",
        "complaints_settled",
        "raids_conducted",
        "monthly_foreign_exchange_earnings",
        "workers_remittances",
        "remittances_by_country",
        "local_departures",
        "local_arrivals",
        "slbfe_registrations_by_gender",
        "slbfe_registrations_by_manpower_level",
        "slbfe_registrations_by_age",
        "slbfe_registrations_by_country",
        "slbfe_registrations_by_source",
        "slbfe_registrations_by_country_vs_manpower_level",
        "slbfe_registrations_by_manpower_level_vs_gender",
        "slbfe_registrations_by_age_vs_manpower_level",
        "slbfe_registrations_by_gender_vs_source",
        "slbfe_registrations_by_source_vs_country",
        "slbfe_registrations_by_district_vs_manpower_level_vs_gender",
    ],
    "tourism": [
        "org_structure",
        "location_vs_revenue_vs_visitors_count",
        "annual_tourism_receipts",
        "top_10_source_markets",
        "arrivals_by_country",
        "arrivals_by_port",
        "arrivals_by_carrier",
        "arrivals_by_purpose",
        "arrivals_by_age",
        "arrivals_by_sex",
        "arrivals_by_month",
        "arrivals_by_month_vs_country",
        "accommodations_by_province",
        "accommodations_by_district",
        "occupancy_rate_by_month",
        "occupancy_rate_by_district",
        "occupancy_rate_by_region",
    ],
}

# Year-specific mappings
YEARS = {
    "2022": {
        "Ranil Wickremesinghe": {
            "Minister of Foreign Affairs": TEMPLATES["foreign_affairs"],
            "Minister of Investment Planning": {
                "Department of Immigration and Emigration": TEMPLATES["immigration"],
            },
            "Minister of Labour and Foreign Employment": {
                "Sri Lanka Foreign Employment Bureau": TEMPLATES["foreign_employment"],
            },
            "Minister of Tourism and Lands": {
                "Sri Lanka Tourism Development Authority": TEMPLATES["tourism"],
            },
        }
    },
    "2023": None,  # copy from 2022
    "2020": {
        "Gotabaya Rajapaksa": {
            "Minister of Foreign Relations": TEMPLATES["foreign_affairs"],
            "State Minister of Internal Security, Home affairs and Disaster Management": {
                "Department of Immigration and Emigration": TEMPLATES["immigration"],
            },
            "State Minister of Foreign Employment Promotion and Market Diversification": {
                "Sri Lanka Foreign Employment Bureau": TEMPLATES["foreign_employment"],
            },
            "Minister of Tourism and Civil Aviation": {
                "Sri Lanka Tourism Development Authority": TEMPLATES["tourism"],
            },
        }
    },
    "2019": {
        "Gotabaya Rajapaksa": {
            "Minister of Foreign Affairs": TEMPLATES["foreign_affairs"],
            "Minister Not Found": {
                "Department of Immigration and Emigration": TEMPLATES["immigration"],
            },
            "Minister of Telecommunication, Foreign Employment and Sports": {
                "Sri Lanka Foreign Employment Bureau": TEMPLATES["foreign_employment"],
            },
            "Minister of Tourism Development, Wildlife and Christian Religious Affairs": {
                "Sri Lanka Tourism Development Authority": TEMPLATES["tourism"],
            },
        }
    },
}

# Fill missing years (copy)
YEARS["2023"] = copy.deepcopy(YEARS["2022"])

SKIP_LEVELS = {"2022", "2023", "2020", "2019", "Sri Lanka", "Government"}

def create_structure(base, hierarchy):
    for name, content in hierarchy.items():
        path = os.path.join(base, name)
        os.makedirs(path, exist_ok=True)

        if isinstance(content, dict):
            create_structure(path, content)
        elif isinstance(content, list):
            for dtype in content:
                dtype_path = os.path.join(path, dtype)
                os.makedirs(dtype_path, exist_ok=True)

                if name not in SKIP_LEVELS:
                    for fixed_file in ["data.json", "metadata.json"]:
                        file_path = os.path.join(dtype_path, fixed_file)
                        if not os.path.exists(file_path):
                            open(file_path, "w").close()


# Build all years
for year, data in YEARS.items():
    structure = {"Sri Lanka": {"Government": data}}
    create_structure(os.path.join(BASE_DIR, year), structure)

print("✅ Folder structures generated in:", BASE_DIR)
