## ADDED Requirements

### Requirement: Role-Based Access Control for UI Features
The system SHALL enforce role-based access control at the UI presentation layer by conditionally rendering features based on user roles.

- UI controls for admin-only features SHALL NOT be created or displayed for non-admin users
- Role checks SHALL occur during UI initialization before widget creation
- Hidden features SHALL be completely removed from the UI tree (not just disabled or hidden)
- Role-based UI rendering SHALL apply consistently across all tabs and dialogs

#### Scenario: Hide analytics UI section for staff users
- **WHEN** a user with role 'staff' navigates to the Reports tab
- **THEN** the "Analytics" section frame and its children SHALL NOT be created
- **AND** the "Revenue by Room Type" button SHALL NOT be visible or accessible
- **AND** the section SHALL NOT occupy any space in the UI layout

#### Scenario: Show analytics UI section for admin users
- **WHEN** a user with role 'admin' navigates to the Reports tab
- **THEN** the "Analytics" section frame SHALL be created and displayed
- **AND** the "Revenue by Room Type" button SHALL be visible and clickable
- **AND** clicking the button SHALL open the revenue analytics dialog

### Requirement: Callback Authorization Guards
The system SHALL implement fail-safe authorization checks in callback methods for sensitive operations.

- Callback methods for admin-only features SHALL verify user role at method entry
- Authorization failures SHALL display an error dialog and log the unauthorized access attempt
- Callbacks SHALL return immediately without executing protected logic when authorization fails
- Authorization guards SHALL be present even when UI controls are hidden by role-based rendering

#### Scenario: Block staff access to revenue analytics callback
- **WHEN** a user with role 'staff' somehow invokes the _show_revenue_analytics callback
- **THEN** the system SHALL call _require_admin("Access Revenue Analytics")
- **AND** display an error dialog: "This action requires administrator privileges"
- **AND** log a warning message with username and action name
- **AND** return immediately without opening the revenue analytics dialog

#### Scenario: Allow admin access to revenue analytics callback
- **WHEN** a user with role 'admin' invokes the _show_revenue_analytics callback
- **THEN** the authorization check SHALL pass
- **AND** the revenue analytics dialog SHALL open normally
- **AND** no error dialog or warning log SHALL be generated

### Requirement: Authorization Testing
The system SHALL include unit tests that verify role-based access control at both UI and callback levels.

#### Scenario: Test analytics section not created for staff
- **WHEN** unit test initializes main UI with a staff user
- **THEN** test SHALL verify analytics_section frame does not exist in UI tree
- **AND** "Revenue by Room Type" button widget is not created
- **AND** no references to analytics UI elements exist in the report_frame

#### Scenario: Test analytics callback guard for staff
- **WHEN** unit test directly invokes _show_revenue_analytics as a staff user
- **THEN** test SHALL verify _require_admin was called
- **AND** revenue analytics dialog was NOT opened
- **AND** error dialog was displayed

#### Scenario: Test analytics access allowed for admin
- **WHEN** unit test initializes main UI with an admin user
- **THEN** test SHALL verify analytics_section frame exists in UI tree
- **AND** "Revenue by Room Type" button is present and functional
- **AND** callback executes successfully without authorization errors
