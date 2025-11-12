# Design: Revenue Analytics by Room Type

## Context
The hotel management system currently provides basic monthly revenue summaries and guest reservation details, but lacks analytical capabilities for understanding revenue patterns by room type over time. Staff need to make informed decisions about pricing and inventory management based on historical performance trends.

The system uses SQLite for storage with a `reservations` table that includes `room_id`, `total_cost`, `start_date`, `end_date`, and `status`. Room types are stored in a separate `rooms` table with `room_id`, `room_type`, and `base_price`.

## Goals / Non-Goals

**Goals:**
- Provide configurable time-bucketed aggregation (daily/weekly/monthly/quarterly) of revenue by room type
- Visualize revenue trends (line plot) and absolute values (bar chart) for each room type
- Enable export of both charts (PNG) and raw data (CSV) with timestamped filenames
- Ensure performance is acceptable for ~20 rooms and typical 1-2 years of reservation history
- Maintain simplicity: use standard matplotlib/pandas rather than complex BI frameworks

**Non-Goals:**
- Real-time dashboard or auto-refresh capabilities
- Multi-property or comparative analytics across different hotels
- Predictive analytics or forecasting
- Web-based or mobile analytics interface
- Advanced statistical analysis (correlation, regression, etc.)

## Decisions

### Architecture: Layered Approach
- **Data Layer** (`app/analytics.py`): SQL aggregation and data preparation
  - Query reservations joined with rooms to get room_type
  - Group by time bucket and room_type
  - Compute metrics: total revenue, reservation count, average cost per reservation
  - Return structured data (list of dicts or pandas DataFrame)
  
- **Visualization Layer** (`app/visualization.py`): Chart generation
  - Accept prepared data from analytics layer
  - Generate matplotlib figures with:
    - Line plot: X=time bucket, Y=average cost per reservation, one line per room type
    - Bar chart: X=time bucket, Y=total revenue (grouped by room type) + reservation count overlay
    - Optional combined view (subplots)
  - Save figures as PNG to `reports/` directory
  
- **UI Layer** (`app/ui/main.py`): User interaction
  - Add "Analytics" menu item (or extend Reports tab with Analytics button)
  - Modal dialog with inputs:
    - Start date (DateEntry)
    - End date (DateEntry)
    - Time bucket (dropdown: Daily/Weekly/Monthly/Quarterly)
    - Chart type (dropdown: Trend/Bar/Combined)
  - Invoke analytics + visualization on "Generate" button
  - Display success message with paths to saved files
  - Handle errors gracefully with informative messages

**Alternative considered:** Embedding charts in Tkinter UI using matplotlib backend
- **Rejected because:** Adds complexity for limited benefit; PNG export is simpler and allows external sharing/printing

### Data Aggregation Strategy
Use SQLite date functions for bucketing:
- **Daily:** `DATE(start_date)` (simple date extraction)
- **Weekly:** `DATE(start_date, 'weekday 0', '-6 days')` (start of week)
- **Monthly:** `SUBSTR(start_date, 1, 7)` (YYYY-MM format)
- **Quarterly:** `SUBSTR(start_date, 1, 4) || '-Q' || ((CAST(SUBSTR(start_date, 6, 2) AS INTEGER) - 1) / 3 + 1)` (YYYY-Q# format)

Query structure (example for monthly):
```sql
SELECT
    SUBSTR(r.start_date, 1, 7) AS time_bucket,
    rm.room_type,
    SUM(r.total_cost) AS total_revenue,
    COUNT(*) AS reservation_count,
    AVG(r.total_cost) AS avg_cost_per_reservation
FROM reservations r
JOIN rooms rm ON r.room_id = rm.room_id
WHERE r.start_date >= ? AND r.start_date <= ?
  AND r.status IN ('Checked-Out', 'Checked-In')
GROUP BY time_bucket, rm.room_type
ORDER BY time_bucket, rm.room_type
```

**Alternative considered:** Using pandas for aggregation after loading raw data
- **Rejected because:** Less performant for large datasets; SQLite aggregation is faster and reduces memory usage

### Visualization Design
**Chart Layout:**
- **Line Plot (Trend):**
  - X-axis: Time buckets (chronological)
  - Y-axis: Average cost per reservation (MYR)
  - One line per room type (distinct colors)
  - Legend showing room types
  - Grid for readability
  
- **Bar Chart (Absolute Revenue):**
  - X-axis: Time buckets
  - Y-axis (primary): Total revenue (MYR)
  - Grouped bars by room type
  - Y-axis (secondary): Reservation count (optional overlay as line)
  
- **Combined View:**
  - Subplot 1: Line plot (top half)
  - Subplot 2: Bar chart (bottom half)
  - Shared X-axis for alignment

**Style:**
- Use matplotlib's default style with minor customizations (grid, larger fonts for readability)
- Figure size: 12x8 inches (landscape orientation for better readability)
- DPI: 100 (sufficient for screen viewing and printing)

**Alternative considered:** Using seaborn for styling
- **Rejected because:** Adds another dependency; matplotlib is sufficient for basic charts

### File Export Strategy
**Naming Convention:**
- PNG: `revenue_by_room_type_{time_bucket}_{start_date}_{end_date}_{timestamp}.png`
  - Example: `revenue_by_room_type_monthly_2024-01_2024-12_20251112_143052.png`
- CSV: `revenue_by_room_type_{time_bucket}_{start_date}_{end_date}_{timestamp}.csv`
  
**Directory:**
- Create `reports/` directory at project root if it doesn't exist
- Check write permissions and show error dialog if unavailable

**CSV Format:**
```csv
time_bucket,room_type,total_revenue,reservation_count,avg_cost_per_reservation
2024-01,Deluxe,12500.00,10,1250.00
2024-01,Standard,8400.00,15,560.00
...
```

**Alternative considered:** Using Excel format (.xlsx)
- **Rejected because:** Requires additional dependency (openpyxl); CSV is simpler and universally compatible

### Dependencies
Add to `requirements.txt`:
```
matplotlib>=3.8.0
pandas>=2.1.0
```

**Why pandas?**
- Simplifies data preparation and transformation (pivot, groupby)
- Provides convenient CSV export with headers
- Well-suited for tabular data manipulation

**Alternative considered:** NumPy only (without pandas)
- **Rejected because:** More manual data wrangling; pandas provides higher-level abstractions for tabular data

## Risks / Trade-offs

### Risk: Performance degradation with large datasets
- **Likelihood:** Low (hotel has ~20 rooms, typical dataset < 10,000 reservations)
- **Impact:** Medium (slow chart generation could frustrate users)
- **Mitigation:** Use SQLite aggregation rather than Python loops; add index on `(start_date, room_id)` if needed; document performance expectations (< 5 seconds for 1-2 years of data)

### Risk: Date bucketing edge cases (timezone, week boundaries)
- **Likelihood:** Medium (different timezones or week-start conventions)
- **Impact:** Low (minor discrepancies in weekly aggregation)
- **Mitigation:** Use hotel timezone consistently (from config); document week-start as Sunday; validate edge cases in tests

### Trade-off: Simplicity vs. advanced features
- **Decision:** Favor simplicity
- **Rationale:** This is a single-property boutique hotel system; advanced features (drill-down, interactive charts, forecasting) would add complexity without clear ROI for current use case
- **Future consideration:** Can extend if user feedback indicates need for more sophisticated analytics

### Trade-off: Embedded charts vs. file export
- **Decision:** File export only (PNG + CSV)
- **Rationale:** Simpler implementation; allows sharing/printing; avoids Tkinter canvas complexity
- **Future consideration:** Could add embedded preview if users find file export cumbersome

## Migration Plan
No migration required - this is a new additive feature. Existing database schema and data remain unchanged.

**Rollback:**
- Remove new files (`app/analytics.py`, `app/visualization.py`, `tests/test_analytics.py`, `tests/test_visualization.py`)
- Revert changes to `app/ui/main.py` and `requirements.txt`
- Delete `reports/` directory (optional - contains only generated outputs)

## Open Questions
1. **Should we add filtering by reservation status?** (e.g., exclude cancelled reservations)
   - **Proposed answer:** Yes, filter to `status IN ('Checked-Out', 'Checked-In')` to reflect actual realized revenue
   
2. **Should we support custom date formats or localization?**
   - **Proposed answer:** No, keep ISO format (YYYY-MM-DD) for consistency with rest of system; can add later if needed
   
3. **Should we allow selecting specific room types to analyze (rather than all)?**
   - **Proposed answer:** Not in initial version; analyze all room types and let users filter in exported CSV if needed; can add checkbox selection in future iteration
   
4. **Should we add a "preview" button to display chart in dialog before saving?**
   - **Proposed answer:** Not in initial version; direct save keeps implementation simpler; can add if user feedback indicates strong need
