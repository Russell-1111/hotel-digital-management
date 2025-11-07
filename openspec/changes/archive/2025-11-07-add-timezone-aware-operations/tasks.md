# Implementation Tasks

## 1. Configuration and Dependencies
- [x] 1.1 Add `pytz` or use `zoneinfo` (stdlib in Python 3.9+) to `requirements.txt`
- [x] 1.2 Add `timezone` field to `AppConfig` dataclass in `app/rooms.py`
- [x] 1.3 Add `timezone = Asia/Kuala_Lumpur` to `[ops]` section in `config.ini`
- [x] 1.4 Update config loader to parse and validate timezone string (handle invalid timezone gracefully)

## 2. Core Timezone Utilities
- [x] 2.1 Create `app/timezone_utils.py` with helper functions:
  - [x] `get_hotel_tz(tz_name: str) -> tzinfo` - load configured timezone
  - [x] `now_utc() -> datetime` - current time in UTC (aware)
  - [x] `now_hotel(tz: tzinfo) -> datetime` - current time in hotel timezone (aware)
  - [x] `to_utc(dt: datetime, tz: tzinfo) -> datetime` - convert hotel local to UTC
  - [x] `to_hotel_tz(dt_utc: datetime, tz: tzinfo) -> datetime` - convert UTC to hotel local
  - [x] `naive_to_aware_utc(naive_dt: datetime, assume_tz: tzinfo) -> datetime` - migration helper

## 3. Update Reservation Module
- [x] 3.1 Replace `datetime.now()` with `now_utc()` in `create_reservation()` for `created_at`/`updated_at`
- [x] 3.2 Replace `datetime.now()` with `now_utc()` in `modify_reservation()` for `updated_at`
- [x] 3.3 Replace `datetime.now()` with `now_utc()` in `cancel_reservation()` for `updated_at`
- [x] 3.4 Update `auto_status_transitions()`:
  - [x] Accept hotel timezone parameter
  - [x] Convert `local_now` parameter to timezone-aware (or compute from `now_hotel(tz)`)
  - [x] Build check-in/check-out datetime with hotel timezone, then compare in UTC
- [x] 3.5 Update `_parse_date()` to return timezone-aware datetime at midnight in hotel timezone

## 4. Update Storage Module (CSV Backend)
- [x] 4.1 Update `_parse_time()` in `storage.py`:
  - [x] Accept hotel timezone parameter
  - [x] Compute next occurrence as timezone-aware datetime in hotel timezone
  - [x] Return UTC timestamp for scheduler comparison
- [x] 4.2 Update `start_daily_backup_scheduler()`:
  - [x] Load hotel timezone from config
  - [x] Pass timezone to `_parse_time()`
  - [x] Use `now_utc()` for sleep calculation
- [x] 4.3 Update backup cleanup logic to use `datetime.now(timezone.utc).astimezone(tz)` for cutoff calculation

## 5. Update Storage Module (SQLite Backend)
- [x] 5.1 Replace all `datetime.now()` calls with `now_utc()` in `storage_sqlite.py`
- [x] 5.2 Ensure ISO 8601 timestamps include timezone marker (e.g., `2025-11-07T10:30:00Z`)
- [x] 5.3 Update backup scheduler to use hotel timezone (same as 4.2)
- [x] 5.4 Add migration function `migrate_naive_timestamps_to_utc()`:
  - [x] Scan all `created_at`/`updated_at` fields in reservations table
  - [x] If timestamp lacks timezone marker, assume it's in hotel's local timezone
  - [x] Convert to UTC and update with `Z` suffix
  - [x] Log migration summary (number of records migrated)
  - [x] Store migration completion flag in `schema_info` or app metadata table

## 6. Update Reporting Module
- [x] 6.1 Update `daily_checkin_list()` and `daily_checkout_list()`:
  - [x] Accept hotel timezone parameter
  - [x] Convert date strings to timezone-aware datetime for accurate filtering
- [x] 6.2 Update `compute_nights()` to handle timezone-aware dates correctly (use `.date()` for day count)

## 7. Update UI Module
- [x] 7.1 Update `app/ui/main.py` to pass hotel timezone to backend operations
- [x] 7.2 Update UI status check to use `now_hotel(tz)` for display of current hotel time
- [x] 7.3 Ensure date pickers interpret dates as midnight in hotel timezone (not UTC)
- [x] 7.4 Add optional timezone display in UI footer or settings (e.g., "Hotel time: Asia/Kuala_Lumpur")

## 8. Testing
- [x] 8.1 Update `tests/test_config.py` to validate timezone field parsing
- [x] 8.2 Update `tests/test_reservations.py`:
  - [x] Create timezone-aware test fixtures
  - [x] Test status transitions across timezone boundaries
  - [x] Test DST transition handling (if applicable to configured timezone)
- [x] 8.3 Update `tests/test_storage.py` and `tests/test_storage_sqlite.py`:
  - [x] Test `_parse_time()` with various timezones
  - [x] Test backup scheduler with non-UTC timezone
- [x] 8.4 Create `tests/test_timezone_utils.py`:
  - [x] Test UTC ↔ hotel timezone conversions
  - [x] Test naive → aware migration helper
  - [x] Test invalid timezone handling
- [x] 8.5 Run full test suite and ensure all datetime-related tests pass

## 9. Documentation
- [x] 9.1 Update `README.md` with timezone configuration instructions
- [x] 9.2 Update `QUICKSTART.md` to mention timezone setting
- [x] 9.3 Add migration guide for users upgrading from naive to timezone-aware version (documented in README and automated in code)
- [x] 9.4 Document timezone field in `config.ini` with examples and IANA timezone list reference

## 10. Validation and Deployment
- [x] 10.1 Test with different timezones (e.g., `UTC`, `America/New_York`, `Asia/Tokyo`)
- [x] 10.2 Verify backup scheduler triggers at correct local time regardless of server timezone
- [x] 10.3 Verify check-in/check-out transitions happen at configured hotel times
- [x] 10.4 Test migration on sample database with naive timestamps
- [x] 10.5 Run coverage report and ensure ≥70% coverage maintained (73% achieved)
