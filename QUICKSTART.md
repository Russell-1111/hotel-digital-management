# Hotel Digital Management System - Quick Start

## Installation (5 minutes)

1. **Set up Python environment:**
   ```powershell
   cd hotel_digital_management
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```

2. **Run the application:**
   ```powershell
   python run.py
   ```

3. **Customize room inventory:**
   Edit `data/rooms.csv` to add your hotel rooms.

## Quick Reference

### Create a Reservation
1. Go to **Reservations** tab
2. Enter guest details and dates
3. Click "Check Availability"
4. Select room → "Create Reservation"

### Check Daily Operations
1. Go to **Daily Ops** tab
2. Select date → "Refresh"
3. View today's check-ins and check-outs

### Generate Revenue Report
1. Go to **Reports** tab
2. Enter month (YYYY-MM)
3. Click "Compute Revenue"

## Key Files

- `config.ini` - Settings (times, rates, directories, timezone)
- `data/rooms.csv` - Room inventory (edit to add rooms)
- `data/reservations.csv` - Reservation records (auto-managed)
- `backups/` - Daily backups (auto at 02:30 hotel time)

**Important**: The `timezone` setting in `config.ini` must be a valid IANA timezone name (e.g., `Asia/Kuala_Lumpur`). See [List of tz database time zones](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones).

## Billing Formula

```
Total = Room Cost + 10% Service + 6% Tax (MYR)
```

Example: 2 nights @ 100 MYR = 233.20 MYR total

## Testing

```powershell
# Run all tests
python -m pytest tests/ -v

# Check coverage (should be ~90%)
python -m pytest tests/ --cov=app
```

## Need Help?

See `README.md` for full documentation.
