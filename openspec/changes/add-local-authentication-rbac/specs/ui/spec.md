## ADDED Requirements

### Requirement: Initial Setup Dialog
The system SHALL display a modal dialog to create the first admin account when no users exist in the database.

#### Scenario: Show initial setup on first run
- **WHEN** the application starts and the users table has 0 rows
- **THEN** the system displays an `InitialSetupDialog` before showing the login dialog
- **AND** the dialog is modal (blocks access to other windows)
- **AND** the dialog title is "Initial Setup - Create Administrator Account"

#### Scenario: Initial setup form fields
- **WHEN** the `InitialSetupDialog` is displayed
- **THEN** it contains a username entry field (plain text)
- **AND** a password entry field (masked with show/hide toggle)
- **AND** a confirm password entry field (masked with show/hide toggle)
- **AND** a "Create Admin Account" button
- **AND** a status label for displaying validation errors or success messages

#### Scenario: Validate initial admin creation
- **WHEN** the user clicks "Create Admin Account"
- **THEN** the system validates that username is not empty
- **AND** validates that password is at least 8 characters long
- **AND** validates that password and confirm password fields match
- **AND** if validation fails, displays an inline error message and allows retry

#### Scenario: Create first admin account
- **WHEN** the user submits valid credentials in the initial setup dialog
- **THEN** the system calls `auth.create_user(db_path, username, password, 'admin')`
- **AND** displays a success message "Administrator account created successfully"
- **AND** closes the dialog after 1 second
- **AND** proceeds to the login dialog

#### Scenario: Cannot cancel initial setup
- **WHEN** the `InitialSetupDialog` is displayed
- **THEN** the dialog cannot be closed via the X button (disabled or closes application)
- **AND** the user must create an admin account to proceed

### Requirement: Login Dialog
The system SHALL display a modal login dialog on application startup that authenticates users before granting access to the main interface.

#### Scenario: Show login dialog on startup
- **WHEN** the application starts and at least one user exists in the database
- **THEN** the system displays a `LoginDialog` before building the main window
- **AND** the dialog is modal (blocks access to other windows)
- **AND** the dialog title is "Login - Hotel Digital Management"

#### Scenario: Login form fields
- **WHEN** the `LoginDialog` is displayed
- **THEN** it contains a username entry field (plain text)
- **AND** a password entry field (masked with show/hide toggle)
- **AND** a "Remember Username" checkbox
- **AND** a "Login" button
- **AND** a status label for displaying error messages

#### Scenario: Remember username feature
- **WHEN** the "Remember Username" checkbox is enabled and login succeeds
- **THEN** the system saves the username to `config.ini` under `[auth]` section as `last_username`
- **AND** sets `remember_username = true` in config
- **WHEN** the login dialog appears on subsequent runs
- **THEN** the username field is pre-filled with the saved username if `remember_username = true`

#### Scenario: Successful login
- **WHEN** the user enters valid credentials and clicks "Login"
- **THEN** the system calls `auth.verify_user(db_path, username, password)`
- **AND** if authentication succeeds, sets `App.current_user = {'username': username, 'role': role}`
- **AND** closes the login dialog
- **AND** proceeds to build and display the main application window

#### Scenario: Failed login with incorrect password
- **WHEN** the user enters incorrect credentials and clicks "Login"
- **THEN** the system displays an inline error message "Invalid username or password"
- **AND** clears the password field
- **AND** allows the user to retry
- **AND** increments the failed login counter

#### Scenario: Display lockout countdown
- **WHEN** the user is locked out after 5 failed attempts
- **THEN** the login button is disabled
- **AND** the status label displays "Account locked. Try again in X seconds." (countdown updates every second)
- **AND** when lockout expires, the login button is re-enabled and status clears

#### Scenario: Exit application on dialog close
- **WHEN** the user closes the login dialog without successfully logging in (X button or Alt+F4)
- **THEN** the application exits with code 0
- **AND** no main window is displayed

### Requirement: Current User Session Management
The system SHALL maintain the current user's identity and role in memory for the duration of the application session.

#### Scenario: Store current user on successful login
- **WHEN** a user successfully authenticates
- **THEN** the `App` class stores the user information in `self.current_user: Dict[str, str]`
- **AND** the dictionary contains keys `'username'` and `'role'`
- **AND** this information is accessible to all UI components and action handlers

#### Scenario: Clear session on application exit
- **WHEN** the application is closed
- **THEN** the `current_user` attribute is cleared (garbage collected)
- **AND** no session persistence or token storage occurs

### Requirement: Role-Based Access Control for UI Actions
The system SHALL enforce role-based permissions by checking the current user's role before allowing sensitive operations.

#### Scenario: Protect cancel reservation action (admin-only)
- **WHEN** a user clicks "Cancel Reservation" button
- **THEN** the system checks `self.current_user['role']`
- **AND** if role is 'staff', displays error dialog: "This action requires administrator privileges"
- **AND** if role is 'admin', proceeds with the cancellation workflow

#### Scenario: Protect revenue report export (admin-only)
- **WHEN** a user attempts to export or compute a revenue report
- **THEN** the system checks `self.current_user['role']`
- **AND** if role is 'staff', displays error dialog: "This action requires administrator privileges"
- **AND** if role is 'admin', proceeds with the report generation

#### Scenario: Protect manual backup trigger (admin-only)
- **WHEN** a user attempts to trigger a manual backup (if exposed in UI)
- **THEN** the system checks `self.current_user['role']`
- **AND** if role is 'staff', displays error dialog: "This action requires administrator privileges"
- **AND** if role is 'admin', proceeds with the backup operation

#### Scenario: Log access denial attempts
- **WHEN** a staff user attempts an admin-only action
- **THEN** the system logs a WARNING level entry: "User '{username}' (staff) attempted admin action: {action_name}"
- **AND** the log entry includes a timestamp

### Requirement: Password Change Dialog
The system SHALL provide a dialog for users to change their password while logged in.

#### Scenario: Open change password dialog
- **WHEN** a logged-in user selects "Change Password" from a menu or button
- **THEN** the system displays a `ChangePasswordDialog` (modal)
- **AND** the dialog title is "Change Password"

#### Scenario: Change password form fields
- **WHEN** the `ChangePasswordDialog` is displayed
- **THEN** it contains an "Old Password" entry field (masked with show/hide toggle)
- **AND** a "New Password" entry field (masked with show/hide toggle)
- **AND** a "Confirm New Password" entry field (masked with show/hide toggle)
- **AND** a "Change Password" button
- **AND** a "Cancel" button
- **AND** a status label for displaying error or success messages

#### Scenario: Validate password change
- **WHEN** the user clicks "Change Password"
- **THEN** the system validates that old password is not empty
- **AND** validates that new password is at least 8 characters long
- **AND** validates that new password and confirm new password fields match
- **AND** if validation fails, displays an inline error message

#### Scenario: Change password successfully
- **WHEN** the user submits valid passwords in the change password dialog
- **THEN** the system calls `auth.change_password(db_path, username, old_password, new_password)`
- **AND** if the call returns `True`, displays "Password changed successfully"
- **AND** closes the dialog after 1 second
- **AND** if the call returns `False`, displays "Incorrect old password"

#### Scenario: Cancel password change
- **WHEN** the user clicks "Cancel" in the change password dialog
- **THEN** the dialog closes without making any changes
- **AND** the user remains logged in with the current password

### Requirement: Authentication Configuration
The system SHALL support authentication-related configuration settings in `config.ini`.

#### Scenario: Load authentication settings from config
- **WHEN** the application loads configuration from `config.ini`
- **THEN** it reads the `[auth]` section if present
- **AND** loads `remember_username` boolean setting (default: `false`)
- **AND** loads `last_username` string setting (default: empty string)

#### Scenario: Save remember username setting
- **WHEN** the user enables "Remember Username" and logs in successfully
- **THEN** the system writes to `config.ini` under `[auth]`:
  ```
  [auth]
  remember_username = true
  last_username = {username}
  ```
- **AND** the config file is updated atomically to prevent corruption

#### Scenario: Clear remembered username
- **WHEN** the user unchecks "Remember Username" and logs in
- **THEN** the system writes to `config.ini`:
  ```
  [auth]
  remember_username = false
  last_username = 
  ```
- **AND** subsequent login dialogs start with an empty username field

### Requirement: Login Dialog UX Polish
The system SHALL provide a smooth and accessible user experience in the login and setup dialogs.

#### Scenario: Show/hide password toggle
- **WHEN** the user clicks the show/hide password icon or checkbox next to a password field
- **THEN** the password field toggles between masked (`show='*'`) and plain text (`show=''`)
- **AND** the toggle icon or label updates to reflect the current state (e.g., "Show" / "Hide")

#### Scenario: Enter key submits form
- **WHEN** the user presses Enter while focused in the username or password field
- **THEN** the login dialog submits the form (equivalent to clicking "Login" button)
- **AND** the initial setup dialog submits the form (equivalent to clicking "Create Admin Account")
- **AND** the change password dialog submits the form (equivalent to clicking "Change Password")

#### Scenario: Tab navigation between fields
- **WHEN** the user presses Tab in a dialog
- **THEN** focus moves to the next field in logical order (username → password → confirm/checkbox → button)
- **AND** Shift+Tab moves focus backwards

#### Scenario: Inline error message display
- **WHEN** an error occurs during login, setup, or password change
- **THEN** the error message is displayed in red text below the form fields
- **AND** the message is concise and actionable (e.g., "Password must be at least 8 characters")
- **AND** previous error messages are cleared before displaying new ones
