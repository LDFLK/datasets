import os

# Base folder
BASE_DIR = "data"

hierarchy = {
    "2022": {
        "Sri Lanka": {
            "Government": {
                "Ranil Wickremesinghe": {
                    "Minister of Foreign Affairs": [
                        "org_structure",
                        "diplomatic_missions",
                        "official_communications",
                        "human_resoruces",
                    ],
                    "Minister of Investment Planning": {
                        "Department of Immigration and Emigration": [
                            "refused_foreign_entry",
                            "deported_foreign_nationals",
                            "asylum_seekers",
                            "refugees",
                            "fraudulent_visa",
                            "fake_passports",
                        ],
                    },
                    "Minister of Labour and Foreign Employment": {
                        "Sri Lanka Foreign Employment Bureau": [
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
                        ]
                    },
                    "Minister of Tourism and Lands": {
                        "Sri Lanka Tourism Development Authority": [ 
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
                        "accommodations_by_province_and_district",
                        "occupancy_rate_by_month",
                        "occupancy_rate_by_district",
                        "occupancy_rate_by_region"
                        ]
                    },
                }
            }
        }
    }
}

SKIP_LEVELS = {"2022", "Sri Lanka", "Government"}


def create_structure(base, hierarchy, parent=None):
    for name, content in hierarchy.items():
        path = os.path.join(base, name)
        os.makedirs(path, exist_ok=True)

        if isinstance(content, dict):
            create_structure(path, content, parent=name)
        elif isinstance(content, list):
            for dtype in content:
                dtype_path = os.path.join(path, dtype)
                os.makedirs(dtype_path, exist_ok=True)

                # Only add data.json & metadata.json if not a skip level
                if name not in SKIP_LEVELS:
                    for fixed_file in ["data.json", "metadata.json"]:
                        file_path = os.path.join(dtype_path, fixed_file)
                        if not os.path.exists(file_path):
                            with open(file_path, "w") as f:
                                f.write("{}")


create_structure(BASE_DIR, hierarchy)
print("✅ Folder structure generated in:", BASE_DIR)
