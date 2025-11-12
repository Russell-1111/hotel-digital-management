## ADDED Requirements

### Requirement: Revenue Analytics by Room Type
The system SHALL provide time-bucketed revenue analytics aggregated by room type with configurable granularity (daily, weekly, monthly, quarterly).

#### Scenario: Aggregate revenue by room type for monthly bucket
- **WHEN** the user requests revenue analytics for date range 2024-01-01 to 2024-12-31 with monthly time bucket
- **THEN** the system queries reservations joined with rooms to get room_type
- **AND** groups data by month (YYYY-MM format) and room_type
- **AND** computes for each group: total revenue (sum of total_cost), reservation count, and average cost per reservation
- **AND** filters to reservations with status IN ('Checked-Out', 'Checked-In')
- **AND** returns structured data with columns: time_bucket, room_type, total_revenue, reservation_count, avg_cost_per_reservation

#### Scenario: Aggregate revenue for daily time bucket
- **WHEN** the user selects daily time bucket
- **THEN** the system groups data by date (YYYY-MM-DD format) extracted from start_date
- **AND** produces one row per date per room_type

#### Scenario: Aggregate revenue for weekly time bucket
- **WHEN** the user selects weekly time bucket
- **THEN** the system groups data by week start date (Sunday) computed using SQLite date functions
- **AND** produces one row per week per room_type

#### Scenario: Aggregate revenue for quarterly time bucket
- **WHEN** the user selects quarterly time bucket
- **THEN** the system groups data by quarter (YYYY-Q# format) computed from start_date
- **AND** produces one row per quarter per room_type

#### Scenario: Handle empty result set
- **WHEN** no reservations exist within the specified date range with eligible status
- **THEN** the system returns an empty result set
- **AND** displays a user-friendly message indicating no data available

### Requirement: Revenue Trend Visualization
The system SHALL generate line plot charts showing average cost per reservation trends over time by room type.

#### Scenario: Generate trend line plot
- **WHEN** the user requests a trend chart for aggregated revenue data
- **THEN** the system creates a matplotlib line plot with:
  - X-axis: Time buckets (chronologically ordered)
  - Y-axis: Average cost per reservation (MYR)
  - One line per room type (distinct colors)
  - Legend identifying each room type
  - Grid enabled for readability
  - Title indicating date range and time bucket

#### Scenario: Handle single room type
- **WHEN** only one room type exists in the data
- **THEN** the system generates a single line plot
- **AND** includes the room type in the legend

### Requirement: Revenue Bar Chart Visualization
The system SHALL generate grouped bar charts showing absolute revenue and reservation counts by room type over time.

#### Scenario: Generate grouped bar chart
- **WHEN** the user requests a bar chart for aggregated revenue data
- **THEN** the system creates a matplotlib bar chart with:
  - X-axis: Time buckets (chronologically ordered)
  - Y-axis (primary): Total revenue (MYR)
  - Grouped bars by room type (distinct colors)
  - Optional secondary Y-axis overlay showing reservation count as a line
  - Legend identifying each room type
  - Grid enabled for readability
  - Title indicating date range and time bucket

#### Scenario: Generate combined trend and bar chart view
- **WHEN** the user selects combined chart type
- **THEN** the system creates a matplotlib figure with two subplots:
  - Top subplot: Trend line plot (avg cost per reservation)
  - Bottom subplot: Grouped bar chart (total revenue)
  - Shared X-axis for alignment
  - Individual Y-axis labels and legends for each subplot

### Requirement: Chart Export as PNG
The system SHALL export generated charts as PNG files with timestamped filenames to the reports/ directory.

#### Scenario: Save chart as PNG with timestamped filename
- **WHEN** a chart is generated
- **THEN** the system saves the figure as PNG to reports/ directory
- **AND** uses filename format: revenue_by_room_type_{time_bucket}_{start_date}_{end_date}_{timestamp}.png
- **AND** timestamp is in format YYYYMMdd_HHmmss in hotel timezone
- **AND** displays the full file path to the user upon success

#### Scenario: Auto-create reports directory if missing
- **WHEN** the reports/ directory does not exist
- **THEN** the system creates the directory with appropriate permissions
- **AND** proceeds with file save

#### Scenario: Handle file save errors
- **WHEN** the system cannot write to reports/ directory (permissions, disk full)
- **THEN** the system displays an error dialog with specific failure reason
- **AND** does not crash or leave partial files

### Requirement: Data Export as CSV
The system SHALL export the underlying aggregated data as CSV files with timestamped filenames to the reports/ directory.

#### Scenario: Export aggregated data as CSV
- **WHEN** analytics data is generated
- **THEN** the system exports the data as CSV to reports/ directory
- **AND** uses filename format: revenue_by_room_type_{time_bucket}_{start_date}_{end_date}_{timestamp}.csv
- **AND** CSV includes headers: time_bucket, room_type, total_revenue, reservation_count, avg_cost_per_reservation
- **AND** numeric values are formatted with two decimal places for currency
- **AND** displays the full file path to the user upon success

#### Scenario: CSV matches chart data exactly
- **WHEN** both chart and CSV are exported in the same operation
- **THEN** the CSV contains exactly the data visualized in the chart
- **AND** row order matches the chronological order of time buckets

### Requirement: Analytics Unit Tests
The system SHALL include unit tests for SQL aggregation logic covering standard and edge cases.

#### Scenario: Test monthly aggregation with sample data
- **WHEN** unit test runs aggregate_revenue_by_room_type() with mock reservations
- **THEN** the test verifies correct grouping by month and room_type
- **AND** validates sum, count, and average calculations
- **AND** confirms filtering of cancelled reservations

#### Scenario: Test edge case with no data
- **WHEN** unit test queries an empty date range
- **THEN** the test verifies an empty result set is returned without errors

#### Scenario: Test edge case with single room type
- **WHEN** unit test queries data with only one room type
- **THEN** the test verifies correct aggregation for that single type

### Requirement: Visualization Functional Tests
The system SHALL include functional tests that generate sample charts using test data.

#### Scenario: Generate test chart and verify file creation
- **WHEN** functional test invokes chart generation with sample data
- **THEN** the test verifies PNG file is created in reports/ directory
- **AND** file size is non-zero
- **AND** filename matches expected pattern

#### Scenario: Verify CSV export format and content
- **WHEN** functional test exports sample data as CSV
- **THEN** the test reads the CSV file and validates:
  - Headers are present and correct
  - Row count matches input data
  - Numeric values are formatted correctly
  - No missing or malformed data
