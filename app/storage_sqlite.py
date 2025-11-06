"""
SQLite-based storage backend for Hotel Digital Management System.

This module provides ACID-compliant data persistence using SQLite, replacing the
CSV-based storage while maintaining API compatibility. All write operations are
wrapped in explicit transactions to ensure atomicity and consistency.

Key Features:
- Automatic schema initialization with indexes for performance
- Transactional writes with parameterized SQL (injection-safe)
- Automatic CSV→SQLite migration on first run
- WAL (Write-Ahead Logging) mode for better concurrency
- Foreign key constraints for referential integrity
"""

from __future__ import annotations
import csv
import logging
import os
import shutil
import sqlite3
import tempfile
from contextlib import contextmanager
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional, Tuple

from .rooms import AppConfig

logger = logging.getLogger(__name__)

# Database schema version for future migrations
SCHEMA_VERSION = 1


@contextmanager
def get_connection(db_path: Path):
    """
    Create a database connection with proper configuration.
    
    Args:
        db_path: Path to SQLite database file
        
    Yields:
        sqlite3.Connection: Configured database connection
        
    Notes:
        - Enables foreign key constraints
        - Sets WAL (Write-Ahead Logging) mode for better concurrency
        - Uses Row factory for dict-like access to results
        - Automatically commits on success, rolls back on exception
    """
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row  # Enable dict-like access
    conn.execute("PRAGMA foreign_keys = ON")  # Enforce FK constraints
    conn.execute("PRAGMA journal_mode = WAL")  # Enable WAL mode
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_schema(conn: sqlite3.Connection) -> None:
    """
    Initialize database schema with all required tables and indexes.
    
    Args:
        conn: Active database connection
        
    Creates:
        - schema_info table: tracks schema version and migration timestamp
        - rooms table: room inventory with pricing
        - reservations table: guest reservations with status tracking
        - idx_reservations_availability: index for fast availability queries
        
    Transaction Handling:
        Caller is responsible for transaction management (BEGIN/COMMIT)
    """
    # Schema metadata table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS schema_info (
            version INTEGER PRIMARY KEY,
            migrated_at TEXT NOT NULL
        )
    """)
    
    # Rooms table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS rooms (
            room_id TEXT PRIMARY KEY,
            room_type TEXT NOT NULL,
            base_price REAL NOT NULL,
            image_path TEXT DEFAULT ''
        )
    """)
    
    # Reservations table with foreign key to rooms
    conn.execute("""
        CREATE TABLE IF NOT EXISTS reservations (
            id TEXT PRIMARY KEY,
            room_id TEXT NOT NULL,
            guest_name TEXT NOT NULL,
            guest_phone TEXT NOT NULL,
            guest_email TEXT NOT NULL,
            start_date TEXT NOT NULL,
            end_date TEXT NOT NULL,
            num_guests INTEGER NOT NULL,
            status TEXT NOT NULL CHECK(status IN ('Confirmed', 'Cancelled', 'Checked-In', 'Checked-Out')),
            total_cost REAL NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            FOREIGN KEY (room_id) REFERENCES rooms(room_id)
        )
    """)
    
    # Index for fast availability lookups (critical for double-booking prevention)
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_reservations_availability
        ON reservations(room_id, start_date, end_date)
    """)
    
    # Record schema version
    conn.execute("""
        INSERT OR REPLACE INTO schema_info (version, migrated_at)
        VALUES (?, ?)
    """, (SCHEMA_VERSION, datetime.now().isoformat()))
    
    logger.info(f"Database schema initialized (version {SCHEMA_VERSION})")


def ensure_db(cfg: AppConfig) -> Path:
    """
    Ensure database exists and is properly initialized.
    
    Args:
        cfg: Application configuration
        
    Returns:
        Path to the database file
        
    Side Effects:
        - Creates data directory if missing
        - Initializes schema if database is new
        - Triggers CSV migration if CSV files exist but DB doesn't
        
    Migration Logic:
        1. If reservations.db exists → return path
        2. If reservations.db missing but CSVs exist → migrate CSVs to DB
        3. If both missing → create empty DB with schema
    """
    cfg.data_dir.mkdir(parents=True, exist_ok=True)
    db_path = cfg.data_dir / 'reservations.db'
    
    # Check if we need to migrate from CSV
    csv_rooms = cfg.data_dir / 'rooms.csv'
    csv_reservations = cfg.data_dir / 'reservations.csv'
    needs_migration = (
        not db_path.exists() and 
        csv_rooms.exists() and 
        csv_reservations.exists()
    )
    
    if needs_migration:
        logger.info("Detected CSV files without database - starting migration...")
        migrate_from_csv(cfg, db_path)
    elif not db_path.exists():
        # Create new empty database
        logger.info(f"Creating new database at {db_path}")
        with get_connection(db_path) as conn:
            init_schema(conn)
    
    return db_path


def migrate_from_csv(cfg: AppConfig, db_path: Path) -> None:
    """
    Migrate data from CSV files to SQLite database.
    
    Args:
        cfg: Application configuration
        db_path: Target database path
        
    Side Effects:
        - Creates new SQLite database
        - Preserves original CSV files (does not delete)
        - Logs migration summary to console and file
        
    Transaction Handling:
        Entire migration runs in a single transaction - either all data migrates
        or none (rollback on any error)
        
    Error Handling:
        - Invalid data rows are logged and skipped
        - Critical errors (schema creation) abort migration and clean up partial DB
        - Original CSV files are never modified
    """
    csv_rooms = cfg.data_dir / 'rooms.csv'
    csv_reservations = cfg.data_dir / 'reservations.csv'
    
    logger.info("=" * 60)
    logger.info("CSV TO SQLITE MIGRATION")
    logger.info("=" * 60)
    
    try:
        with get_connection(db_path) as conn:
            # Initialize schema within transaction
            init_schema(conn)
            
            # Migrate rooms
            rooms_migrated = 0
            logger.info(f"Reading rooms from {csv_rooms}")
            with csv_rooms.open('r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    try:
                        conn.execute("""
                            INSERT INTO rooms (room_id, room_type, base_price, image_path)
                            VALUES (?, ?, ?, ?)
                        """, (
                            row['room_id'],
                            row['room_type'],
                            float(row['base_price']),
                            row.get('image_path', '')
                        ))
                        rooms_migrated += 1
                    except Exception as e:
                        logger.warning(f"Skipping invalid room row: {row} - Error: {e}")
            
            logger.info(f"✓ Migrated {rooms_migrated} rooms")
            
            # Migrate reservations
            reservations_migrated = 0
            logger.info(f"Reading reservations from {csv_reservations}")
            with csv_reservations.open('r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    try:
                        conn.execute("""
                            INSERT INTO reservations (
                                id, room_id, guest_name, guest_phone, guest_email,
                                start_date, end_date, num_guests, status,
                                total_cost, created_at, updated_at
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            row['reservation_id'],
                            row['room_id'],
                            row['guest_name'],
                            row['phone'],
                            row['email'],
                            row['check_in_date'],
                            row['check_out_date'],
                            int(row['num_guests']),
                            row['status'],
                            float(row['total_cost']),
                            row['created_at'],
                            row['updated_at']
                        ))
                        reservations_migrated += 1
                    except Exception as e:
                        logger.warning(f"Skipping invalid reservation row: {row} - Error: {e}")
            
            logger.info(f"✓ Migrated {reservations_migrated} reservations")
            
            # Record migration timestamp
            conn.execute("""
                UPDATE schema_info SET migrated_at = ?
            """, (datetime.now().isoformat(),))
            
        # Migration successful - log summary
        logger.info("=" * 60)
        logger.info(f"MIGRATION COMPLETE")
        logger.info(f"  Rooms: {rooms_migrated}")
        logger.info(f"  Reservations: {reservations_migrated}")
        logger.info(f"  Database: {db_path}")
        logger.info(f"  Original CSV files preserved in {cfg.data_dir}")
        logger.info("=" * 60)
        
        # Print to console as well
        print(f"\n✓ Migration complete: {rooms_migrated} rooms, {reservations_migrated} reservations")
        print(f"  Database created at: {db_path}")
        print(f"  Original CSV files preserved\n")
        
    except Exception as e:
        logger.error(f"Migration failed: {e}", exc_info=True)
        # Clean up partial database
        if db_path.exists():
            db_path.unlink()
        raise RuntimeError(f"CSV migration failed: {e}") from e


def read_rooms(cfg: AppConfig) -> List[Dict[str, any]]:
    """
    Read all rooms from database.
    
    Args:
        cfg: Application configuration
        
    Returns:
        List of room dictionaries with keys: room_id, room_type, base_price, image_path
        
    Notes:
        - Returns empty list if no rooms exist
        - Results are ordered by room_id for consistency
    """
    db_path = ensure_db(cfg)
    with get_connection(db_path) as conn:
        cursor = conn.execute("""
            SELECT room_id, room_type, base_price, image_path
            FROM rooms
            ORDER BY room_id
        """)
        return [dict(row) for row in cursor.fetchall()]


def read_reservations(cfg: AppConfig, date_range: Optional[Tuple[str, str]] = None) -> List[Dict[str, any]]:
    """
    Read reservations from database, optionally filtered by date range.
    
    Args:
        cfg: Application configuration
        date_range: Optional tuple of (start_date, end_date) in YYYY-MM-DD format
                   Returns reservations overlapping this range
        
    Returns:
        List of reservation dictionaries with keys matching reservation schema
        
    Notes:
        - Returns all reservations if date_range is None
        - Results ordered by start_date, then created_at
        - Date range filter uses indexed query for performance
    """
    db_path = ensure_db(cfg)
    with get_connection(db_path) as conn:
        if date_range:
            start, end = date_range
            # Find reservations overlapping the date range using indexed query
            cursor = conn.execute("""
                SELECT id, room_id, guest_name, guest_phone, guest_email,
                       start_date, end_date, num_guests, status,
                       total_cost, created_at, updated_at
                FROM reservations
                WHERE room_id IN (SELECT DISTINCT room_id FROM reservations)
                  AND start_date < ?
                  AND end_date > ?
                ORDER BY start_date, created_at
            """, (end, start))
        else:
            cursor = conn.execute("""
                SELECT id, room_id, guest_name, guest_phone, guest_email,
                       start_date, end_date, num_guests, status,
                       total_cost, created_at, updated_at
                FROM reservations
                ORDER BY start_date, created_at
            """)
        
        return [dict(row) for row in cursor.fetchall()]


def write_reservation(cfg: AppConfig, reservation: Dict[str, any]) -> bool:
    """
    Create a new reservation in the database.
    
    Args:
        cfg: Application configuration
        reservation: Reservation dictionary with required fields
        
    Returns:
        True if successful, False otherwise
        
    Transaction Handling:
        - Entire operation wrapped in transaction (atomic)
        - Validates room availability within transaction (prevents race conditions)
        - Rolls back automatically on any error
        
    Required Fields in reservation dict:
        id, room_id, guest_name, guest_phone, guest_email,
        start_date, end_date, num_guests, status,
        total_cost, created_at, updated_at
    """
    db_path = ensure_db(cfg)
    
    try:
        with get_connection(db_path) as conn:
            # Validate room availability within transaction
            overlaps = conn.execute("""
                SELECT COUNT(*) as count
                FROM reservations
                WHERE room_id = ?
                  AND status NOT IN ('Cancelled', 'Checked-Out')
                  AND start_date < ?
                  AND end_date > ?
            """, (
                reservation['room_id'],
                reservation['end_date'],
                reservation['start_date']
            )).fetchone()
            
            if overlaps['count'] > 0:
                logger.warning(f"Room {reservation['room_id']} not available for {reservation['start_date']} to {reservation['end_date']}")
                return False
            
            # Insert reservation using parameterized SQL (injection-safe)
            conn.execute("""
                INSERT INTO reservations (
                    id, room_id, guest_name, guest_phone, guest_email,
                    start_date, end_date, num_guests, status,
                    total_cost, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                reservation['id'],
                reservation['room_id'],
                reservation['guest_name'],
                reservation['guest_phone'],
                reservation['guest_email'],
                reservation['start_date'],
                reservation['end_date'],
                reservation['num_guests'],
                reservation['status'],
                reservation['total_cost'],
                reservation['created_at'],
                reservation['updated_at']
            ))
            
        logger.info(f"Created reservation {reservation['id']} for room {reservation['room_id']}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to create reservation: {e}", exc_info=True)
        return False


def update_reservation(cfg: AppConfig, reservation_id: str, updates: Dict[str, any]) -> bool:
    """
    Update an existing reservation.
    
    Args:
        cfg: Application configuration
        reservation_id: ID of reservation to update
        updates: Dictionary of fields to update (subset of reservation fields)
        
    Returns:
        True if successful, False if reservation not found or update failed
        
    Transaction Handling:
        - Entire operation wrapped in transaction
        - Re-validates availability if room_id or dates change
        - Automatically updates updated_at timestamp
        
    Common update fields:
        room_id, guest_name, guest_phone, guest_email,
        start_date, end_date, num_guests, status, total_cost
    """
    db_path = ensure_db(cfg)
    
    try:
        with get_connection(db_path) as conn:
            # Check if reservation exists
            existing = conn.execute("""
                SELECT * FROM reservations WHERE id = ?
            """, (reservation_id,)).fetchone()
            
            if not existing:
                logger.warning(f"Reservation {reservation_id} not found")
                return False
            
            # If changing room or dates, re-validate availability
            room_changed = 'room_id' in updates
            dates_changed = 'start_date' in updates or 'end_date' in updates
            
            if room_changed or dates_changed:
                check_room = updates.get('room_id', existing['room_id'])
                check_start = updates.get('start_date', existing['start_date'])
                check_end = updates.get('end_date', existing['end_date'])
                
                # Check for overlaps excluding this reservation
                overlaps = conn.execute("""
                    SELECT COUNT(*) as count
                    FROM reservations
                    WHERE room_id = ?
                      AND id != ?
                      AND status NOT IN ('Cancelled', 'Checked-Out')
                      AND start_date < ?
                      AND end_date > ?
                """, (check_room, reservation_id, check_end, check_start)).fetchone()
                
                if overlaps['count'] > 0:
                    logger.warning(f"Room {check_room} not available for updated dates")
                    return False
            
            # Build UPDATE query dynamically based on provided fields
            updates['updated_at'] = datetime.now().isoformat()
            
            set_clause = ', '.join([f"{key} = ?" for key in updates.keys()])
            values = list(updates.values()) + [reservation_id]
            
            conn.execute(f"""
                UPDATE reservations
                SET {set_clause}
                WHERE id = ?
            """, values)
            
        logger.info(f"Updated reservation {reservation_id}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to update reservation {reservation_id}: {e}", exc_info=True)
        return False


def is_room_available(cfg: AppConfig, room_id: str, start_date: str, end_date: str, exclude_id: Optional[str] = None) -> bool:
    """
    Check if a room is available for a given date range.
    
    Args:
        cfg: Application configuration
        room_id: Room identifier
        start_date: Check-in date (YYYY-MM-DD)
        end_date: Check-out date (YYYY-MM-DD)
        exclude_id: Optional reservation ID to exclude from check (for modifications)
        
    Returns:
        True if room is available, False if conflicts exist
        
    Notes:
        - Uses indexed query (idx_reservations_availability) for O(log n) performance
        - Excludes cancelled and checked-out reservations
        - Overlap logic: new_start < existing_end AND new_end > existing_start
    """
    db_path = ensure_db(cfg)
    
    with get_connection(db_path) as conn:
        if exclude_id:
            cursor = conn.execute("""
                SELECT COUNT(*) as count
                FROM reservations
                WHERE room_id = ?
                  AND id != ?
                  AND status NOT IN ('Cancelled', 'Checked-Out')
                  AND start_date < ?
                  AND end_date > ?
            """, (room_id, exclude_id, end_date, start_date))
        else:
            cursor = conn.execute("""
                SELECT COUNT(*) as count
                FROM reservations
                WHERE room_id = ?
                  AND status NOT IN ('Cancelled', 'Checked-Out')
                  AND start_date < ?
                  AND end_date > ?
            """, (room_id, end_date, start_date))
        
        result = cursor.fetchone()
        return result['count'] == 0


def backup_db(cfg: AppConfig) -> None:
    """
    Create atomic backup of SQLite database.
    
    Args:
        cfg: Application configuration
        
    Side Effects:
        - Creates timestamped backup in backup_dir
        - Performs checkpoint to consolidate WAL before backup
        - Cleans up backups older than retention period
        
    Backup Strategy:
        1. Checkpoint WAL to consolidate all changes into main DB file
        2. Copy main DB file atomically (temp file + rename)
        3. Clean up old backups based on retention policy
        
    Notes:
        - Backup includes only the main .db file (WAL/SHM consolidated)
        - Uses same atomic pattern as CSV backups (temp + replace)
    """
    cfg.backup_dir.mkdir(parents=True, exist_ok=True)
    db_path = ensure_db(cfg)
    
    if not db_path.exists():
        logger.warning("Database file does not exist, skipping backup")
        return
    
    # Checkpoint WAL to consolidate changes
    try:
        with get_connection(db_path) as conn:
            conn.execute("PRAGMA wal_checkpoint(TRUNCATE)")
        logger.debug("WAL checkpoint completed")
    except Exception as e:
        logger.warning(f"WAL checkpoint failed (continuing with backup): {e}")
    
    # Create timestamped backup
    timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
    backup_name = f"{timestamp}-reservations.db"
    backup_path = cfg.backup_dir / backup_name
    
    # Atomic copy: write to temp file, then rename
    try:
        with tempfile.NamedTemporaryFile(
            mode='wb',
            delete=False,
            dir=str(cfg.backup_dir),
            suffix='.tmp'
        ) as tmp:
            with open(db_path, 'rb') as src:
                shutil.copyfileobj(src, tmp)
            tmp_path = tmp.name
        
        # Atomic rename
        os.replace(tmp_path, backup_path)
        logger.info(f"Database backup created: {backup_path}")
        
    except Exception as e:
        logger.error(f"Backup failed: {e}", exc_info=True)
        if 'tmp_path' in locals() and Path(tmp_path).exists():
            Path(tmp_path).unlink()
        raise
    
    # Clean up old backups
    cutoff = datetime.now() - timedelta(days=cfg.backup_retention_days)
    for backup_file in cfg.backup_dir.glob('*-reservations.db'):
        try:
            mtime = datetime.fromtimestamp(backup_file.stat().st_mtime)
            if mtime < cutoff:
                backup_file.unlink()
                logger.info(f"Deleted old backup: {backup_file}")
        except Exception as e:
            logger.warning(f"Failed to delete old backup {backup_file}: {e}")


def export_csv(cfg: AppConfig, output_dir: Optional[Path] = None) -> None:
    """
    Export current database state to CSV files.
    
    Args:
        cfg: Application configuration
        output_dir: Target directory for CSV files (defaults to cfg.data_dir)
        
    Side Effects:
        - Creates/overwrites rooms.csv and reservations.csv
        - Uses atomic writes (temp file + rename)
        
    Output Files:
        - rooms.csv: room_id, room_type, base_price, image_path
        - reservations.csv: reservation_id, room_id, guest_name, phone, email,
                           check_in_date, check_out_date, num_guests, status,
                           total_cost, created_at, updated_at
        
    Use Cases:
        - Legacy compatibility
        - Data export for reporting
        - Backup in human-readable format
    """
    if output_dir is None:
        output_dir = cfg.data_dir
    
    output_dir.mkdir(parents=True, exist_ok=True)
    db_path = ensure_db(cfg)
    
    logger.info(f"Exporting database to CSV files in {output_dir}")
    
    # Export rooms
    rooms_path = output_dir / 'rooms.csv'
    with get_connection(db_path) as conn:
        cursor = conn.execute("SELECT room_id, room_type, base_price, image_path FROM rooms ORDER BY room_id")
        rows = cursor.fetchall()
        
        with tempfile.NamedTemporaryFile(
            mode='w',
            delete=False,
            dir=str(output_dir),
            newline='',
            encoding='utf-8'
        ) as tmp:
            writer = csv.writer(tmp)
            writer.writerow(['room_id', 'room_type', 'base_price', 'image_path'])
            for row in rows:
                writer.writerow([row['room_id'], row['room_type'], row['base_price'], row['image_path']])
            tmp_path = tmp.name
        
        os.replace(tmp_path, rooms_path)
        logger.info(f"Exported {len(rows)} rooms to {rooms_path}")
    
    # Export reservations
    reservations_path = output_dir / 'reservations.csv'
    with get_connection(db_path) as conn:
        cursor = conn.execute("""
            SELECT id, room_id, guest_name, guest_phone, guest_email,
                   start_date, end_date, num_guests, status,
                   total_cost, created_at, updated_at
            FROM reservations
            ORDER BY created_at
        """)
        rows = cursor.fetchall()
        
        with tempfile.NamedTemporaryFile(
            mode='w',
            delete=False,
            dir=str(output_dir),
            newline='',
            encoding='utf-8'
        ) as tmp:
            writer = csv.writer(tmp)
            writer.writerow([
                'reservation_id', 'room_id', 'guest_name', 'phone', 'email',
                'check_in_date', 'check_out_date', 'num_guests', 'status',
                'total_cost', 'created_at', 'updated_at'
            ])
            for row in rows:
                writer.writerow([
                    row['id'], row['room_id'], row['guest_name'],
                    row['guest_phone'], row['guest_email'],
                    row['start_date'], row['end_date'], row['num_guests'],
                    row['status'], f"{row['total_cost']:.2f}",
                    row['created_at'], row['updated_at']
                ])
            tmp_path = tmp.name
        
        os.replace(tmp_path, reservations_path)
        logger.info(f"Exported {len(rows)} reservations to {reservations_path}")
    
    print(f"\n✓ Export complete: {rooms_path.parent}")
    print(f"  - rooms.csv: {len(rows)} rooms")
    print(f"  - reservations.csv: {len(rows)} reservations\n")
