#!/usr/bin/env bash
# Ingest statistics data for years 2020 to 2025.
# Waits 3 minutes between each year's ingestion.
# Run from the repository root: ./scripts/ingest_all_years.sh

set -e

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

for year in 2020 2021 2022 2023 2024 2025; do
  echo "=========================================="
  echo "Ingesting year: $year"
  echo "=========================================="
  python -m ingestion.ingest_data_yaml "data/statistics/${year}/data_hierarchy_${year}.yaml"
  if [[ "$year" != 2025 ]]; then
    echo "Waiting 3 minutes before next year..."
    sleep 180
  fi
done

echo "=========================================="
echo "All years (2020–2025) ingested."
echo "=========================================="
