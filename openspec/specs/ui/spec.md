# ui Specification

## Purpose
Defines the user interface standards and conventions for the Hotel Digital Management System desktop application. These requirements ensure consistent visual design, accessible interactions, clear user feedback, and responsive layouts across all Tkinter screens.
## Requirements
### Requirement: Theming and Styles
The system SHALL use ttk-based theming with consistent widget styles and accessible defaults.

- Fonts shall be legible with a minimum default size of 10pt (Segoe UI on Windows or equivalent sans-serif).
- ttk theme shall be set to Vista (Windows), Clam, or similar modern theme based on platform availability.
- Widget styles shall be applied consistently: TLabel, TButton (4px padding), TEntry (4px padding), TLabelFrame (bold labels).
- List widgets (Listbox) shall use readable fonts (e.g., Segoe UI 9pt).
- Optional: Support for light/dark theme variants without breaking default appearance.

#### Scenario: Apply base theme and styles
- **WHEN** the application starts
- **THEN** a ttk theme is selected and applied (Vista, Clam, or fallback)
- **AND** base font is set to Segoe UI 10pt or equivalent
- **AND** all ttk widgets reflect consistent styling across tabs

### Requirement: Layout and Spacing
The system SHALL standardize layout using consistent spacing and geometry management.

- Use an 8px spacing unit for padding and margins between controls within a logical group.
- Frame containers shall specify padding (e.g., `ttk.Frame(padding=8)`).
- Grid layouts shall use padx/pady consistently (e.g., `grid(padx=8, pady=4)`).
- Define a minimum window size of 800×500 pixels; allow resizing up to larger dimensions.
- Key widgets (Listbox, Notebook content areas) shall expand with the window using `fill=tk.BOTH, expand=True`.
- Notebook (tabs) shall have 8px outer padding.

#### Scenario: Resizable layout with consistent padding
- **WHEN** the user resizes the main window
- **THEN** list and content areas expand while maintaining consistent 8px padding
- **AND** minimum size constraint prevents the window from becoming unusably small

### Requirement: Feedback and Errors
The system SHALL provide user feedback for operations and surface errors via dialogs with log references.

- Invalid input (e.g., malformed dates) shall show inline visual cues: red text color with brief (2-second) display before reverting.
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

### Requirement: Responsiveness
The system SHALL keep the UI responsive with a resizable window and expanding widgets.

- Do not block the main thread for trivial operations; provide visual indication if an action takes noticeable time (>1 second).
- Key content regions (lists, forms, result areas) must expand and remain usable at larger window sizes.
- Window sizing: default 900×600, minimum 800×500, resizable to larger dimensions.
- Widgets use appropriate layout managers (pack, grid) with fill/expand options to adapt to available space.

#### Scenario: Visible progress during refresh
- **WHEN** the user triggers a refresh or compute action that takes noticeable time
- **THEN** the UI shows busy/working feedback (e.g., status message, cursor change)
- **AND** the interface remains responsive or clearly indicates processing status

### Requirement: Room Image Display in Dropdown
The system SHALL display thumbnail images of rooms in the room selection dropdown on the Reservations tab.

#### Scenario: Display room thumbnails in dropdown
- **WHEN** the room selection dropdown is populated with available rooms
- **THEN** each dropdown item SHALL include a thumbnail image (80x60 pixels) of the room
- **AND** the thumbnail SHALL appear alongside the room text (number, type, price)
- **AND** rooms without images SHALL display a placeholder thumbnail

#### Scenario: Update thumbnails when availability changes
- **WHEN** the user clicks "Check Availability" to refresh the room list
- **THEN** the dropdown SHALL reload and display updated room thumbnails
- **AND** image loading SHALL not block the UI thread
- **AND** previously loaded images SHALL be reused if available in cache

### Requirement: Room Image Display in Availability List
The system SHALL display larger preview images of rooms in the Availability tab listing.

#### Scenario: Display room preview images in availability list
- **WHEN** the Availability tab shows the list of rooms and their status
- **THEN** each room entry SHALL include a preview image (320x240 pixels)
- **AND** the preview image SHALL appear aligned with the room status text
- **AND** rooms without images SHALL display a larger placeholder image

#### Scenario: Handle image loading errors gracefully
- **WHEN** a room image fails to load due to file system errors
- **THEN** the UI SHALL display the placeholder image instead
- **AND** the room selection/display SHALL remain functional
- **AND** a warning SHALL be logged but no error dialog shown to the user

### Requirement: Image Memory Management
The system SHALL manage loaded room images efficiently to prevent memory leaks.

#### Scenario: Cache room images to prevent garbage collection
- **WHEN** room images are loaded for display in Tkinter widgets
- **THEN** PhotoImage objects SHALL be stored in a persistent cache
- **AND** the cache SHALL prevent images from being garbage collected while in use
- **AND** the cache SHALL be cleared and refreshed when room data is reloaded

#### Scenario: Reuse cached images on refresh
- **WHEN** the user triggers a refresh of room lists or availability
- **THEN** already-loaded room images SHALL be reused from cache
- **AND** only new or changed images SHALL be loaded from disk
- **AND** unnecessary image reloading SHALL be avoided to improve performance

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

### Requirement: Reservation List Display Format
The system SHALL display reservation lists without showing internal reservation IDs to users.

- Reservation lists on the Reservations tab SHALL display: Room number, guest name, check-in/out dates, status, and total cost
- Format SHALL be: `"Room {room_id} | {guest_name} | {check_in_date}->{check_out_date} | {status} | MYR {total_cost}"`
- Reservation ID SHALL NOT be visible in the list display (remains internal for backend operations)
- List items SHALL use pipe (|) separators for visual clarity between fields
- Each field SHALL be separated by ` | ` (space-pipe-space) for consistent spacing

#### Scenario: Display reservation in list without ID
- **WHEN** the Reservations tab loads and populates the existing reservations list
- **THEN** each list item displays: `"Room {room_id} | {guest_name} | {check_in}->{check_out} | {status} | MYR {cost}"`
- **AND** the reservation ID is not visible to the user
- **AND** pipe separators clearly delimit each field

#### Scenario: Select and modify reservation without visible ID
- **WHEN** a user selects a reservation from the list and clicks "Modify Selected"
- **THEN** the system correctly identifies the reservation using internal ID mapping
- **AND** opens the modification dialog with pre-filled reservation details
- **AND** the user never sees or needs to know the reservation ID

#### Scenario: Select and cancel reservation without visible ID
- **WHEN** a user selects a reservation from the list and clicks "Cancel Selected"
- **THEN** the system correctly identifies the reservation using internal ID mapping
- **AND** cancels the correct reservation
- **AND** the user never sees or needs to know the reservation ID

### Requirement: Daily Operations List Display Format
The system SHALL display daily check-in and check-out lists without showing internal reservation IDs.

- Daily check-ins list SHALL display: Room number and guest name
- Daily check-outs list SHALL display: Room number and guest name
- Format SHALL be: `"Room {room_id} | {guest_name}"`
- Reservation ID SHALL NOT be visible in daily operations lists
- Simplified format appropriate for quick reference during daily operations

#### Scenario: Display check-ins without ID
- **WHEN** the Daily Ops tab loads and populates today's check-ins
- **THEN** each list item displays: `"Room {room_id} | {guest_name}"`
- **AND** the reservation ID is not visible
- **AND** the list is clean and easy to scan

#### Scenario: Display check-outs without ID
- **WHEN** the Daily Ops tab loads and populates today's check-outs
- **THEN** each list item displays: `"Room {room_id} | {guest_name}"`
- **AND** the reservation ID is not visible
- **AND** the list is clean and easy to scan

## Design Notes

### Theme Setup
Implemented in `app/ui/main.py` via `_setup_theme()` method:
- Selects best available theme (Vista > Clam > default)
- Configures base fonts and widget styles
- Sets option database for fallback widgets

### Error Handling Helper
Implemented as `_show_error(title, message)` method in the main App class:
- Constructs full error message with log path
- Logs error details to `logs/app.log`
- Displays tkinter messagebox with error information

### Layout Patterns
- **Daily Ops Tab**: pack-based with 8px padding frames
- **Reservations Tab**: grid layout for form fields with consistent column spacing
- **Availability Tab**: pack + grid hybrid with 8px padding
- **Reports Tab**: pack with centered results display

### Validation Feedback
Date entry widgets provide instant visual feedback by temporarily changing foreground color to red on validation failure, then auto-reverting after 2 seconds.
