# Add Local Authentication and Role-Based Access Control

## Why
The hotel management system currently has no access control, allowing anyone with physical access to the computer to perform sensitive operations like canceling reservations, exporting revenue data, modifying configuration, or triggering backups. This poses security and accountability risks in a front desk environment where multiple staff members may use the same workstation. Adding local authentication with role-based access control (admin vs. staff) will enforce least-privilege principles, prevent unauthorized actions, and create an audit trail for sensitive operations.

## What Changes
- Create new `app/auth.py` module with user management and authentication functions
- Add `users` table to SQLite database schema with secure password storage
- Implement login dialog in UI that appears on application startup
- Enforce role-based access control for sensitive UI actions (admin-only operations)
- Provide initial setup flow for creating first admin account when no users exist
- Implement brute-force protection with temporary lockout after failed login attempts
- Add unit tests for authentication logic and role enforcement
- Support optional "remember username" feature (no password storage) for convenience
- Add password change capability for logged-in users

### Key Features
- **User Management**: Create users with username, hashed password, and role (admin or staff)
- **Password Security**: Use `hashlib.pbkdf2_hmac` with SHA-256, strong random salt, and 310,000 iterations (OWASP 2023 recommendation)
- **Login Flow**: Modal dialog on startup; blocks access until successful authentication
- **Role-Based Access**: Protect admin-only actions (cancel reservation, revenue export, backups, config edits) with role checks
- **Brute-Force Protection**: Lock out account for 5 minutes after 5 consecutive failed login attempts (in-memory tracking)
- **Initial Setup**: Prompt to create first admin user if database has no users
- **Password Changes**: Allow users to change their own password via UI dialog
- **Session Management**: Store current user context (username, role) in App instance after successful login

### Protected Admin-Only Actions
- Cancel reservation
- Export revenue reports
- Trigger manual backups
- Edit configuration settings (if/when exposed in UI)
- Create/delete user accounts (future enhancement)

## Impact
- **Affected specs**: `auth` (new), `ui` (modified), `storage` (modified)
- **Affected code**: 
  - New: `app/auth.py`, `tests/test_auth.py`
  - Modified: `app/storage_sqlite.py` (add users table to schema), `app/ui/main.py` (add login dialog and role checks)
- **Dependencies**: No new external dependencies (use standard library `hashlib`, `secrets`, `sqlite3`)
- **Database schema**: Add `users` table with migration for existing installations
- **User experience**: Adds login step on startup; minimal friction for daily use with "remember username" option
- **Breaking changes**: None (existing installations will prompt for initial admin setup)
- **Security posture**: Significantly improved with authentication and access control

## Non-Goals (Out of Scope)
- Multi-user concurrent sessions (still single-operator workstation)
- Password reset via email or external recovery mechanism
- Session timeout or auto-logout (assumes trusted workstation environment)
- Centralized user management or LDAP/AD integration
- Audit logging of user actions (may be added in future change)
- Password complexity requirements enforcement (recommended but not enforced)
- Two-factor authentication (future enhancement)
