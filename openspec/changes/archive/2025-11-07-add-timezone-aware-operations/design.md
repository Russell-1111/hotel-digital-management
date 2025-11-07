# Design: Timezone-Aware Operations

## Context
The hotel management system currently uses naive `datetime` objects throughout the codebase. All timestamps are implicitly treated as "local time" without explicit timezone information. This creates several issues:
- **Portability**: System behavior depends on server's OS timezone setting
- **Ambiguity**: Historical timestamps don't record which timezone they were created in
- **DST transitions**: Status transitions and backups may fire at unexpected times during DST changes
- **Multi-location deployment**: Cannot accurately handle hotels in different timezones with a single codebase

The system is deployed on Windows desktop machines at the hotel front desk. The hotel operates in a single timezone (Kuala Lumpur, Malaysia = `Asia/Kuala_Lumpur`, UTC+8 year-round, no DST).

## Goals / Non-Goals

**Goals:**
- Store all timestamps in UTC with explicit timezone markers (ISO 8601 compliant)
- Allow hotel to configure operational timezone independently of server OS timezone
- Make scheduled operations (check-in/check-out transitions, backups) trigger at correct local hotel time regardless of server timezone
- Migrate existing naive timestamps without data loss
- Maintain backward compatibility: users see times in hotel's local timezone

**Non-Goals:**
- Multi-timezone support for a single hotel (hotel operates in one timezone only)
- User-specific timezones (front desk staff work in hotel's timezone)
- Timezone selection UI (configured via `config.ini` once during setup)
- Support for very old Python versions without `zoneinfo` (require Python 3.9+)

## Decisions

### 1. Use Python 3.9+ `zoneinfo` (not `pytz`)
**Decision**: Use standard library `zoneinfo` module for timezone handling.

**Rationale**:
- `zoneinfo` is built into Python 3.9+ (no external dependency)
- Simpler API than `pytz` (no `localize()` vs `replace()` confusion)
- Official replacement for `pytz` in modern Python
- Accesses system IANA timezone database (always up-to-date on Windows via `tzdata` fallback package)

**Alternative considered**: `pytz` library
- Pro: Works on older Python versions
- Con: More complex API; external dependency; deprecated in favor of `zoneinfo`
- Rejected because project already requires Python 3.x and can mandate 3.9+

**Implementation**:
```python
from zoneinfo import ZoneInfo, available_timezones
import datetime

# Load hotel timezone from config
hotel_tz = ZoneInfo("Asia/Kuala_Lumpur")

# Get current time in UTC
now_utc = datetime.datetime.now(datetime.timezone.utc)

# Convert to hotel timezone
now_hotel = now_utc.astimezone(hotel_tz)
```

### 2. Store Timestamps in UTC, Display in Hotel Timezone
**Decision**: All timestamps in database and CSV files use UTC with ISO 8601 format (`YYYY-MM-DDTHH:MM:SSZ`). UI displays times converted to hotel's local timezone.

**Rationale**:
- UTC is unambiguous (no DST transitions, no offset changes)
- Industry best practice for distributed systems
- Simplifies debugging (logs, database queries use single reference frame)
- Easy conversion to any display timezone

**Alternative considered**: Store in hotel's local timezone
- Pro: Simpler for single-timezone deployment
- Con: Ambiguous during DST transitions; requires re-interpreting if hotel relocates
- Rejected because UTC storage is more robust long-term

**Implementation**:
- Update `created_at`/`updated_at` generation: `datetime.datetime.now(datetime.timezone.utc).isoformat()`
- Update UI datetime parsing: interpret user input as hotel local time, convert to UTC before storage
- Add display helper: `utc_to_hotel_display(utc_timestamp: str, tz: ZoneInfo) -> str`

### 3. Configuration via `config.ini` with Validation
**Decision**: Add `timezone = Asia/Kuala_Lumpur` to `[ops]` section in `config.ini`. Validate on startup; fail gracefully with clear error message if invalid.

**Rationale**:
- Follows existing configuration pattern (all operational settings in `[ops]`)
- IANA timezone names are standard, human-readable, and OS-agnostic
- Validation prevents silent errors from typos

**Alternative considered**: Auto-detect server timezone
- Pro: No configuration needed
- Con: Server timezone may not match hotel location; makes behavior implicit and unpredictable
- Rejected because explicit configuration is more reliable

**Implementation**:
```python
# In rooms.py AppConfig
timezone: str  # IANA timezone name (e.g., "Asia/Kuala_Lumpur")

# In config loader
try:
    tz = ZoneInfo(config["ops"]["timezone"])
except ZoneInfoNotFoundError:
    raise ValueError(f"Invalid timezone: {config['ops']['timezone']}. See https://en.wikipedia.org/wiki/List_of_tz_database_time_zones")
```

### 4. Automatic Migration of Naive Timestamps
**Decision**: On first startup with new version, automatically detect naive timestamps in database and migrate to UTC. Assume naive timestamps were created in hotel's configured timezone.

**Rationale**:
- Avoids manual migration step for users
- Timestamps without timezone info are interpreted in hotel's operational timezone (reasonable assumption)
- One-time operation, minimal performance impact

**Alternative considered**: Manual migration script
- Pro: More control, no assumptions
- Con: Requires user intervention, risk of data loss if user forgets to run script
- Rejected because automatic migration is safer for single-hotel deployment

**Implementation**:
- Add migration flag to `schema_info` table: `naive_timestamp_migration_completed BOOLEAN DEFAULT 0`
- On startup, check flag; if not set:
  - Query all `created_at`/`updated_at` fields
  - Parse timestamps; if they lack timezone info, assume they're in hotel timezone
  - Convert to UTC and update records
  - Set migration flag to 1
- Log migration summary: "Migrated 42 naive timestamps to UTC"

### 5. Scheduler Uses Hotel Timezone for Local Time
**Decision**: Backup scheduler and status transition scheduler interpret configured times (02:30, 14:00, 11:00) as hotel local time, but compute next run time in UTC.

**Rationale**:
- Hotel operations should follow hotel's local clock, not server's local clock
- Schedulers work correctly even if server is in different timezone or moves between timezones

**Implementation**:
```python
def _parse_time(hhmm: str, hotel_tz: ZoneInfo) -> datetime:
    """Parse HH:MM as next occurrence in hotel timezone, return as UTC."""
    now_utc = datetime.datetime.now(datetime.timezone.utc)
    now_hotel = now_utc.astimezone(hotel_tz)
    
    hour, minute = map(int, hhmm.split(':'))
    target_hotel = now_hotel.replace(hour=hour, minute=minute, second=0, microsecond=0)
    if target_hotel <= now_hotel:
        target_hotel += datetime.timedelta(days=1)
    
    return target_hotel.astimezone(datetime.timezone.utc)
```

### 6. Date-Only Fields Remain Timezone-Naive
**Decision**: `check_in_date` and `check_out_date` fields remain as date-only strings (`YYYY-MM-DD`) without time or timezone information. Status transitions combine date with configured time and timezone.

**Rationale**:
- Check-in/check-out dates are conceptual dates in hotel's local calendar, not specific instants in time
- Simpler for users: "I want to book Nov 10-12" is clearer than "I want to book 2025-11-10T00:00:00+08:00 to 2025-11-12T00:00:00+08:00"
- Time component (14:00, 11:00) comes from configuration, applied uniformly

**Implementation**:
- Keep `check_in_date`/`check_out_date` as `YYYY-MM-DD` strings
- In `auto_status_transitions()`, combine date string with configured time and hotel timezone:
  ```python
  check_in_dt = datetime.datetime.strptime(reservation.check_in_date, "%Y-%m-%d").replace(
      hour=14, minute=0, tzinfo=hotel_tz
  )
  ```

## Risks / Trade-offs

### Risk 1: Python 3.9+ Requirement
**Mitigation**: Document minimum Python version in README and `requirements.txt`. Current project likely already uses 3.9+ (released Oct 2020, nearly 5 years old).

### Risk 2: Migration Assumptions May Be Wrong
**Scenario**: Existing naive timestamps were not actually in hotel's timezone (e.g., if someone tested with server in different timezone).
**Mitigation**:
- Log migration warnings if timestamps are far in the past or future (likely anomalies)
- Keep CSV/database backup before migration (handled by existing backup system)
- Provide manual override flag in `config.ini` for migration timezone if needed: `migration_source_timezone = UTC` (default: use `timezone` value)

### Risk 3: Performance Impact of Timezone Conversions
**Assessment**: Negligible. Timezone conversions are cheap (arithmetic + lookup). Hotel has ~20 rooms, dozens of operations per day.
**Mitigation**: Profile if concerns arise, but unlikely to be measurable.

### Trade-off: Display Complexity
**Trade-off**: UI code becomes slightly more complex (must convert UTC → hotel timezone for display).
**Acceptance**: This is standard practice in any multi-timezone system. Complexity is localized to display layer, doesn't affect core business logic.

## Migration Plan

### Pre-Migration (Before Upgrade)
1. System automatically creates daily backups (existing feature)
2. No user action required

### During First Startup with New Version
1. Application detects `naive_timestamp_migration_completed = 0` in metadata
2. Reads all reservations with `created_at`/`updated_at` timestamps
3. For each timestamp:
   - Try parsing as ISO 8601 with timezone
   - If timezone is missing, assume timestamp is in hotel's configured timezone
   - Convert to UTC and format as `YYYY-MM-DDTHH:MM:SSZ`
   - Update record
4. Set `naive_timestamp_migration_completed = 1`
5. Log summary: "Timezone migration complete: 42 timestamps migrated from Asia/Kuala_Lumpur to UTC"

### Post-Migration
- All new timestamps generated in UTC
- UI displays times in hotel's local timezone
- Schedulers use hotel timezone for next-run calculations

### Rollback (If Needed)
1. Restore from backup taken before upgrade
2. Downgrade to previous version
3. System reverts to naive datetime behavior

## Open Questions

1. **Q**: Should we display timezone abbreviation in UI (e.g., "14:00 MYT")?
   **A**: Optional enhancement; defer to UI implementation phase. Most users don't need to see timezone (they know they're in Malaysia).

2. **Q**: What if hotel relocates to different timezone?
   **A**: Update `timezone` in `config.ini`. All future operations use new timezone. Historical timestamps remain in UTC, so they're still valid. No migration needed.

3. **Q**: How to handle invalid timezone in config?
   **A**: Application fails to start with clear error message directing user to fix `config.ini`. List example valid timezones in error message.

4. **Q**: Should we use `tzdata` package as fallback for Windows?
   **A**: Yes, add `tzdata` to `requirements.txt`. It's required on Windows for `zoneinfo` to access IANA database. No-op on Linux/macOS (they have system timezone data).
