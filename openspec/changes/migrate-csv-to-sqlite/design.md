# Design: SQLite Migration

## Context
The hotel management system currently uses CSV files for data persistence with file-locking for concurrency control. This works for single-user scenarios but has limitations:
- No native transaction support (atomic writes simulated via temp files)
- No indexes (availability checks require full table scans)
- No schema enforcement (errors detected at runtime)
- File locking complexity and potential timeout issues

SQLite offers ACID transactions, indexed queries, and schema validation while maintaining single-file simplicity and zero external dependencies.

## Goals / Non-Goals

**Goals:**
- Replace CSV backend with SQLite while preserving all existing behavior
- Automatic migration from CSV→SQLite on first run (zero manual intervention)
- Maintain backward compatibility during transition (shim layer)
- Preserve CSV export capability for reporting/legacy needs
- Use only Python stdlib (no external dependencies)
- Improve query performance for availability checks via indexes

**Non-Goals:**
- Multi-user concurrent access (still single front-desk operator)
- Network/remote database support
- Advanced SQL features (views, triggers, stored procedures)
- Performance tuning beyond basic indexes
- Migration rollback mechanism (forward-only)

## Decisions

### Decision 1: Shim Layer Pattern
**Choice:** Implement `storage_sqlite.py` with same public API as current `storage.py` functions, then modify `storage.py` to import/re-export based on config flag.

**Alternatives Considered:**
- Direct replacement (modify storage.py in-place) → Rejected: harder to test both backends during transition
- Feature flag at call sites → Rejected: requires changes across entire codebase

**Rationale:** Shim pattern isolates changes, enables side-by-side testing, and provides rollback path if issues arise.

### Decision 2: Schema Design
**Rooms Table:**
```sql
CREATE TABLE rooms (
    room_id TEXT PRIMARY KEY,
    room_type TEXT NOT NULL,
    base_price REAL NOT NULL,
    image_path TEXT DEFAULT ''
);
```

**Reservations Table:**
```sql
CREATE TABLE reservations (
    id TEXT PRIMARY KEY,
    room_id TEXT NOT NULL,
    guest_name TEXT NOT NULL,
    guest_phone TEXT NOT NULL,
    guest_email TEXT NOT NULL,
    start_date TEXT NOT NULL,
    end_date TEXT NOT NULL,
    num_guests INTEGER NOT NULL,
    status TEXT NOT NULL,
    total_cost REAL NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    FOREIGN KEY (room_id) REFERENCES rooms(room_id)
);

CREATE INDEX idx_reservations_availability 
ON reservations(room_id, start_date, end_date);
```

**Alternatives Considered:**
- Numeric date storage (Julian days) → Rejected: ISO8601 text is human-readable and sortable
- Separate status table → Rejected: overkill for 4 fixed statuses

**Rationale:** Text dates preserve existing format, index supports fast availability queries, foreign key ensures referential integrity.

### Decision 3: Migration Strategy
**Choice:** On app startup, if `data/reservations.db` doesn't exist but CSV files do, automatically migrate and log to console.

**Alternatives Considered:**
- Manual migration script only → Rejected: adds friction for users
- Dual-mode (read from both) → Rejected: complex and error-prone
- Keep CSV as source of truth → Rejected: defeats purpose of migration

**Rationale:** Automatic migration ensures zero-downtime deployment and no manual steps.

### Decision 4: Transaction Handling
**Choice:** Wrap all write operations in explicit transactions with `BEGIN`/`COMMIT`, use `connection.row_factory = sqlite3.Row` for dict-like access.

**Rationale:** Explicit transactions ensure atomicity; Row factory maintains API compatibility with current CSV dict results.

### Decision 5: Backup Mechanism
**Choice:** Replace CSV file copies with atomic `.db` file copy using temp file + os.replace pattern (same as current CSV atomic writes).

**Rationale:** Maintains consistency with existing backup strategy; SQLite file is self-contained.

## Risks / Trade-offs

| Risk | Impact | Mitigation |
|------|--------|------------|
| Migration data loss | High | Thorough testing, validation logging, preserve original CSV files |
| SQLite file corruption | Medium | Regular backups, write-ahead logging (WAL mode) |
| Performance regression | Low | Indexed queries should be faster; load testing with ~20 rooms |
| Test failures during transition | Medium | Create parallel test suites, incremental migration |
| Users on old CSV data | Low | Migration runs automatically; add config flag to force re-migration |

## Migration Plan

### Phase 1: Implementation (Pre-Deployment)
1. Implement `app/storage_sqlite.py` with full API parity
2. Add unit tests for SQLite backend (temp DB per test)
3. Create standalone `scripts/migrate_csv_to_sqlite.py` with validation
4. Update `config.ini` schema and `app/rooms.py` config loading
5. Modify `app/storage.py` shim to check config flag

### Phase 2: Testing
1. Run full test suite with `use_sqlite=False` (baseline)
2. Run full test suite with `use_sqlite=True` (SQLite)
3. Test migration script against production-like CSV data
4. Validate backup/restore with SQLite files
5. Performance test availability queries with 100+ reservations

### Phase 3: Deployment
1. Update `config.ini` default to `use_sqlite=true`
2. On first app launch, migration runs automatically
3. Log migration results to console and `logs/app.log`
4. Original CSV files remain in `data/` (not deleted)
5. Future operations use SQLite exclusively

### Phase 4: Validation
1. Monitor logs for errors
2. Verify reservation creation/modification works
3. Confirm double-booking prevention still enforced
4. Validate daily/monthly reports generate correctly

### Rollback Plan
If critical issues arise:
1. Set `use_sqlite=false` in `config.ini`
2. Restart app (reverts to CSV backend)
3. Export current DB state to CSV via `export_csv()`
4. Investigate and fix SQLite issues offline

## Open Questions
1. ~~Should we enable WAL mode for better concurrency?~~ → YES, enable via `PRAGMA journal_mode=WAL`
2. ~~Should migration delete original CSV files?~~ → NO, preserve as backup/audit trail
3. ~~How to handle schema migrations in future?~~ → Add `schema_version` table, check on startup
4. ~~Should we add a `migrated_at` timestamp to DB?~~ → YES, add to schema_info table
