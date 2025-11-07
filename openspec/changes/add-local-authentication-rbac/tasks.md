## 1. Database Schema
- [x] 1.1 Add `users` table to `init_schema()` in `app/storage_sqlite.py`
- [x] 1.2 Add schema migration check for users table (CREATE IF NOT EXISTS)
- [x] 1.3 Test schema initialization with empty database
- [x] 1.4 Verify foreign key constraints and indexes work correctly

## 2. Authentication Module (`app/auth.py`)
- [x] 2.1 Implement `_hash_password(password: str) -> str` helper (salt + PBKDF2-HMAC-SHA256)
- [x] 2.2 Implement `_verify_password(password: str, password_hash: str) -> bool` helper
- [x] 2.3 Implement `create_user(db_path: Path, username: str, password: str, role: str) -> None`
- [x] 2.4 Implement `verify_user(db_path: Path, username: str, password: str) -> Optional[str]` (returns role or None)
- [x] 2.5 Implement `change_password(db_path: Path, username: str, old_password: str, new_password: str) -> bool`
- [x] 2.6 Implement `list_users(db_path: Path) -> List[Dict[str, str]]` (admin-only, returns username, role, created_at)
- [x] 2.7 Add in-memory failed login tracking with lockout logic
- [x] 2.8 Implement `check_lockout(username: str) -> Optional[int]` (returns remaining lockout seconds or None)
- [x] 2.9 Implement `record_failed_login(username: str) -> None`
- [x] 2.10 Implement `reset_failed_logins(username: str) -> None`

## 3. Initial Setup Dialog (`app/ui/main.py`)
- [x] 3.1 Create `InitialSetupDialog` class (Toplevel, modal)
- [x] 3.2 Add username entry field with validation (non-empty)
- [x] 3.3 Add password entry fields (password, confirm password) with show/hide toggle
- [x] 3.4 Add minimum password length validation (8 characters)
- [x] 3.5 Add password confirmation matching check
- [x] 3.6 Add "Create Admin Account" button that calls `auth.create_user()`
- [x] 3.7 Handle errors gracefully with inline error messages
- [x] 3.8 Close dialog on successful admin creation

## 4. Login Dialog (`app/ui/main.py`)
- [x] 4.1 Create `LoginDialog` class (Toplevel, modal)
- [x] 4.2 Add username entry field
- [x] 4.3 Add password entry field with show/hide toggle
- [x] 4.4 Add "Remember Username" checkbox (saves to config.ini)
- [x] 4.5 Add "Login" button that calls `auth.verify_user()`
- [x] 4.6 Display inline error messages for failed login
- [x] 4.7 Implement lockout display (show countdown timer if locked out)
- [x] 4.8 Set `App.current_user` on successful login
- [x] 4.9 Close dialog on successful login
- [x] 4.10 Exit application if dialog closed without login (window protocol handler)

## 5. Main Application Integration (`app/ui/main.py`)
- [x] 5.1 Add `current_user: Optional[Dict[str, str]]` attribute to `App` class (stores username, role)
- [x] 5.2 Check user count on startup (before building UI)
- [x] 5.3 Show `InitialSetupDialog` if no users exist
- [x] 5.4 Show `LoginDialog` after setup (or directly if users exist)
- [x] 5.5 Block UI construction until successful login
- [x] 5.6 Load remembered username from config if checkbox enabled

## 6. Role-Based Access Control (`app/ui/main.py`)
- [x] 6.1 Add `_require_admin(action_name: str) -> bool` helper method
- [x] 6.2 Protect "Cancel Reservation" button click handler with admin check
- [x] 6.3 Protect "Export Revenue Report" action with admin check
- [x] 6.4 Protect "Trigger Manual Backup" action (if exposed in UI) with admin check
- [x] 6.5 Show error dialog when staff attempts admin-only action: "This action requires administrator privileges"
- [x] 6.6 Log access denial attempts to app.log

## 7. Password Change Feature (`app/ui/main.py`)
- [x] 7.1 Create `ChangePasswordDialog` class (Toplevel, modal)
- [x] 7.2 Add old password entry field
- [x] 7.3 Add new password entry fields (password, confirm) with show/hide toggle
- [x] 7.4 Validate old password via `auth.verify_user()`
- [x] 7.5 Validate new passwords match and meet minimum length (8 chars)
- [x] 7.6 Call `auth.change_password()` and show success/error message
- [x] 7.7 Add "Change Password" menu item or button in UI (accessible to all logged-in users)

## 8. Configuration Updates (`config.ini`)
- [x] 8.1 Add `[auth]` section to config.ini
- [x] 8.2 Add `remember_username = false` setting
- [x] 8.3 Add `last_username = ` setting (populated by checkbox)
- [x] 8.4 Update `load_config()` in `app/rooms.py` to parse auth section

## 9. Unit Tests (`tests/test_auth.py`)
- [x] 9.1 Test `create_user()` with valid admin role
- [x] 9.2 Test `create_user()` with valid staff role
- [x] 9.3 Test `create_user()` with duplicate username (should fail)
- [x] 9.4 Test `verify_user()` with correct password (returns role)
- [x] 9.5 Test `verify_user()` with incorrect password (returns None)
- [x] 9.6 Test `verify_user()` with non-existent username (returns None)
- [x] 9.7 Test `change_password()` with correct old password (succeeds)
- [x] 9.8 Test `change_password()` with incorrect old password (fails)
- [x] 9.9 Test failed login lockout (5 failures trigger 5-minute lockout)
- [x] 9.10 Test lockout expiration (can login after 5 minutes)
- [x] 9.11 Test password hash format (contains salt and hash, hex-encoded)
- [x] 9.12 Test `list_users()` returns all users with correct fields

## 10. Integration Tests (`tests/test_ui.py` or new test file)
- [x] 10.1 Test initial setup flow with empty database (mock dialog interactions)
- [x] 10.2 Test login flow with valid credentials (mock dialog)
- [x] 10.3 Test login flow with invalid credentials (mock dialog)
- [x] 10.4 Test role enforcement: staff cannot cancel reservation
- [x] 10.5 Test role enforcement: admin can cancel reservation
- [x] 10.6 Test role enforcement: staff cannot export report
- [x] 10.7 Test role enforcement: admin can export report
- [x] 10.8 Test remember username saves and loads from config

## 11. Documentation
- [x] 11.1 Update README.md with authentication setup instructions
- [x] 11.2 Document initial admin account creation flow
- [x] 11.3 Document admin vs staff role differences
- [x] 11.4 Add troubleshooting section for forgotten admin password (manual DB reset)
- [x] 11.5 Update USER_GUIDE.md with login and password change instructions
- [x] 11.6 Add security best practices section (password recommendations, workstation locking)

## 12. Validation and Cleanup
- [x] 12.1 Run all unit tests and ensure 100% pass rate
- [x] 12.2 Run integration tests and verify UI flows work correctly
- [x] 12.3 Perform manual testing against checklist in design.md
- [x] 12.4 Run `pytest --cov=app.auth` and verify >90% code coverage for auth module
- [x] 12.5 Review code for security issues (no plaintext passwords, proper salt handling)
- [x] 12.6 Ensure all error messages are user-friendly and log technical details
- [x] 12.7 Verify database schema migration works on fresh and existing installations
- [x] 12.8 Update spec deltas and run `openspec validate add-local-authentication-rbac --strict`
