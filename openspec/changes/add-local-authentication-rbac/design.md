## Context
The hotel front desk operates on a shared workstation where multiple staff members may log in throughout the day. Currently, there is no authentication or access control, creating security and accountability gaps. This design introduces a lightweight, local authentication system appropriate for a single-workstation desktop application.

## Goals / Non-Goals

### Goals
- Prevent unauthorized access to the application and sensitive operations
- Distinguish between admin and staff roles with different permissions
- Protect passwords using industry-standard hashing (PBKDF2-HMAC-SHA256)
- Provide clear, simple UX for login and password management
- Maintain single-operator simplicity (no concurrent sessions or complex state)

### Non-Goals
- Multi-user concurrent access (still single operator at a time)
- Network authentication or centralized user directory (LDAP/AD)
- Password recovery via email or external mechanisms
- Session timeout or auto-logout features
- Comprehensive audit logging (may be added separately)
- Password complexity requirements enforcement (recommended in UI but not enforced)

## Decisions

### Decision: Use PBKDF2-HMAC-SHA256 for Password Hashing
**Why**: PBKDF2 is a well-established, NIST-recommended key derivation function available in Python's standard library (`hashlib`). It provides strong protection against brute-force attacks through configurable iterations.

**Implementation Details**:
- Algorithm: PBKDF2-HMAC-SHA256
- Iterations: 310,000 (OWASP 2023 recommendation for PBKDF2-SHA256)
- Salt: 32 bytes random salt generated per user via `secrets.token_bytes(32)`
- Storage format: `salt:hash` (both hex-encoded) in `users.password_hash` column

**Alternatives Considered**:
- `bcrypt` via `passlib`: More resistant to GPU attacks, but requires external dependency. PBKDF2 sufficient for local desktop use case.
- `argon2`: Best modern choice, but requires native libraries; deployment complexity not justified for this use case.
- Plain SHA-256: Insecure; rejected.

### Decision: In-Memory Failed Login Tracking
**Why**: Simple brute-force protection without database complexity. Resets on application restart, which is acceptable for a local desktop app.

**Implementation**:
- Track failed attempts per username in a module-level dictionary: `_failed_attempts: Dict[str, List[datetime]]`
- After 5 failed attempts within a rolling 5-minute window, deny login for that username for 5 minutes
- Clear successful login resets the counter for that user
- No persistent storage; state resets on app restart

**Alternatives Considered**:
- Persistent lockout in database: More robust but adds complexity; overkill for local use
- Account lockout requiring admin unlock: Too disruptive for small team
- No brute-force protection: Unacceptable security posture

### Decision: Modal Login Dialog on Startup
**Why**: Desktop application pattern; ensures authentication before any data access.

**Implementation**:
- `LoginDialog` class (Toplevel window, modal)
- Blocks main window until successful login or user closes app
- If dialog closed without login, application exits
- Displays error messages inline with retry capability
- Optional "Remember Username" checkbox (stores last username in config, not password)

**Alternatives Considered**:
- Embedded login in main window: Less secure; allows browsing UI before auth
- Separate login executable: Unnecessary complexity for single-app scenario

### Decision: Role-Based Access via Simple String Comparison
**Why**: Only two roles (admin, staff); no need for complex permissions framework.

**Implementation**:
- Roles stored as text: `'admin'` or `'staff'`
- `App.current_user` attribute stores `{'username': str, 'role': str}` after login
- Protected actions check `if self.current_user['role'] != 'admin': show_error(); return`
- Admin-only actions: cancel reservation, export reports, trigger backups, user management

**Alternatives Considered**:
- Permissions bitmap: Over-engineered for two roles
- Decorator-based access control: Doesn't fit Tkinter callback pattern well

### Decision: Initial Setup Flow for First Admin
**Why**: Bootstrapping problem—no users exist initially; need secure way to create first admin.

**Implementation**:
- On startup, before showing login dialog, check `SELECT COUNT(*) FROM users`
- If count is 0, show `InitialSetupDialog` to create first admin account
- Prompt for username and password (with confirmation)
- Enforce minimum password length (8 characters) in setup dialog
- After creation, proceed to normal login flow

**Alternatives Considered**:
- Hardcoded default admin account: Security risk; bad practice
- Command-line user creation tool: Extra step for deployment; less user-friendly

## Database Schema

### Users Table
```sql
CREATE TABLE IF NOT EXISTS users (
    username TEXT PRIMARY KEY,
    password_hash TEXT NOT NULL,  -- Format: "salt_hex:hash_hex"
    role TEXT NOT NULL CHECK (role IN ('admin', 'staff')),
    created_at TEXT NOT NULL,  -- ISO8601 UTC timestamp
    updated_at TEXT NOT NULL   -- ISO8601 UTC timestamp (for password changes)
)
```

### Schema Migration
- Extend `init_schema()` in `app/storage_sqlite.py` to add `users` table if it doesn't exist
- No data migration needed (fresh table)
- Schema version remains 1 (additive change, no breaking modifications)

## Security Considerations

### Password Storage
- Never store plaintext passwords
- Use cryptographically secure random salt per user
- Verify password by recomputing hash with stored salt and comparing

### Brute-Force Protection
- Temporary lockout prevents automated password guessing
- 5-minute lockout duration balances security and usability
- In-memory tracking acceptable for local desktop app

### Session Management
- Current user stored in `App.current_user` (in-memory only)
- No persistent session tokens (fresh login each app start)
- Application exit clears session state

### Password Change Flow
- Require old password verification before accepting new password
- Update `password_hash` and `updated_at` timestamp atomically
- Display success confirmation and optionally log event

## UX Flow Diagrams

### Startup Flow
```
1. Application starts
2. Check if users table has any rows
   - If empty → Show InitialSetupDialog → Create admin → Continue to login
   - If not empty → Continue to login
3. Show LoginDialog (modal)
   - User enters username/password
   - On success → Load main window with current_user set
   - On failure → Increment failed attempts, show error, allow retry
   - If 5 failures → Show lockout message with countdown
   - On dialog close → Exit application
```

### Protected Action Flow
```
1. User clicks "Cancel Reservation" button
2. Check self.current_user['role']
   - If 'admin' → Proceed with cancellation
   - If 'staff' → Show error dialog: "This action requires administrator privileges"
3. End
```

### Password Change Flow
```
1. User selects "Change Password" from menu (or button)
2. Show ChangePasswordDialog
3. Prompt for: old password, new password, confirm new password
4. Validate:
   - Old password matches current hash
   - New passwords match each other
   - New password meets minimum length (8 chars)
5. Update database: new hash, updated_at timestamp
6. Show success message
```

## Risks / Trade-offs

### Risk: Forgotten Admin Password
**Impact**: No access to application; no recovery mechanism.

**Mitigation**:
- Document manual database reset procedure in README (delete users table row and restart app)
- Consider adding admin password reset via config file flag in future iteration
- Recommend writing down initial admin password in secure location

### Trade-off: No Session Timeout
**Choice**: No auto-logout or session timeout.

**Rationale**: Workstation is typically in a controlled environment (front desk). Auto-logout would disrupt workflow. User can manually close app if leaving workstation unattended.

**Mitigation**: Recommend organizational policy for locking workstation when unattended.

### Risk: In-Memory Lockout State
**Impact**: Lockout state resets on application restart, allowing retry of brute-force attacks.

**Mitigation**: Acceptable for local desktop app. Persistent lockout would be excessive. Physical access to workstation already provides attack vectors.

## Migration Plan

### Existing Installations
1. User starts updated application
2. Database schema initializes `users` table (if not exists)
3. No users exist → InitialSetupDialog appears
4. User creates first admin account
5. Normal operation resumes

### Steps
- No manual migration steps required
- Automatic schema update on first run
- Zero downtime (single-user app)

### Rollback
- If downgrade needed: users table is unused by old code; safe to leave in database
- To fully rollback: manually drop users table via SQLite CLI (optional)

## Testing Strategy

### Unit Tests (`tests/test_auth.py`)
- `test_create_user`: Verify user creation with hashed password
- `test_verify_user_success`: Correct password returns role
- `test_verify_user_failure`: Incorrect password returns None
- `test_change_password`: Old password verified, new hash stored
- `test_list_users_admin_only`: Admin can list users, staff cannot (future)
- `test_failed_login_lockout`: 5 failures triggers lockout
- `test_lockout_expires`: Lockout expires after 5 minutes
- `test_password_hash_format`: Verify salt:hash format

### Integration Tests
- `test_initial_setup_flow`: Empty database triggers setup dialog (mock)
- `test_login_flow_success`: Valid credentials grant access
- `test_login_flow_failure`: Invalid credentials deny access
- `test_role_enforcement_cancel_reservation`: Staff blocked, admin allowed
- `test_role_enforcement_export_report`: Staff blocked, admin allowed

### Manual Testing Checklist
- [ ] First run: setup dialog appears, admin created successfully
- [ ] Login with correct credentials: main window loads
- [ ] Login with incorrect credentials: error shown, retry allowed
- [ ] 5 failed logins: lockout message displayed, login disabled for 5 minutes
- [ ] Remember username: checkbox saves/loads username from config
- [ ] Change password: old password required, new password validated and stored
- [ ] Admin cancels reservation: action completes
- [ ] Staff cancels reservation: error dialog shown
- [ ] Admin exports report: action completes
- [ ] Staff exports report: error dialog shown

## Open Questions
None at this time. Design is straightforward and aligns with established patterns for local desktop authentication.
