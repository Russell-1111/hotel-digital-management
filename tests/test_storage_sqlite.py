"""
Unit tests for SQLite storage backend.

Tests cover:
- Schema initialization
- CRUD operations with transactions
- CSV migration
- Availability queries with indexes
- Backup operations
- CSV export
"""

import sqlite3
import tempfile
from datetime import datetime, timedelta
from pathlib import Path

import pytest

from app.rooms import AppConfig
from app import storage_sqlite


@pytest.fixture
def temp_cfg(tmp_path: Path) -> AppConfig:
    """Create temporary config for testing."""
    return AppConfig(
        data_dir=tmp_path / "data",
        backup_dir=tmp_path / "backups",
        use_sqlite=True,
        check_in_time="14:00",
        check_out_time="11:00",
        backup_time="02:30",
        backup_retention_days=7,
        service_charge_rate=0.10,
        tax_rate=0.06,
        currency="MYR",
        timezone="Asia/Kuala_Lumpur",
        remember_username=False,
        last_username=""
    )


@pytest.fixture
def sample_rooms_csv(tmp_path: Path) -> Path:
    """Create sample rooms.csv for migration testing."""
    csv_path = tmp_path / "data" / "rooms.csv"
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    
    csv_path.write_text(
        "room_id,room_type,base_price,image_path\n"
        "101,Standard,100.00,images/rooms/101.png\n"
        "102,Deluxe,150.00,images/rooms/102.png\n"
        "103,Standard,100.00,\n",
        encoding='utf-8'
    )
    return csv_path


@pytest.fixture
def sample_reservations_csv(tmp_path: Path) -> Path:
    """Create sample reservations.csv for migration testing."""
    csv_path = tmp_path / "data" / "reservations.csv"
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    
    now = datetime.now().isoformat()
    csv_path.write_text(
        "reservation_id,room_id,guest_name,phone,email,check_in_date,check_out_date,num_guests,status,total_cost,created_at,updated_at\n"
        f"r1,101,Alice,111,alice@gmail.com,2025-10-25,2025-10-27,2,Confirmed,233.20,{now},{now}\n"
        f"r2,102,Bob,222,bob@outlook.com,2025-10-28,2025-10-30,1,Confirmed,349.80,{now},{now}\n",
        encoding='utf-8'
    )
    return csv_path


def test_schema_initialization(temp_cfg: AppConfig):
    """Test that database schema is created correctly."""
    db_path = storage_sqlite.ensure_db(temp_cfg)
    
    assert db_path.exists()
    
    # Verify tables exist
    with sqlite3.connect(str(db_path)) as conn:
        cursor = conn.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' 
            ORDER BY name
        """)
        tables = [row[0] for row in cursor.fetchall()]
        
        assert 'schema_info' in tables
        assert 'rooms' in tables
        assert 'reservations' in tables
        
        # Verify index exists
        cursor = conn.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='index' AND name='idx_reservations_availability'
        """)
        assert cursor.fetchone() is not None


def test_csv_migration(temp_cfg: AppConfig, sample_rooms_csv: Path, sample_reservations_csv: Path):
    """Test automatic CSV to SQLite migration."""
    db_path = storage_sqlite.ensure_db(temp_cfg)
    
    assert db_path.exists()
    
    # Verify rooms migrated
    rooms = storage_sqlite.read_rooms(temp_cfg)
    assert len(rooms) == 3
    assert rooms[0]['room_id'] == '101'
    assert rooms[0]['room_type'] == 'Standard'
    assert rooms[0]['base_price'] == 100.0
    assert rooms[1]['room_id'] == '102'
    assert rooms[1]['base_price'] == 150.0
    
    # Verify reservations migrated
    reservations = storage_sqlite.read_reservations(temp_cfg)
    assert len(reservations) == 2
    assert reservations[0]['id'] == 'r1'
    assert reservations[0]['guest_name'] == 'Alice'
    assert reservations[1]['id'] == 'r2'
    assert reservations[1]['guest_name'] == 'Bob'
    
    # Verify original CSV files still exist
    assert sample_rooms_csv.exists()
    assert sample_reservations_csv.exists()


def test_read_rooms(temp_cfg: AppConfig):
    """Test reading rooms from database."""
    db_path = storage_sqlite.ensure_db(temp_cfg)
    
    # Insert test data
    with storage_sqlite.get_connection(db_path) as conn:
        conn.execute("""
            INSERT INTO rooms (room_id, room_type, base_price, image_path)
            VALUES ('101', 'Standard', 100.0, ''), ('102', 'Deluxe', 150.0, 'img.png')
        """)
    
    rooms = storage_sqlite.read_rooms(temp_cfg)
    assert len(rooms) == 2
    assert rooms[0]['room_id'] == '101'
    assert rooms[1]['room_id'] == '102'
    assert rooms[1]['image_path'] == 'img.png'


def test_write_reservation(temp_cfg: AppConfig):
    """Test creating a new reservation with transaction."""
    db_path = storage_sqlite.ensure_db(temp_cfg)
    
    # Add a room first
    with storage_sqlite.get_connection(db_path) as conn:
        conn.execute("""
            INSERT INTO rooms (room_id, room_type, base_price, image_path)
            VALUES ('101', 'Standard', 100.0, '')
        """)
    
    # Create reservation
    now = datetime.now().isoformat()
    reservation = {
        'id': 'r1',
        'room_id': '101',
        'guest_name': 'Alice',
        'guest_phone': '111',
        'guest_email': 'alice@gmail.com',
        'start_date': '2025-10-25',
        'end_date': '2025-10-27',
        'num_guests': 2,
        'status': 'Confirmed',
        'total_cost': 233.20,
        'created_at': now,
        'updated_at': now
    }
    
    success = storage_sqlite.write_reservation(temp_cfg, reservation)
    assert success
    
    # Verify it was saved
    reservations = storage_sqlite.read_reservations(temp_cfg)
    assert len(reservations) == 1
    assert reservations[0]['guest_name'] == 'Alice'


def test_double_booking_prevention(temp_cfg: AppConfig):
    """Test that overlapping reservations are rejected."""
    db_path = storage_sqlite.ensure_db(temp_cfg)
    
    # Add a room
    with storage_sqlite.get_connection(db_path) as conn:
        conn.execute("""
            INSERT INTO rooms (room_id, room_type, base_price, image_path)
            VALUES ('101', 'Standard', 100.0, '')
        """)
    
    # Create first reservation
    now = datetime.now().isoformat()
    reservation1 = {
        'id': 'r1',
        'room_id': '101',
        'guest_name': 'Alice',
        'guest_phone': '111',
        'guest_email': 'alice@gmail.com',
        'start_date': '2025-10-25',
        'end_date': '2025-10-27',
        'num_guests': 2,
        'status': 'Confirmed',
        'total_cost': 233.20,
        'created_at': now,
        'updated_at': now
    }
    
    success = storage_sqlite.write_reservation(temp_cfg, reservation1)
    assert success
    
    # Try overlapping reservation (should fail)
    reservation2 = {
        'id': 'r2',
        'room_id': '101',
        'guest_name': 'Bob',
        'guest_phone': '222',
        'guest_email': 'bob@outlook.com',
        'start_date': '2025-10-26',
        'end_date': '2025-10-28',
        'num_guests': 1,
        'status': 'Confirmed',
        'total_cost': 233.20,
        'created_at': now,
        'updated_at': now
    }
    
    success = storage_sqlite.write_reservation(temp_cfg, reservation2)
    assert not success  # Should be rejected
    
    # Only first reservation should exist
    reservations = storage_sqlite.read_reservations(temp_cfg)
    assert len(reservations) == 1


def test_update_reservation(temp_cfg: AppConfig):
    """Test updating an existing reservation."""
    db_path = storage_sqlite.ensure_db(temp_cfg)
    
    # Setup: add room and reservation
    with storage_sqlite.get_connection(db_path) as conn:
        conn.execute("""
            INSERT INTO rooms (room_id, room_type, base_price, image_path)
            VALUES ('101', 'Standard', 100.0, '')
        """)
    
    now = datetime.now().isoformat()
    reservation = {
        'id': 'r1',
        'room_id': '101',
        'guest_name': 'Alice',
        'guest_phone': '111',
        'guest_email': 'alice@gmail.com',
        'start_date': '2025-10-25',
        'end_date': '2025-10-27',
        'num_guests': 2,
        'status': 'Confirmed',
        'total_cost': 233.20,
        'created_at': now,
        'updated_at': now
    }
    
    storage_sqlite.write_reservation(temp_cfg, reservation)
    
    # Update guest info
    success = storage_sqlite.update_reservation(temp_cfg, 'r1', {
        'guest_name': 'Alice Smith',
        'guest_phone': '999'
    })
    assert success
    
    # Verify update
    reservations = storage_sqlite.read_reservations(temp_cfg)
    assert reservations[0]['guest_name'] == 'Alice Smith'
    assert reservations[0]['guest_phone'] == '999'
    assert reservations[0]['guest_email'] == 'alice@gmail.com'  # Unchanged


def test_is_room_available(temp_cfg: AppConfig):
    """Test room availability checking with indexed query."""
    db_path = storage_sqlite.ensure_db(temp_cfg)
    
    # Setup: add room and reservation
    with storage_sqlite.get_connection(db_path) as conn:
        conn.execute("""
            INSERT INTO rooms (room_id, room_type, base_price, image_path)
            VALUES ('101', 'Standard', 100.0, '')
        """)
    
    now = datetime.now().isoformat()
    reservation = {
        'id': 'r1',
        'room_id': '101',
        'guest_name': 'Alice',
        'guest_phone': '111',
        'guest_email': 'alice@gmail.com',
        'start_date': '2025-10-25',
        'end_date': '2025-10-27',
        'num_guests': 2,
        'status': 'Confirmed',
        'total_cost': 233.20,
        'created_at': now,
        'updated_at': now
    }
    
    storage_sqlite.write_reservation(temp_cfg, reservation)
    
    # Test availability checks
    assert not storage_sqlite.is_room_available(temp_cfg, '101', '2025-10-25', '2025-10-27')  # Exact overlap
    assert not storage_sqlite.is_room_available(temp_cfg, '101', '2025-10-26', '2025-10-28')  # Partial overlap
    assert storage_sqlite.is_room_available(temp_cfg, '101', '2025-10-23', '2025-10-25')  # Before (no overlap)
    assert storage_sqlite.is_room_available(temp_cfg, '101', '2025-10-27', '2025-10-29')  # After (no overlap)
    assert storage_sqlite.is_room_available(temp_cfg, '102', '2025-10-25', '2025-10-27')  # Different room
    
    # Test exclude_id parameter (for modifications)
    assert storage_sqlite.is_room_available(temp_cfg, '101', '2025-10-25', '2025-10-27', exclude_id='r1')


def test_backup_db(temp_cfg: AppConfig):
    """Test database backup creation."""
    db_path = storage_sqlite.ensure_db(temp_cfg)
    
    # Add some data
    with storage_sqlite.get_connection(db_path) as conn:
        conn.execute("""
            INSERT INTO rooms (room_id, room_type, base_price, image_path)
            VALUES ('101', 'Standard', 100.0, '')
        """)
    
    # Create backup
    storage_sqlite.backup_db(temp_cfg)
    
    # Verify backup exists
    backups = list(temp_cfg.backup_dir.glob('*-reservations.db'))
    assert len(backups) == 1
    assert backups[0].exists()
    
    # Verify backup is valid SQLite database
    with sqlite3.connect(str(backups[0])) as conn:
        cursor = conn.execute("SELECT COUNT(*) FROM rooms")
        assert cursor.fetchone()[0] == 1


def test_backup_retention(temp_cfg: AppConfig):
    """Test that old backups are deleted."""
    db_path = storage_sqlite.ensure_db(temp_cfg)
    
    # Create an old backup (simulate)
    old_timestamp = (datetime.now() - timedelta(days=8)).strftime('%Y%m%d-%H%M%S')
    old_backup = temp_cfg.backup_dir / f"{old_timestamp}-reservations.db"
    temp_cfg.backup_dir.mkdir(parents=True, exist_ok=True)
    old_backup.write_text("fake backup", encoding='utf-8')
    
    # Set file modification time to 8 days ago
    import os
    old_time = (datetime.now() - timedelta(days=8)).timestamp()
    os.utime(old_backup, (old_time, old_time))
    
    # Run backup (should clean up old one)
    storage_sqlite.backup_db(temp_cfg)
    
    # Old backup should be deleted
    assert not old_backup.exists()


def test_csv_export(temp_cfg: AppConfig):
    """Test exporting database to CSV files."""
    db_path = storage_sqlite.ensure_db(temp_cfg)
    
    # Add test data
    with storage_sqlite.get_connection(db_path) as conn:
        conn.execute("""
            INSERT INTO rooms (room_id, room_type, base_price, image_path)
            VALUES ('101', 'Standard', 100.0, 'img.png')
        """)
        
        now = datetime.now().isoformat()
        conn.execute("""
            INSERT INTO reservations (
                id, room_id, guest_name, guest_phone, guest_email,
                start_date, end_date, num_guests, status,
                total_cost, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, ('r1', '101', 'Alice', '111', 'alice@gmail.com',
              '2025-10-25', '2025-10-27', 2, 'Confirmed',
              233.20, now, now))
    
    # Export to CSV
    export_dir = temp_cfg.data_dir / 'export'
    storage_sqlite.export_csv(temp_cfg, export_dir)
    
    # Verify CSV files exist
    assert (export_dir / 'rooms.csv').exists()
    assert (export_dir / 'reservations.csv').exists()
    
    # Verify content
    rooms_content = (export_dir / 'rooms.csv').read_text(encoding='utf-8')
    assert '101' in rooms_content
    assert 'Standard' in rooms_content
    assert '100.0' in rooms_content
    
    reservations_content = (export_dir / 'reservations.csv').read_text(encoding='utf-8')
    assert 'r1' in reservations_content
    assert 'Alice' in reservations_content


def test_transaction_rollback_on_error(temp_cfg: AppConfig):
    """Test that transactions roll back on errors."""
    db_path = storage_sqlite.ensure_db(temp_cfg)
    
    # Add a room
    with storage_sqlite.get_connection(db_path) as conn:
        conn.execute("""
            INSERT INTO rooms (room_id, room_type, base_price, image_path)
            VALUES ('101', 'Standard', 100.0, '')
        """)
    
    # Try to create reservation with invalid foreign key (should fail and rollback)
    now = datetime.now().isoformat()
    invalid_reservation = {
        'id': 'r1',
        'room_id': '999',  # Non-existent room
        'guest_name': 'Alice',
        'guest_phone': '111',
        'guest_email': 'alice@gmail.com',
        'start_date': '2025-10-25',
        'end_date': '2025-10-27',
        'num_guests': 2,
        'status': 'Confirmed',
        'total_cost': 233.20,
        'created_at': now,
        'updated_at': now
    }
    
    success = storage_sqlite.write_reservation(temp_cfg, invalid_reservation)
    assert not success
    
    # Verify no reservations exist (transaction rolled back)
    reservations = storage_sqlite.read_reservations(temp_cfg)
    assert len(reservations) == 0


def test_date_range_filtering(temp_cfg: AppConfig):
    """Test reading reservations with date range filter."""
    db_path = storage_sqlite.ensure_db(temp_cfg)
    
    # Setup: add room and multiple reservations
    with storage_sqlite.get_connection(db_path) as conn:
        conn.execute("""
            INSERT INTO rooms (room_id, room_type, base_price, image_path)
            VALUES ('101', 'Standard', 100.0, '')
        """)
        
        now = datetime.now().isoformat()
        conn.execute("""
            INSERT INTO reservations (
                id, room_id, guest_name, guest_phone, guest_email,
                start_date, end_date, num_guests, status,
                total_cost, created_at, updated_at
            ) VALUES 
            ('r1', '101', 'Alice', '111', 'a@x.com', '2025-10-25', '2025-10-27', 2, 'Confirmed', 233.20, ?, ?),
            ('r2', '101', 'Bob', '222', 'b@x.com', '2025-11-01', '2025-11-03', 1, 'Confirmed', 233.20, ?, ?),
            ('r3', '101', 'Carol', '333', 'c@x.com', '2025-11-10', '2025-11-12', 2, 'Confirmed', 233.20, ?, ?)
        """, (now, now, now, now, now, now))
    
    # Test date range filtering
    reservations_oct = storage_sqlite.read_reservations(temp_cfg, date_range=('2025-10-01', '2025-10-31'))
    assert len(reservations_oct) == 1
    assert reservations_oct[0]['guest_name'] == 'Alice'
    
    reservations_nov = storage_sqlite.read_reservations(temp_cfg, date_range=('2025-11-01', '2025-11-30'))
    assert len(reservations_nov) == 2
    assert {r['guest_name'] for r in reservations_nov} == {'Bob', 'Carol'}
    
    # Test without filter (all reservations)
    all_reservations = storage_sqlite.read_reservations(temp_cfg)
    assert len(all_reservations) == 3
