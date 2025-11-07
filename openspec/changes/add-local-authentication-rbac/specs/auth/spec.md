## ADDED Requirements

### Requirement: User Account Management
The system SHALL provide functions to create, authenticate, and manage user accounts with role-based access control.

#### Scenario: Create admin user
- **WHEN** `create_user(db_path, username, password, 'admin')` is called
- **THEN** the system creates a new user record in the `users` table with hashed password and 'admin' role
- **AND** the password is hashed using PBKDF2-HMAC-SHA256 with 310,000 iterations and a unique 32-byte random salt
- **AND** `created_at` and `updated_at` timestamps are set to current UTC time

#### Scenario: Create staff user
- **WHEN** `create_user(db_path, username, password, 'staff')` is called
- **THEN** the system creates a new user record with hashed password and 'staff' role
- **AND** the password hashing follows the same security standards as admin users

#### Scenario: Reject duplicate username
- **WHEN** `create_user()` is called with a username that already exists in the database
- **THEN** the function raises a `ValueError` with message "Username already exists"
- **AND** no new user record is created

#### Scenario: Validate role values
- **WHEN** `create_user()` is called with an invalid role (not 'admin' or 'staff')
- **THEN** the function raises a `ValueError` with message "Role must be 'admin' or 'staff'"
- **AND** no user record is created

### Requirement: Password Authentication
The system SHALL authenticate users by verifying passwords against stored hashes and return the user's role on success.

#### Scenario: Successful login with correct password
- **WHEN** `verify_user(db_path, username, password)` is called with correct credentials
- **THEN** the function returns the user's role as a string ('admin' or 'staff')
- **AND** resets failed login counter for that username

#### Scenario: Failed login with incorrect password
- **WHEN** `verify_user()` is called with incorrect password
- **THEN** the function returns `None`
- **AND** increments the failed login counter for that username
- **AND** records the failed attempt timestamp

#### Scenario: Non-existent username
- **WHEN** `verify_user()` is called with a username that doesn't exist
- **THEN** the function returns `None`
- **AND** does not increment failed login counter (prevents username enumeration timing attacks)

### Requirement: Secure Password Hashing
The system SHALL use PBKDF2-HMAC-SHA256 with strong parameters to hash and verify passwords.

#### Scenario: Generate password hash with unique salt
- **WHEN** hashing a password for storage
- **THEN** the system generates a cryptographically secure 32-byte random salt using `secrets.token_bytes(32)`
- **AND** computes the hash using PBKDF2-HMAC-SHA256 with 310,000 iterations
- **AND** stores the result in format `"salt_hex:hash_hex"` where both are hex-encoded

#### Scenario: Verify password against stored hash
- **WHEN** verifying a password
- **THEN** the system extracts the salt from the stored hash string
- **AND** recomputes the hash using the same salt and iteration count
- **AND** performs constant-time comparison of hashes to prevent timing attacks

### Requirement: Brute-Force Protection
The system SHALL protect against brute-force login attempts by temporarily locking out users after repeated failures.

#### Scenario: Lock out after 5 failed attempts
- **WHEN** a user fails to login 5 times within a 5-minute window
- **THEN** `check_lockout(username)` returns the number of seconds remaining in the lockout period (300 seconds)
- **AND** `verify_user()` immediately returns `None` without checking the password
- **AND** a log entry is created recording the lockout event

#### Scenario: Lockout expires after 5 minutes
- **WHEN** a user is locked out and 5 minutes elapse since the 5th failed attempt
- **THEN** `check_lockout(username)` returns `None` (lockout expired)
- **AND** the user can attempt to login again
- **AND** the failed login counter is reset

#### Scenario: Successful login resets failed counter
- **WHEN** a user successfully authenticates
- **THEN** all failed login attempts for that username are cleared from the tracking dictionary
- **AND** the lockout state is reset

#### Scenario: In-memory lockout state
- **WHEN** the application restarts
- **THEN** all lockout states and failed login counters are reset (in-memory tracking only)
- **AND** users previously locked out can attempt login immediately after restart

### Requirement: Password Change
The system SHALL allow users to change their passwords after verifying their current password.

#### Scenario: Change password with valid old password
- **WHEN** `change_password(db_path, username, old_password, new_password)` is called
- **THEN** the system verifies the old password matches the current hash
- **AND** generates a new hash for the new password with a fresh salt
- **AND** updates the `password_hash` and `updated_at` fields in the database
- **AND** returns `True` to indicate success

#### Scenario: Reject password change with incorrect old password
- **WHEN** `change_password()` is called with an incorrect old password
- **THEN** the system verifies the old password and finds it does not match
- **AND** does not update the database
- **AND** returns `False` to indicate failure

#### Scenario: Update timestamp on password change
- **WHEN** a password is successfully changed
- **THEN** the `updated_at` field is set to the current UTC timestamp
- **AND** the `created_at` field remains unchanged

### Requirement: User Listing
The system SHALL provide a function to list all users with their metadata (admin-only feature).

#### Scenario: List all users
- **WHEN** `list_users(db_path)` is called
- **THEN** the function returns a list of dictionaries with keys: `username`, `role`, `created_at`
- **AND** password hashes are NOT included in the results
- **AND** users are sorted by username alphabetically

#### Scenario: Empty user list
- **WHEN** `list_users()` is called and no users exist in the database
- **THEN** the function returns an empty list `[]`

### Requirement: Authentication Module Logging
The system SHALL log authentication events and security-relevant operations to the application log.

#### Scenario: Log user creation
- **WHEN** a new user is created
- **THEN** a log entry is written at INFO level: "Created user '{username}' with role '{role}'"
- **AND** the log entry includes a timestamp

#### Scenario: Log failed login attempts
- **WHEN** a login attempt fails due to incorrect password
- **THEN** a log entry is written at WARNING level: "Failed login attempt for user '{username}'"
- **AND** the log entry includes the timestamp of the attempt

#### Scenario: Log lockout events
- **WHEN** a user is locked out due to excessive failed attempts
- **THEN** a log entry is written at WARNING level: "User '{username}' locked out for 5 minutes after 5 failed attempts"
- **AND** the log entry includes the lockout start timestamp

#### Scenario: Log password changes
- **WHEN** a user successfully changes their password
- **THEN** a log entry is written at INFO level: "User '{username}' changed password"
- **AND** the log entry includes a timestamp
