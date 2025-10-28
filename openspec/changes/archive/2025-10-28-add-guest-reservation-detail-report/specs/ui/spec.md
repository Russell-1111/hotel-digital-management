# ui Spec Delta

## ADDED Requirements

### Requirement: Guest Reservation Detail Report Display
The Reports tab SHALL provide a section to generate and display detailed guest reservation reports with filtering by date range.

#### Scenario: Display report input controls
- **WHEN** the user navigates to the Reports tab
- **THEN** the system displays input fields for start date and end date (format YYYY-MM-DD)
- **AND** provides a "Generate Report" button to trigger report generation
- **AND** defaults the date range to the first and last day of the current month

#### Scenario: Display report results in table
- **WHEN** the user clicks "Generate Report" with valid dates
- **THEN** the system displays a table with columns: Guest Name, Room ID, Check-In Date, Check-Out Date, Nights, Total Cost (MYR)
- **AND** each row represents one reservation within the date range
- **AND** the table is sorted by check-in date ascending

#### Scenario: Display grand total
- **WHEN** the guest reservation detail report is displayed
- **THEN** the system shows a summary row or label displaying the grand total of all reservation costs in MYR with two decimals
- **AND** the grand total updates whenever the report is regenerated

#### Scenario: Handle empty results
- **WHEN** no reservations match the selected date range
- **THEN** the system displays an empty table and shows "MYR 0.00" as the grand total
- **AND** optionally displays a message "No reservations found for this period"
