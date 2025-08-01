# Licensing Analysis Repository
 
## Repository Structure

### Scripts
- `scripts/analysis/` - Analysis scripts for different types of cost analysis
- `scripts/data_collection/` - Data collection and template generation scripts
- `scripts/reporting/` - Report generation and presentation scripts
- `scripts/utilities/` - Utility and helper scripts

### Reports
- `reports/current/` - Current analysis reports and outputs
- `reports/archive/` - Archived reports by date
- `reports/templates/` - Report templates

### Data
- `data/raw/` - Raw data files
- `data/processed/` - Processed data files
- `data/cache/` - Cache files

### Outputs
- `outputs/charts/` - Generated charts and visualizations
- `outputs/csv/` - CSV export files
- `outputs/pdf/` - PDF reports

### Documentation
- `docs/guides/` - Documentation and guides
- `docs/summaries/` - Analysis summaries

## Quick Start

### Running Analysis
```bash
# Run employee growth analysis
python main_runner.py employee_growth

# Run monthly billing analysis
python main_runner.py monthly_billing

# Run Synoptek licensing analysis
python main_runner.py synoptek_licensing
```

### Available Analysis Types
- **employee_growth** - Employee growth impact analysis
- **monthly_billing** - Monthly billing pattern analysis
- **synoptek_licensing** - Synoptek licensing cost analysis
- **temporal** - Comprehensive temporal analysis
- **vendor** - Executive vendor analysis
- **comprehensive** - Comprehensive executive analysis

## Maintenance

### Cleanup
```bash
python cleanup.py
```

## Key Findings

### Employee Growth Analysis
- **Growth:** 120 -> 160 employees (33.3% increase)
- **Cost Impact:** $27,030 monthly savings vs expected costs
- **Scaling Services:** 12 services properly scaling with growth
- **Non-Scaling Services:** 171 services for optimization review

### Synoptek Analysis
- **Total Services:** 183 services analyzed
- **Monthly Cost:** $3,716,684
- **Cost Efficiency:** 25% below expected costs for scaling services
- **Recommendation:** Continue relationship, focus on non-scaling services

## Recent Reports

All current reports are available in `reports/current/` with the following structure:
- **Markdown Reports** - Human-readable analysis summaries
- **CSV Exports** - Detailed data for further analysis
- **Charts** - Visual representations of key findings
- **PDF Reports** - Executive-ready presentations

---
*Last Updated: 2025-07-28 14:49:05*
