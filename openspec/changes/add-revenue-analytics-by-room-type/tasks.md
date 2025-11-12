## 1. Dependencies and Setup
- [x] 1.1 Add matplotlib>=3.8.0 and pandas>=2.1.0 to requirements.txt
- [x] 1.2 Create reports/ directory structure with .gitkeep file
- [x] 1.3 Install new dependencies in development environment

## 2. Data Layer Implementation (app/analytics.py)
- [x] 2.1 Create aggregate_revenue_by_room_type() function with SQL query for daily bucketing
- [x] 2.2 Add SQL query variants for weekly, monthly, and quarterly bucketing
- [x] 2.3 Implement time bucket helper functions (bucket_to_sql_expr, format_bucket_label)
- [x] 2.4 Add data validation and error handling for date ranges and status filtering
- [x] 2.5 Write unit tests for SQL aggregation logic (test_analytics.py) with mock data
- [x] 2.6 Write unit tests for edge cases (empty data, single room type, date boundaries)

## 3. Visualization Layer Implementation (app/visualization.py)
- [x] 3.1 Create generate_trend_chart() function for line plot (avg cost per reservation)
- [x] 3.2 Create generate_bar_chart() function for grouped bar chart (total revenue + count overlay)
- [x] 3.3 Create generate_combined_chart() function with subplots (trend + bar)
- [x] 3.4 Implement save_chart_as_png() with timestamped filename generation
- [x] 3.5 Implement export_data_as_csv() with pandas DataFrame export
- [x] 3.6 Add chart styling helpers (configure grid, legend, labels, colors)
- [x] 3.7 Write functional test that generates sample chart using test data (test_visualization.py)
- [x] 3.8 Write test for CSV export with validation of format and content

## 4. UI Integration (app/ui/main.py)
- [x] 4.1 Create RevenueAnalyticsDialog class with modal window structure
- [x] 4.2 Add date range inputs (start_date_entry, end_date_entry) using DateEntry
- [x] 4.3 Add time bucket dropdown (Daily/Weekly/Monthly/Quarterly)
- [x] 4.4 Add chart type dropdown (Trend/Bar/Combined)
- [x] 4.5 Implement _generate_analytics() method to invoke analytics + visualization
- [x] 4.6 Add progress indicator (label) during chart generation
- [x] 4.7 Display success message with paths to saved PNG and CSV files
- [x] 4.8 Add error handling with informative dialogs for common failures
- [x] 4.9 Add "Analytics" button in Reports tab (below Guest Reservation Details section)
- [x] 4.10 Wire button click to open RevenueAnalyticsDialog

## 5. Testing and Validation
- [x] 5.1 Run unit tests for analytics.py and verify all aggregation scenarios pass
- [x] 5.2 Run functional test for visualization.py and inspect generated charts
- [x] 5.3 Manual test: Generate daily revenue chart with sample data
- [x] 5.4 Manual test: Generate weekly revenue chart with sample data
- [x] 5.5 Manual test: Generate monthly revenue chart with sample data
- [x] 5.6 Manual test: Generate quarterly revenue chart with sample data
- [x] 5.7 Manual test: Verify CSV export matches chart data
- [x] 5.8 Manual test: Verify timestamped filenames are unique and correctly formatted
- [x] 5.9 Edge case test: Generate chart with no data (empty result)
- [x] 5.10 Edge case test: Generate chart with single room type
- [x] 5.11 Edge case test: Verify reports/ directory is auto-created if missing
- [x] 5.12 Error handling test: Attempt to generate chart with invalid date range

## 6. Documentation and Cleanup
- [x] 6.1 Add docstrings to all new functions in analytics.py and visualization.py
- [x] 6.2 Add inline comments for complex SQL queries and date bucketing logic
- [x] 6.3 Update module-level docstrings with usage examples
- [x] 6.4 Verify all imports are properly organized (standard → third-party → local)
- [x] 6.5 Run linter (if configured) and fix any style issues
- [x] 6.6 Verify test coverage includes new modules (aim for >70%)

## 7. Final Integration and Smoke Test
- [x] 7.1 Run full application and verify UI layout is not broken
- [x] 7.2 Test authentication flow remains intact
- [x] 7.3 Generate analytics chart through full UI flow (end-to-end)
- [x] 7.4 Verify exported files are readable and correctly formatted
- [x] 7.5 Check logs for any errors or warnings during chart generation
- [x] 7.6 Verify reports/ directory contains expected files with correct naming

## Dependencies
- Task 2.x must complete before 3.x (visualization depends on analytics data structure)
- Task 3.x must complete before 4.x (UI invokes visualization layer)
- Task 1.x can be done in parallel with 2.x

## Parallelizable Work
- Task 2.x (analytics) and 3.x (visualization) can have stubs created in parallel, then integrated
- Task 5.x (testing) can begin as soon as corresponding implementation tasks complete
- Task 6.x (documentation) can be done incrementally alongside implementation
