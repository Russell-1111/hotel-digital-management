# Hotel Digital Management System

A Windows desktop application for managing hotel operations including reservations, room inventory, billing, and reporting. Built with Python and Tkinter for a single boutique hotel (~20 rooms).

## Features

### Core Capabilities
- **Authentication & Access Control**: Local user authentication with admin/staff roles
- **Reservation Management**: Create, modify, and cancel reservations with automatic availability checking
- **Room Inventory**: Static room configuration with real-time status tracking (Available/Reserved/Occupied)
- **Billing**: Automatic calculation with 10% service charge + 6% tax (MYR currency)
- **Reporting**: Daily check-in/out lists and monthly revenue summaries
- **Data Persistence**: SQLite database with atomic transactions
- **Automatic Backups**: Daily backups at 02:30 with 7-day retention
- **Security**: PBKDF2-HMAC-SHA256 password hashing with brute-force protection

### Business Rules
- **Check-in time**: 14:00 (2:00 PM)
- **Check-out time**: 11:00 (11:00 AM)
- **Same-day bookings**: Supported with real-time availability
- **Double-booking prevention**: Enforced through availability validation
- **Auto status transitions**: Confirmed → Checked-In (at 14:00), Checked-In → Checked-Out (at 11:00)

## System Requirements

- **Operating System**: Windows 10 or later
- **Python**: 3.10 or higher
- **Storage**: Local file system (no database required)
- **Network**: Not required (offline operation)

## Installation

### 1. Clone or Download

```powershell
cd C:\Users\User\Downloads
# Or download and extract the project folder
```

### 2. Set Up Python Environment

```powershell
cd hotel_digital_management
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install Dependencies

```powershell
pip install -r requirements.txt
```

This installs:
- `tkcalendar` - Calendar widget for date selection
- `pytest` and `pytest-cov` - Testing framework
- `tzdata` - Timezone database (required on Windows for timezone support)

### 4. Configure Settings (Optional)

Edit `config.ini` to customize:
- Data and backup directories
- Check-in/check-out times
- Backup schedule and retention
- Hotel timezone (IANA timezone name)
- Service charge and tax rates

Default `config.ini`:
```ini
[paths]
data_dir = data
backup_dir = backups

[storage]
use_sqlite = true

[ops]
check_in_time = 14:00
check_out_time = 11:00
backup_time = 02:30
backup_retention_days = 7
timezone = Asia/Kuala_Lumpur

[finance]
service_charge_rate = 0.10
tax_rate = 0.06
currency = MYR

[auth]
remember_username = false
last_username = 
```

**Important Configuration Notes:**

- **timezone**: Must be a valid IANA timezone name (e.g., `Asia/Kuala_Lumpur`, `UTC`, `America/New_York`). This determines the hotel's operational timezone for check-in/check-out times and scheduled operations. All timestamps are stored in UTC internally but displayed and scheduled according to this timezone. See the [List of tz database time zones](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones) for valid timezone names.

- **use_sqlite**: Should be `true` for SQLite storage (default). CSV storage is deprecated.

- **remember_username**: Set to `true` to remember the last logged-in username. The username will be pre-filled in the login dialog.

- **last_username**: Automatically updated when remember_username is enabled. Do not edit manually.

## Authentication & User Management

### User Roles

The system supports two user roles:

- **Admin**: Full access to all features including:
  - All reservation operations (create, modify, cancel)
  - Revenue reporting and export
  - Password changes
  
- **Staff**: Limited access:
  - View reservations
  - Create and modify reservations
  - Cannot cancel reservations
  - Cannot access revenue reports

### Login Process

1. Launch the application with `python run.py`
2. Enter your username and password in the login dialog
3. Optionally check "Remember username" to pre-fill on next login
4. Click "Login" or press Enter

**Security Features:**
- **Brute-force protection**: After 5 failed login attempts, the account is locked for 5 minutes
- **Lockout countdown**: Shows remaining time during lockout period
- **Session-based**: Must re-login after closing the application

### Changing Your Password

1. Login to the application
2. Click the **"Change Password"** button in the footer
3. Enter your current password
4. Enter and confirm your new password
5. Click "Change Password"

**Password Requirements:**
- Minimum 8 characters recommended
- Use a mix of letters, numbers, and symbols for security
- Passwords are never stored in plaintext

### Managing Users

**Adding New Users** (requires database access):

Since there's no UI for user management, additional users must be created through Python:

```python
from pathlib import Path
from app import auth

# Create a staff user
auth.create_user(
    Path("data/reservations.db"),
    username="staff1",
    password="SecurePassword123!",
    role="staff"
)

# Create an admin user
auth.create_user(
    Path("data/reservations.db"),
    username="admin2",
    password="AnotherSecure456!",
    role="admin"
)
```

**Listing Users**:

```python
from pathlib import Path
from app import auth

users = auth.list_users(Path("data/reservations.db"))
for user in users:
    print(f"{user['username']}: {user['role']} (created: {user['created_at']})")
```

### Security Best Practices

1. **Use Strong Passwords**: Minimum 12 characters with mix of character types
2. **Don't Share Accounts**: Create separate accounts for each staff member
3. **Regular Password Changes**: Change passwords every 90 days
4. **Protect the Database**: Restrict access to `data/reservations.db` file
5. **Secure Backups**: Ensure backup directory has appropriate permissions
6. **Log Review**: Monitor `logs/app.log` for suspicious authentication attempts

### Troubleshooting Authentication

**Forgot Password:**
- There is no password reset feature
- An admin user must change the password via database access
- Or restore from a backup if admin password is lost

**Account Locked Out:**
- Wait 5 minutes for lockout to expire
- Ensure you're entering the correct password
- Check `logs/app.log` for failed login attempts

**Can't Create Admin Account:**
- Ensure the database doesn't already have users
- Delete `data/reservations.db` to start fresh (loses all data)
- Check `logs/app.log` for detailed error messages

### 5. Initialize Data

On first run, the application automatically creates:
- SQLite database at `data/reservations.db`
- Users table for authentication
- Rooms and reservations tables
- `backups/` - Backup directory

#### First-Time Setup: Create Admin Account

The first time you launch the application, you'll see an **Initial Setup** dialog:

1. Enter a username for the first admin account (e.g., "admin")
2. Enter a secure password (minimum 8 characters recommended)
3. Confirm the password
4. Click "Create Admin Account"

**Important Security Notes:**
- The first user is always created as an **admin** with full permissions
- Password is hashed using PBKDF2-HMAC-SHA256 (310,000 iterations)
- Store your password securely - there is no password reset feature
- Additional users can be created later through the database (admin only)

#### Migrating from CSV to SQLite

If you have existing CSV data (`data/rooms.csv`, `data/reservations.csv`), it will be automatically migrated to SQLite on first run. The CSV files will be backed up to `data/rooms.csv.backup` and `data/reservations.csv.backup`.

## Usage

### Launch Application

```powershell
python run.py
```

Or using the virtual environment:
```powershell
.\.venv\Scripts\python.exe run.py
```

On first launch, you'll be prompted to create an admin account. On subsequent launches, you'll see the login dialog.

### User Interface

The application features a modern Tkinter UI with consistent theming, responsive layout, and clear user feedback.

**UI Highlights:**
- **Modern Theme**: ttk styling with accessible fonts (Segoe UI, 10pt)
- **Resizable Window**: Minimum 800×500, default 900×600; key widgets expand with window
- **Consistent Spacing**: 8px padding throughout for a clean, professional look
- **Input Validation**: Invalid dates show red text with brief visual feedback
- **Error Dialogs**: Clear error messages with links to `logs/app.log` for troubleshooting
- **Responsive Feedback**: Visual cues during operations

The application has four main tabs:

#### 1. Daily Ops
- View today's check-ins and check-outs
- Automatically applies status transitions based on current time
- Select any date to view scheduled operations

**How to use:**
1. Select or enter a date (YYYY-MM-DD format)
2. Click "Refresh" to update lists
3. View check-ins and check-outs for that date

#### 2. Reservations
- Create new reservations
- View all existing reservations
- Modify or cancel reservations

**Create a reservation:**
1. Enter guest details (name, phone, email)
2. Select check-in and check-out dates
3. Enter number of guests
4. Click "Check Availability" to see available rooms
5. Select a room from the dropdown
6. Click "Create Reservation"

**Modify a reservation:**
1. Select a reservation from the list
2. Click "Modify Selected"
3. Update any fields (dates, room, guest info)
4. Click "Refresh Rooms" if changing dates
5. Click "Save Changes"

**Cancel a reservation:**
1. Select a reservation from the list
2. Click "Cancel Selected" **(Admin only)**
3. Confirm the cancellation

#### 3. Availability
- Check room availability for a date range
- View all rooms and their status

**How to use:**
1. Enter start date (YYYY-MM-DD)
2. Enter end date (YYYY-MM-DD)
3. Click "Check"
4. View which rooms are Available or Unavailable

#### 4. Reports
- Generate monthly revenue summaries **(Admin only)**

**How to use:**
1. Enter year-month (YYYY-MM format, e.g., 2025-10)
2. Click "Compute Revenue"
3. View total revenue in MYR

## Architecture

### Project Structure

```
hotel_digital_management/
├── app/
│   ├── __init__.py
│   ├── auth.py             # Authentication and authorization
│   ├── billing.py          # Cost calculations (service + tax)
│   ├── config.py           # Configuration management
│   ├── reporting.py        # Daily/monthly reports
│   ├── reservations.py     # Reservation operations
│   ├── rooms.py            # Room inventory management
│   ├── storage.py          # Legacy CSV storage
│   ├── storage_sqlite.py   # SQLite storage backend
│   ├── timezone_utils.py   # Timezone handling
│   └── ui/
│       └── main.py         # Tkinter UI with auth dialogs
├── data/
│   └── reservations.db     # SQLite database (rooms, reservations, users)
├── backups/                # Timestamped database backups
├── tests/                  # Pytest test suite (>90% coverage)
│   └── test_auth.py        # Authentication tests
├── config.ini              # Application configuration
├── run.py                  # Application entry point
└── openspec/               # OpenSpec documentation
```

### Design Principles

- **Security First**: Authentication required before any operations, PBKDF2 password hashing
- **Simple Modular Structure**: Clear separation between business logic, storage, and UI
- **Database Storage**: SQLite with atomic transactions and WAL mode
- **Minimal Dependencies**: Uses Python standard library (except tkcalendar and pytest)
- **Offline Operation**: No network or external services required
- **Automatic Safety**: Status transitions, backups, and double-booking prevention

### Data Flow

1. **User Authentication** → Login Dialog (Tkinter)
2. **User Input** → UI (Tkinter)
3. **Business Logic** → Modules (auth, reservations, rooms, billing, reporting)
4. **Storage** → SQLite database with atomic transactions
5. **Backups** → Scheduled daily database copies with retention policy

## Billing Calculation

The system calculates stay costs as follows:

```
Subtotal = nightly_rate × number_of_nights
Service Charge = 10% of Subtotal
Tax = 6% of (Subtotal + Service Charge)
Total = Subtotal + Service Charge + Tax
```

**Example:** 2 nights at MYR 100.00/night
- Subtotal: MYR 200.00
- Service Charge: MYR 20.00 (10% of 200)
- Tax: MYR 13.20 (6% of 220)
- **Total: MYR 233.20**

## Testing

### Run All Tests

```powershell
python -m pytest tests/ -v
```

### Run with Coverage

```powershell
python -m pytest tests/ --cov=app --cov-report=term-missing
```

### Test Coverage

- **30+ tests** covering all core modules
- **>90% overall coverage** (target: ≥70%)
- Modules: auth (95%), billing (100%), config (100%), rooms (100%), reservations (97%), storage_sqlite (>85%)

### Test Categories

- **Unit Tests**: Authentication, password hashing, billing calculations, date logic, database operations
- **Integration Tests**: Reservation flows, backup operations, CSV to SQLite migration
- **Edge Cases**: Double-booking, invalid dates, lockout behavior, missing data
- **Security Tests**: Brute-force protection, password verification, role enforcement

## Backup and Recovery

### Timezone-Aware Operations

The system uses timezone-aware datetime handling to ensure accurate scheduling and timestamps:

- **Storage**: All timestamps are stored in UTC with ISO 8601 format
- **Display**: Times are shown in the hotel's configured timezone
- **Scheduling**: Check-in/check-out transitions and backups trigger based on hotel local time
- **Migration**: On first startup with timezone support, existing naive timestamps are automatically migrated to UTC

### Automatic Backups

- Scheduled daily at 02:30 local time
- Creates timestamped copies in `backups/` directory
- Retains last 7 days of backups automatically
- Copies both `rooms.csv` and `reservations.csv`

### Manual Backup

```powershell
# Copy data directory
xcopy data\*.csv backups\manual\ /Y
```

### Recovery

1. Stop the application
2. Restore CSV files from `backups/` to `data/`
3. Restart the application

## Troubleshooting

### Application Won't Start

**Problem**: Missing Python environment
```powershell
# Solution: Recreate virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install pytest pytest-cov
```

### Database Locked

**Problem**: Database file is locked by another process
- **Solution**: Close all instances of the application and any database browsers, then restart

### Database Locked

**Problem**: SQLite database locked
- **Solution**: Ensure only one instance of the application is running
- Check for orphaned processes in Task Manager

### Missing Reservations

**Problem**: Data file corrupted or missing
- **Solution**: Restore from `backups/` directory (SQLite database backups)

### Authentication Issues

**Problem**: Can't login or forgot password
- **Solution**: See **Authentication & User Management** section above
- Check `logs/app.log` for failed login attempts
- Admin user can reset passwords via Python script

### Wrong Room Status

**Problem**: Status not updating
- **Solution**: Click "Refresh" in Daily Ops to trigger status transitions

### Errors or Unexpected Behavior

**Problem**: Application shows an error dialog or behaves incorrectly
- **Solution**: Check `logs/app.log` in the application directory for detailed error messages
- Logs rotate daily and retain 7 days of history
- Share the log file when reporting issues

## Configuration Reference

### Time Formats
- Dates: `YYYY-MM-DD` (ISO 8601)
- Times: `HH:MM` (24-hour format)

### Status Values
- **Confirmed**: Reservation created, not yet checked in
- **Checked-In**: Guest has checked in (auto at 14:00 or manual)
- **Checked-Out**: Guest has checked out (auto at 11:00)
- **Cancelled**: Reservation cancelled (room freed)

### Room Status (Derived)
- **Available**: No active reservations
- **Reserved**: Future reservation exists
- **Occupied**: Guest currently checked in

## Development

### OpenSpec Documentation

This project follows OpenSpec spec-driven development. See:
- `openspec/project.md` - Project conventions and tech stack
- `openspec/changes/archive/2025-10-24-add-hotel-core-ops/` - Implementation proposal

### Code Style

- **Naming**: `snake_case` for functions/variables, `PascalCase` for classes
- **File naming**: `kebab-case.py` for modules
- **Formatting**: Black (line length 100)
- **Type hints**: Required for public functions
- **Docstrings**: Google-style for public APIs

### Running from Source

```powershell
# Development mode
python -m app.ui.main

# Or via entry point
python run.py
```

## Limitations

- Single-property support only
- Single concurrent user (file locking serializes writes)
- CSV storage (not suitable for >1000 rooms or high concurrency)
- No online booking integration
- No payment processing
- Windows-only (Tkinter + file locking implementation)

## Future Enhancements

Potential improvements (not currently implemented):
- Multi-property support
- Database backend (SQLite/PostgreSQL)
- Web interface
- Mobile app
- Channel manager integration (Booking.com, Expedia)
- Email/SMS notifications
- Advanced reporting (occupancy trends, guest analytics)
- Payment gateway integration

## License

This project is for internal use. All rights reserved.

## Support

For issues or questions:
1. Check this README
2. Review logs at `logs/app.log` for detailed error messages (7-day retention)
3. Review `openspec/project.md` for technical details
4. Run tests to validate your environment

## Version History

### v2.0.0 (2025-11-07)
- **Authentication System**: Local user authentication with admin/staff roles
- **Security**: PBKDF2-HMAC-SHA256 password hashing (310,000 iterations)
- **Brute-force Protection**: 5 failed attempts = 5 minute lockout
- **SQLite Migration**: Migrated from CSV to SQLite database
- **Role-Based Access**: Admin-only actions (cancel reservations, revenue reports)
- **Password Management**: Change password functionality
- **User Management**: Create/list users programmatically
- **Test Coverage**: 95% coverage on auth module, 30+ total tests

### v1.0.0 (2025-10-24)
- Initial release
- Core reservation management
- Billing with service charge and tax
- Daily/monthly reporting
- Automatic backups
- 90% test coverage
