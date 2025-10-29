# Hotel Digital Management System

A Windows desktop application for managing hotel operations including reservations, room inventory, billing, and reporting. Built with Python and Tkinter for a single boutique hotel (~20 rooms).

## Features

### Core Capabilities
- **Reservation Management**: Create, modify, and cancel reservations with automatic availability checking
- **Room Inventory**: Static room configuration with real-time status tracking (Available/Reserved/Occupied)
- **Billing**: Automatic calculation with 10% service charge + 6% tax (MYR currency)
- **Reporting**: Daily check-in/out lists and monthly revenue summaries
- **Data Persistence**: CSV-based storage with atomic writes and file locking
- **Automatic Backups**: Daily backups at 02:30 with 7-day retention

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
# Install application dependencies
pip install -r requirements.txt

# Install development/testing dependencies
pip install pytest pytest-cov
```

### 4. Configure Settings (Optional)

Edit `config.ini` to customize:
- Data and backup directories
- Check-in/check-out times
- Backup schedule and retention
- Service charge and tax rates

Default `config.ini`:
```ini
[paths]
data_dir = data
backup_dir = backups

[ops]
check_in_time = 14:00
check_out_time = 11:00
backup_time = 02:30
backup_retention_days = 7

[finance]
service_charge_rate = 0.10
tax_rate = 0.06
currency = MYR
```

### 5. Initialize Data

On first run, the application automatically creates:
- `data/rooms.csv` - Room inventory (edit to add your rooms)
- `data/reservations.csv` - Reservation records
- `backups/` - Backup directory

Sample `data/rooms.csv`:
```csv
room_id,room_type,base_price
101,Standard,120.00
102,Deluxe,180.00
103,Standard,120.00
104,Suite,250.00
```

## Usage

### Launch Application

```powershell
python run.py
```

Or using the virtual environment:
```powershell
.\.venv\Scripts\python.exe run.py
```

### User Interface

The application features a modern Tkinter UI with consistent theming, responsive layout, and clear user feedback.

**UI Highlights:**
- **Modern Theme**: ttk styling with accessible fonts (Segoe UI, 10pt)
- **Calendar Date Pickers**: All date fields feature interactive calendar dropdowns for easy date selection, reducing manual entry errors
- **Resizable Window**: Minimum 800×500, default 900×600; key widgets expand with window
- **Consistent Spacing**: 8px padding throughout for a clean, professional look
- **Input Validation**: Invalid date ranges (check-out before check-in) are automatically detected with clear error messages
- **Error Dialogs**: Clear error messages with links to `logs/app.log` for troubleshooting
- **Responsive Feedback**: Visual cues during operations

The application has four main tabs:

#### 1. Daily Ops
- View today's check-ins and check-outs
- Automatically applies status transitions based on current time
- Select any date to view scheduled operations

**How to use:**
1. Select or enter a date using the calendar dropdown (or type in YYYY-MM-DD format)
2. Click "Refresh" to update lists
3. View check-ins and check-outs for that date

#### 2. Reservations
- Create new reservations
- View all existing reservations
- Modify or cancel reservations

**Create a reservation:**
1. Enter guest details (name, phone, email)
2. Select check-in and check-out dates using the calendar dropdown widgets (or type dates in YYYY-MM-DD format)
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
2. Click "Cancel Selected"

#### 3. Availability
- Check room availability for a date range
- View all rooms and their status

**How to use:**
1. Enter start and end dates using the calendar dropdowns (or type in YYYY-MM-DD format)
2. Click "Check"
3. View which rooms are Available or Unavailable

#### 4. Reports
- Generate monthly revenue summaries

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
│   ├── billing.py          # Cost calculations (service + tax)
│   ├── config.py           # Configuration management
│   ├── reporting.py        # Daily/monthly reports
│   ├── reservations.py     # Reservation operations
│   ├── rooms.py            # Room inventory management
│   ├── storage.py          # CSV I/O, backups, locking
│   └── ui/
│       └── main.py         # Tkinter UI
├── data/
│   ├── rooms.csv           # Room inventory (static)
│   └── reservations.csv    # Reservation records (dynamic)
├── backups/                # Timestamped CSV backups
├── tests/                  # Pytest test suite (90% coverage)
├── config.ini              # Application configuration
├── run.py                  # Application entry point
└── openspec/               # OpenSpec documentation
```

### Design Principles

- **Simple Modular Structure**: Clear separation between business logic, storage, and UI
- **File-Based Storage**: CSV files with atomic writes and file locking
- **No External Dependencies**: Uses Python standard library (except pytest for testing)
- **Offline Operation**: No network or database required
- **Automatic Safety**: Status transitions, backups, and double-booking prevention

### Data Flow

1. **User Input** → UI (Tkinter)
2. **Business Logic** → Modules (reservations, rooms, billing, reporting)
3. **Storage** → CSV files with atomic writes
4. **Backups** → Scheduled daily copies with retention policy

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

- **22 tests** covering all core modules
- **90% overall coverage** (target: ≥70%)
- Modules: billing (100%), config (100%), rooms (100%), reservations (97%), storage (72%), reporting (100%)

### Test Categories

- **Unit Tests**: Billing calculations, date logic, CSV I/O
- **Integration Tests**: Reservation flows, backup operations
- **Edge Cases**: Double-booking, invalid dates, missing data

## Backup and Recovery

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

### CSV File Locked

**Problem**: File in use by another process
- **Solution**: Close the application and any CSV editors, then restart

### Missing Reservations

**Problem**: Data file corrupted
- **Solution**: Restore from `backups/` directory

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

### v1.0.0 (2025-10-24)
- Initial release
- Core reservation management
- Billing with service charge and tax
- Daily/monthly reporting
- Automatic backups
- 90% test coverage
