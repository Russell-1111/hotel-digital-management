# Change Proposal: Add Timezone-Aware Operations

## Why
The system currently uses naive datetime objects and implicit "local time" assumptions throughout. This creates portability issues if the hotel operates across timezones, the server is relocated, or during daylight saving time transitions. Timestamps stored in the database lack timezone information, making historical data ambiguous. Scheduled operations (check-in/check-out transitions, backups) assume server local time without explicit configuration, which can cause unexpected behavior in deployment environments with different timezone settings.

## What Changes
- Add timezone configuration to `config.ini` with hotel's operational timezone (e.g., `Asia/Kuala_Lumpur`)
- Convert all datetime operations to use timezone-aware objects (Python `datetime` with `tzinfo`)
- Store all timestamps in UTC with explicit timezone marker (ISO 8601 format with `Z` suffix or offset)
- Update check-in/check-out/backup schedulers to use configured hotel timezone for local time calculations
- Add `pytz` or `zoneinfo` (Python 3.9+) dependency for IANA timezone support
- Migrate existing naive timestamps in database to UTC format during application startup
- Preserve backward compatibility: display times to users in hotel's local timezone while storing in UTC

## Impact
- Affected specs: `reservations`, `storage`
- Affected code:
  - `app/reservations.py`: `create_reservation()`, `modify_reservation()`, `cancel_reservation()`, `auto_status_transitions()`
  - `app/storage.py`: `_parse_time()`, `start_daily_backup_scheduler()`, backup cleanup logic
  - `app/storage_sqlite.py`: timestamp generation and migration logic
  - `app/reporting.py`: date filtering and timestamp display
  - `app/ui/main.py`: datetime parsing and display formatting
  - `app/rooms.py`: `AppConfig` dataclass - add `timezone` field
  - `config.ini`: new `[ops]` entry: `timezone = Asia/Kuala_Lumpur`
  - `requirements.txt`: add timezone library dependency
- Migration strategy: One-time automatic migration on first startup with new version; convert all existing `created_at`/`updated_at` timestamps from naive to UTC
- Testing: Update all timestamp-related tests to use timezone-aware fixtures
