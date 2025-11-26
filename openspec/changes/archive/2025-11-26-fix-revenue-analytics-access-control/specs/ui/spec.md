## ADDED Requirements

### Requirement: Admin-Only Analytics UI Section
The Analytics section in the Reports tab SHALL be visible and accessible only to users with the 'admin' role.

- The analytics_section frame and all its child widgets SHALL be conditionally created based on user role
- Non-admin users SHALL NOT see the Analytics section in the Reports tab
- The conditional rendering SHALL occur in the _build_reports() method during UI initialization
- The section SHALL be completely omitted from the UI tree for non-admin users (not just hidden or disabled)

#### Scenario: Hide Analytics section for staff users
- **WHEN** a user with role 'staff' navigates to the Reports tab during application initialization
- **THEN** the system SHALL skip creation of the analytics_section LabelFrame
- **AND** the "Revenue by Room Type" button SHALL NOT be created
- **AND** the analytics description label SHALL NOT be created
- **AND** no Analytics section SHALL appear in the report_frame

#### Scenario: Display Analytics section for admin users
- **WHEN** a user with role 'admin' navigates to the Reports tab during application initialization
- **THEN** the system SHALL create the analytics_section LabelFrame with text="Analytics" and padding=8
- **AND** create the analytics description label with explanatory text
- **AND** create the "Revenue by Room Type" button with command=_show_revenue_analytics
- **AND** pack the analytics_section into report_frame with fill=tk.X, padx=8, pady=8

#### Scenario: Analytics button callback includes authorization guard
- **WHEN** the _show_revenue_analytics callback method is invoked
- **THEN** the method SHALL call self._require_admin("Access Revenue Analytics") as the first statement
- **AND** if authorization fails (returns False), return immediately without opening the dialog
- **AND** if authorization succeeds (returns True), proceed to open RevenueAnalyticsDialog

## MODIFIED Requirements

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

#### Scenario: Analytics section follows role-based rendering
- **WHEN** the Reports tab is built
- **THEN** the Analytics section SHALL only be created if current_user['role'] == 'admin'
- **AND** staff users SHALL see only the Monthly Revenue Summary and Guest Reservation Detail sections
- **AND** admin users SHALL see all three sections including Analytics
