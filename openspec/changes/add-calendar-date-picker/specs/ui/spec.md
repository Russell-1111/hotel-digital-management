## ADDED Requirements

### Requirement: Calendar Date Picker Widget
The system SHALL provide calendar date picker widgets for all date input fields, allowing users to select dates visually while maintaining manual keyboard entry capability.

- Date input fields SHALL use a calendar widget (tkcalendar.DateEntry) that displays both a text entry and a clickable calendar icon
- Users SHALL be able to either type dates manually in YYYY-MM-DD format or click the calendar icon to select visually
- Calendar widget SHALL open a dropdown calendar when the calendar icon is clicked
- Calendar widget SHALL default to showing the current month or the current value of the field
- Manual typing SHALL still work exactly as before with full validation
- All date formats SHALL remain YYYY-MM-DD throughout the system

#### Scenario: Select date using calendar picker
- **WHEN** a user clicks the calendar icon on any date input field
- **THEN** a visual calendar dropdown appears showing the current month
- **AND** the user can navigate months and select a date
- **AND** the selected date is populated in YYYY-MM-DD format
- **AND** the calendar closes automatically after selection

#### Scenario: Type date manually
- **WHEN** a user clicks directly in the date text entry field
- **THEN** they can type a date manually in YYYY-MM-DD format
- **AND** existing validation rules apply (red text for invalid dates)
- **AND** the calendar widget accepts the manually typed date

#### Scenario: Calendar widget styling
- **WHEN** the application starts and displays date input fields
- **THEN** calendar widgets SHALL have consistent styling matching the ttk theme
- **AND** calendar icon SHALL be clearly visible and clickable
- **AND** widget width and padding SHALL match other ttk.Entry widgets (consistent 8px spacing)

## MODIFIED Requirements

### Requirement: Feedback and Errors
The system SHALL provide user feedback for operations and surface errors via dialogs with log references.

- Invalid input (e.g., malformed dates) shall show inline visual cues: red text color with brief (2-second) display before reverting.
- Calendar date picker widgets SHALL maintain visual feedback for invalid manually-typed dates
- On unexpected errors or validation failures, display an error dialog with:
  - Concise error message
  - Absolute filesystem path to the log file (e.g., `logs/app.log`)
  - Example: `"Failed to create reservation: Room unavailable.\n\nCheck C:\...\logs\app.log for details."`
- Long-running or refresh operations should provide visual indication (status messages or transient feedback).
- Errors shall be logged with context (module, timestamp, stack trace) to the application log file.

#### Scenario: Error dialog with log hint
- **WHEN** an unexpected exception occurs during a UI action (e.g., reservation creation fails)
- **THEN** an error dialog appears with a user-friendly message
- **AND** it includes the absolute path to `logs/app.log` for detailed troubleshooting
- **AND** the error is logged with full context

#### Scenario: Invalid date validation with calendar picker
- **WHEN** a user manually types an invalid date in a calendar date picker field
- **THEN** the field displays red text color as visual feedback
- **AND** the red color reverts to black after 2 seconds
- **AND** the calendar picker functionality remains available
