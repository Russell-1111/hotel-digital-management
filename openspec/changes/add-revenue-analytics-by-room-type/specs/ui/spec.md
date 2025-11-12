## ADDED Requirements

### Requirement: Revenue Analytics UI Integration
The system SHALL provide a user interface for accessing revenue analytics through the Reports tab.

#### Scenario: Display Analytics button in Reports tab
- **WHEN** the user navigates to the Reports tab
- **THEN** the system displays an "Analytics" button below the Guest Reservation Details section
- **AND** the button is clearly labeled "Revenue by Room Type"

#### Scenario: Open Revenue Analytics Dialog
- **WHEN** the user clicks the "Revenue by Room Type" button
- **THEN** the system opens a modal dialog titled "Revenue Analytics by Room Type"
- **AND** the dialog contains input controls for date range, time bucket, and chart type
- **AND** the dialog is centered on the parent window
- **AND** the dialog prevents interaction with the main window until closed

### Requirement: Revenue Analytics Dialog Controls
The system SHALL provide interactive controls in the Revenue Analytics Dialog for configuring analysis parameters.

#### Scenario: Display date range inputs
- **WHEN** the Revenue Analytics Dialog opens
- **THEN** the dialog displays:
  - "Start Date" label with DateEntry widget (YYYY-MM-DD format)
  - "End Date" label with DateEntry widget (YYYY-MM-DD format)
  - Default start date set to first day of current month in hotel timezone
  - Default end date set to last day of current month in hotel timezone

#### Scenario: Validate date range
- **WHEN** the user selects start date after end date
- **THEN** the system displays an error message "Start date must be before end date"
- **AND** prevents chart generation until corrected

#### Scenario: Display time bucket selector
- **WHEN** the Revenue Analytics Dialog opens
- **THEN** the dialog displays a dropdown labeled "Time Bucket" with options:
  - Daily
  - Weekly
  - Monthly
  - Quarterly
- **AND** default selection is "Monthly"

#### Scenario: Display chart type selector
- **WHEN** the Revenue Analytics Dialog opens
- **THEN** the dialog displays a dropdown labeled "Chart Type" with options:
  - Trend (Line Plot)
  - Bar Chart (Revenue)
  - Combined (Trend + Bar)
- **AND** default selection is "Combined"

### Requirement: Analytics Generation and Feedback
The system SHALL provide visual feedback during analytics generation and display results or errors clearly.

#### Scenario: Display progress indicator during generation
- **WHEN** the user clicks "Generate" button
- **THEN** the system disables the Generate button
- **AND** displays a status label "Generating analytics..."
- **AND** processes the request in the foreground (blocking UI temporarily)

#### Scenario: Display success message with file paths
- **WHEN** chart and CSV generation complete successfully
- **THEN** the system displays a success message dialog with:
  - Message: "Analytics generated successfully!"
  - PNG file path: reports/revenue_by_room_type_...png
  - CSV file path: reports/revenue_by_room_type_...csv
- **AND** re-enables the Generate button
- **AND** clears the progress indicator

#### Scenario: Handle empty data gracefully
- **WHEN** analytics query returns no data for the selected date range
- **THEN** the system displays an informational dialog:
  - Message: "No reservation data found for the selected date range and filters."
  - Suggestion: "Try adjusting the date range or check that reservations exist with status Checked-In or Checked-Out."
- **AND** does not create PNG or CSV files
- **AND** re-enables the Generate button

#### Scenario: Handle analytics errors
- **WHEN** an error occurs during analytics generation (database error, file write error)
- **THEN** the system displays an error dialog with:
  - Title: "Analytics Error"
  - Message: Specific error description (e.g., "Unable to write to reports/ directory. Check permissions.")
  - Log reference: "Check logs/app.log for details."
- **AND** logs the full error with stack trace
- **AND** re-enables the Generate button

### Requirement: Analytics Dialog Layout and UX
The system SHALL follow consistent layout and UX patterns aligned with existing Reports tab design.

#### Scenario: Dialog layout and styling
- **WHEN** the Revenue Analytics Dialog is displayed
- **THEN** the dialog uses:
  - Consistent padding (8px) around sections
  - LabelFrame for grouping related inputs
  - ttk widgets matching the app's theme
  - Minimum width of 500px for readability
  - Resizable to false (fixed dimensions for simplicity)

#### Scenario: Cancel button closes dialog
- **WHEN** the user clicks "Cancel" button
- **THEN** the dialog closes without generating analytics
- **AND** no files are created

#### Scenario: Close dialog button (X) behavior
- **WHEN** the user clicks the window close button (X)
- **THEN** the dialog closes without generating analytics
- **AND** behaves identically to the Cancel button
