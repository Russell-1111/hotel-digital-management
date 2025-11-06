#!/usr/bin/env python3
"""
Standalone CSV to SQLite Migration Script

This script migrates data from CSV files (rooms.csv, reservations.csv) to an
SQLite database for the Hotel Digital Management System.

Usage:
    python scripts/migrate_csv_to_sqlite.py [OPTIONS]

Options:
    --data-dir PATH      Directory containing CSV files (default: data/)
    --output PATH        Output database path (default: data/reservations.db)
    --dry-run            Validate CSV data without creating database
    --verbose, -v        Enable verbose logging
    --help, -h           Show this help message

Examples:
    # Basic migration (uses defaults)
    python scripts/migrate_csv_to_sqlite.py

    # Specify custom paths
    python scripts/migrate_csv_to_sqlite.py --data-dir ./my_data --output ./hotel.db

    # Validate CSV without migrating
    python scripts/migrate_csv_to_sqlite.py --dry-run --verbose

Exit Codes:
    0 - Success
    1 - CSV file not found
    2 - Invalid CSV data
    3 - Database creation failed
    4 - Other error
"""

import argparse
import csv
import logging
import sqlite3
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple


def setup_logging(verbose: bool = False) -> None:
    """Configure logging for the migration script."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )


def validate_csv_files(data_dir: Path) -> Tuple[Path, Path]:
    """
    Validate that required CSV files exist.
    
    Args:
        data_dir: Directory containing CSV files
        
    Returns:
        Tuple of (rooms_path, reservations_path)
        
    Raises:
        FileNotFoundError: If required CSV files are missing
    """
    rooms_path = data_dir / 'rooms.csv'
    reservations_path = data_dir / 'reservations.csv'
    
    if not data_dir.exists():
        raise FileNotFoundError(f"Data directory not found: {data_dir}")
    
    if not rooms_path.exists():
        raise FileNotFoundError(f"rooms.csv not found in {data_dir}")
    
    if not reservations_path.exists():
        raise FileNotFoundError(f"reservations.csv not found in {data_dir}")
    
    logging.info(f"Found CSV files in {data_dir}")
    return rooms_path, reservations_path


def validate_room_row(row: Dict[str, str], row_num: int) -> List[str]:
    """
    Validate a room CSV row.
    
    Args:
        row: CSV row as dictionary
        row_num: Row number for error reporting
        
    Returns:
        List of validation error messages (empty if valid)
    """
    errors = []
    
    if not row.get('room_id', '').strip():
        errors.append(f"Row {row_num}: Missing room_id")
    
    if not row.get('room_type', '').strip():
        errors.append(f"Row {row_num}: Missing room_type")
    
    try:
        price = float(row.get('base_price', 0))
        if price < 0:
            errors.append(f"Row {row_num}: Negative base_price: {price}")
    except ValueError:
        errors.append(f"Row {row_num}: Invalid base_price: {row.get('base_price')}")
    
    return errors


def validate_reservation_row(row: Dict[str, str], row_num: int) -> List[str]:
    """
    Validate a reservation CSV row.
    
    Args:
        row: CSV row as dictionary
        row_num: Row number for error reporting
        
    Returns:
        List of validation error messages (empty if valid)
    """
    errors = []
    
    required_fields = [
        'reservation_id', 'room_id', 'guest_name', 'phone', 'email',
        'check_in_date', 'check_out_date', 'status'
    ]
    
    for field in required_fields:
        if not row.get(field, '').strip():
            errors.append(f"Row {row_num}: Missing {field}")
    
    # Validate dates
    for date_field in ['check_in_date', 'check_out_date', 'created_at', 'updated_at']:
        date_str = row.get(date_field, '').strip()
        if date_str:
            try:
                datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            except ValueError:
                errors.append(f"Row {row_num}: Invalid {date_field}: {date_str}")
    
    # Validate numeric fields
    try:
        num_guests = int(row.get('num_guests', 0))
        if num_guests < 1:
            errors.append(f"Row {row_num}: Invalid num_guests: {num_guests}")
    except ValueError:
        errors.append(f"Row {row_num}: Invalid num_guests: {row.get('num_guests')}")
    
    try:
        total = float(row.get('total_cost', 0))
        if total < 0:
            errors.append(f"Row {row_num}: Negative total_cost: {total}")
    except ValueError:
        errors.append(f"Row {row_num}: Invalid total_cost: {row.get('total_cost')}")
    
    # Validate status
    valid_statuses = {'Confirmed', 'Cancelled', 'Checked-In', 'Checked-Out'}
    status = row.get('status', '').strip()
    if status and status not in valid_statuses:
        errors.append(f"Row {row_num}: Invalid status: {status} (must be one of {valid_statuses})")
    
    return errors


def dry_run_validation(rooms_path: Path, reservations_path: Path) -> bool:
    """
    Validate CSV files without creating database.
    
    Args:
        rooms_path: Path to rooms.csv
        reservations_path: Path to reservations.csv
        
    Returns:
        True if validation passes, False otherwise
    """
    logging.info("=" * 60)
    logging.info("DRY RUN: Validating CSV files")
    logging.info("=" * 60)
    
    all_errors = []
    
    # Validate rooms
    logging.info(f"Validating {rooms_path}...")
    with rooms_path.open('r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        room_count = 0
        for i, row in enumerate(reader, start=2):  # Start at 2 (header is row 1)
            room_count += 1
            errors = validate_room_row(row, i)
            all_errors.extend(errors)
    
    logging.info(f"  Checked {room_count} rooms")
    
    # Validate reservations
    logging.info(f"Validating {reservations_path}...")
    with reservations_path.open('r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        reservation_count = 0
        for i, row in enumerate(reader, start=2):
            reservation_count += 1
            errors = validate_reservation_row(row, i)
            all_errors.extend(errors)
    
    logging.info(f"  Checked {reservation_count} reservations")
    
    # Report results
    logging.info("=" * 60)
    if all_errors:
        logging.error(f"VALIDATION FAILED: {len(all_errors)} errors found")
        for error in all_errors:
            logging.error(f"  • {error}")
        return False
    else:
        logging.info("✓ VALIDATION PASSED")
        logging.info(f"  Ready to migrate {room_count} rooms and {reservation_count} reservations")
        logging.info("=" * 60)
        return True


def create_schema(conn: sqlite3.Connection) -> None:
    """Create database schema with tables and indexes."""
    logging.info("Creating database schema...")
    
    # Schema info table
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
    
    # Reservations table
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
    
    # Index for availability queries
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_reservations_availability
        ON reservations(room_id, start_date, end_date)
    """)
    
    # Record schema version
    conn.execute("""
        INSERT OR REPLACE INTO schema_info (version, migrated_at)
        VALUES (1, ?)
    """, (datetime.now().isoformat(),))
    
    logging.info("✓ Schema created")


def migrate_data(rooms_path: Path, reservations_path: Path, output_path: Path) -> None:
    """
    Perform the actual migration from CSV to SQLite.
    
    Args:
        rooms_path: Path to rooms.csv
        reservations_path: Path to reservations.csv
        output_path: Path to output database file
        
    Raises:
        RuntimeError: If migration fails
    """
    logging.info("=" * 60)
    logging.info("MIGRATING CSV TO SQLITE")
    logging.info("=" * 60)
    logging.info(f"Source: {rooms_path.parent}")
    logging.info(f"Target: {output_path}")
    logging.info("")
    
    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Delete existing database if present
    if output_path.exists():
        logging.warning(f"Removing existing database: {output_path}")
        output_path.unlink()
    
    try:
        # Create database connection
        conn = sqlite3.connect(str(output_path))
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute("PRAGMA journal_mode = WAL")
        
        # Create schema
        create_schema(conn)
        
        # Begin transaction for data migration
        conn.execute("BEGIN")
        
        # Migrate rooms
        logging.info("Migrating rooms...")
        rooms_migrated = 0
        rooms_skipped = 0
        
        with rooms_path.open('r', encoding='utf-8') as f:
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
                    logging.warning(f"Skipping room {row.get('room_id')}: {e}")
                    rooms_skipped += 1
        
        logging.info(f"  ✓ Migrated {rooms_migrated} rooms ({rooms_skipped} skipped)")
        
        # Migrate reservations
        logging.info("Migrating reservations...")
        reservations_migrated = 0
        reservations_skipped = 0
        
        with reservations_path.open('r', encoding='utf-8') as f:
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
                    logging.warning(f"Skipping reservation {row.get('reservation_id')}: {e}")
                    reservations_skipped += 1
        
        logging.info(f"  ✓ Migrated {reservations_migrated} reservations ({reservations_skipped} skipped)")
        
        # Commit transaction
        conn.commit()
        conn.close()
        
        # Success summary
        logging.info("=" * 60)
        logging.info("✓ MIGRATION COMPLETE")
        logging.info(f"  Database: {output_path}")
        logging.info(f"  Rooms: {rooms_migrated}")
        logging.info(f"  Reservations: {reservations_migrated}")
        logging.info(f"  Original CSV files preserved")
        logging.info("=" * 60)
        
    except Exception as e:
        logging.error(f"Migration failed: {e}", exc_info=True)
        # Clean up partial database
        if output_path.exists():
            output_path.unlink()
        raise RuntimeError(f"Migration failed: {e}") from e


def main() -> int:
    """Main entry point for the migration script."""
    parser = argparse.ArgumentParser(
        description='Migrate Hotel Management CSV data to SQLite',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    parser.add_argument(
        '--data-dir',
        type=Path,
        default=Path('data'),
        help='Directory containing CSV files (default: data/)'
    )
    
    parser.add_argument(
        '--output',
        type=Path,
        default=Path('data/reservations.db'),
        help='Output database path (default: data/reservations.db)'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Validate CSV data without creating database'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.verbose)
    
    try:
        # Validate CSV files exist
        rooms_path, reservations_path = validate_csv_files(args.data_dir)
        
        if args.dry_run:
            # Dry run: validate only
            success = dry_run_validation(rooms_path, reservations_path)
            return 0 if success else 2
        else:
            # Actual migration
            migrate_data(rooms_path, reservations_path, args.output)
            return 0
            
    except FileNotFoundError as e:
        logging.error(str(e))
        return 1
    except RuntimeError as e:
        logging.error(str(e))
        return 3
    except Exception as e:
        logging.error(f"Unexpected error: {e}", exc_info=True)
        return 4


if __name__ == '__main__':
    sys.exit(main())
