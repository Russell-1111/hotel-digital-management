# Add Revenue Analytics by Room Type

## Why
Hotel staff currently lack visibility into revenue trends and performance patterns by room type. They cannot easily identify which room types generate the most revenue, track booking patterns over time, or make data-driven pricing decisions. This feature addresses the need for time-based revenue analytics with configurable granularity (daily/weekly/monthly/quarterly) and visual trend analysis.

## What Changes
- Add SQL aggregation functions to compute revenue by room type over configurable time periods
- Implement visualization module using matplotlib to generate line plots (trends) and bar charts (absolute values)
- Add "Analytics → Revenue by Room Type" menu item in the UI with modal dialog for time range and bucket selection
- Export generated charts as timestamped PNG files to `reports/` directory
- Export underlying data as timestamped CSV files for external analysis
- Add unit tests for SQL aggregation logic and functional tests for chart generation with sample data
- Update `requirements.txt` to include matplotlib and pandas dependencies

## Impact
- Affected specs: `reporting`, `ui`
- Affected code:
  - New file: `app/analytics.py` (SQL aggregation and data preparation)
  - New file: `app/visualization.py` (chart generation using matplotlib)
  - Modified: `app/ui/main.py` (add Analytics menu and dialog)
  - New file: `tests/test_analytics.py` (unit tests for aggregation)
  - New file: `tests/test_visualization.py` (functional tests for chart generation)
  - Modified: `requirements.txt` (add matplotlib, pandas)
- New directory: `reports/` (auto-created for chart/CSV exports)
