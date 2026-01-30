# Sri Lanka Government Statistics Datasets

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0) 
[![Code of Conduct](https://img.shields.io/badge/Code%20of%20Conduct-Contributor-ff69b4.svg)](CODE_OF_CONDUCT.md)
[![Security](https://img.shields.io/badge/Security-Policy-green.svg)](SECURITY.md)
[![Contributing](https://img.shields.io/badge/Contributing-Guidelines-blue.svg)](CONTRIBUTING.md)

This repository contains cleaned and organized datasets from various Sri Lankan government public sources, compiled by the Lanka Data Foundation. The data spans from 2019 to 2025 and covers multiple ministries and departments.

All datasets are in clean JSON format with metadata.

To see a summary of all data available, see the [Data Matrix](docs/data_matrix.md).

## Features

| Feature | Description |
|---------|-------------|
| **Multi-Year Coverage** | 6 years of comprehensive data (2020-2025) |
| **Government-Wide Scope** | Data from 4 major ministries and multiple departments |
| **Clean & Structured** | All datasets in standardized JSON format with consistent schemas |
| **175+ Datasets** | Extensive collection covering tourism, immigration, employment, and foreign affairs |
| **Rich Metadata** | Each dataset includes optional metadata for context and provenance |
| **Interactive Browser** | Browse data online via GitHub Pages with built-in JSON viewer |
| **Bulk Downloads** | Year-wise ZIP files for easy batch downloading |

## Getting Started

### Browsing & Viewing Data

The easiest way to explore the datasets:

- **[Browse all data interactively →](docs/index.md)** - Navigate through the data hierarchy
- **[View online at GitHub Pages →](https://ldflk.github.io/datasets/docs/)** - Access the web interface

All datasets are available as JSON files in the `data/` directory, organized by year and ministry.

### Adding New Data

To add new datasets to this repository:

1. **Navigate to the appropriate year folder** in `data/statistics/[YEAR]/`
2. **Add your dataset** as a JSON file in the correct ministry/department structure
3. **Update the hierarchy file** (`data_hierarchy_[YEAR].yaml`) to include your new dataset
4. **Submit a pull request** - See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines

#### Data File Requirements
- **data.json**: Must contain valid JSON data
- **metadata.json**: Optional, should contain dataset metadata (description, source, etc.)
- Files must be placed in appropriately named folders with appropriate categories

### Ingesting Data into OpenGIN

If you want to ingest this data into your own OpenGIN database instance, see [Data Ingestion Guide](ingestion/README.md) for complete setup instructions, prerequisites, and usage examples.

## Contributing

Please see our [Contributing Guidelines](CONTRIBUTING.md).

## Code of Conduct

Please see our [Code of Conduct](CODE_OF_CONDUCT.md).

## Security

Please see our [Security Policy](SECURITY.md).

## License

See [LICENSE](LICENSE) file for details.
