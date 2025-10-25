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
