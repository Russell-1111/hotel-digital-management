from pathlib import Path
from datetime import datetime, timedelta
from app.storage import write_csv_atomic, read_csv, backup_now, ensure_dirs
from app.rooms import AppConfig


def test_csv_read_write(tmp_path: Path):
    """Test atomic CSV read and write operations."""
    csv_path = tmp_path / "test.csv"
    fieldnames = ["id", "name", "value"]
    rows = [
        {"id": "1", "name": "Alice", "value": "100"},
        {"id": "2", "name": "Bob", "value": "200"},
    ]
    
    write_csv_atomic(csv_path, fieldnames, rows)
    assert csv_path.exists()
    
    result = read_csv(csv_path)
    assert len(result) == 2
    assert result[0]["name"] == "Alice"
    assert result[1]["value"] == "200"


def test_csv_empty_file(tmp_path: Path):
    """Test reading non-existent CSV returns empty list."""
    csv_path = tmp_path / "missing.csv"
    result = read_csv(csv_path)
    assert result == []


def test_backup_creation_and_retention(tmp_path: Path):
    """Test backup creates timestamped files and respects retention policy."""
    data_dir = tmp_path / "data"
    backup_dir = tmp_path / "backups"
    data_dir.mkdir()
    backup_dir.mkdir()
    
    # Create sample data files
    rooms_path = data_dir / "rooms.csv"
    reservations_path = data_dir / "reservations.csv"
    rooms_path.write_text("room_id,room_type,base_price\n101,Standard,120.00\n", encoding='utf-8')
    reservations_path.write_text("reservation_id,room_id,guest_name,phone,email,check_in_date,check_out_date,num_guests,status,total_cost,created_at,updated_at\n", encoding='utf-8')
    
    # Create config
    cfg = AppConfig(
        data_dir=data_dir,
        backup_dir=backup_dir,
        use_sqlite=False,
        check_in_time="14:00",
        check_out_time="11:00",
        backup_time="02:30",
        backup_retention_days=7,
        service_charge_rate=0.10,
        tax_rate=0.06,
        currency="MYR"
    )
    
    from app.storage import FilePaths
    fps = FilePaths(data_dir, backup_dir, rooms_path, reservations_path)
    
    # Create backup
    backup_now(cfg, fps)
    
    # Check backup files exist
    backups = list(backup_dir.glob("*.csv"))
    assert len(backups) == 2
    assert any("rooms.csv" in str(b) for b in backups)
    assert any("reservations.csv" in str(b) for b in backups)
    
    # Create old backup (should be deleted)
    old_timestamp = (datetime.now() - timedelta(days=8)).strftime('%Y%m%d-%H%M%S')
    old_backup = backup_dir / f"{old_timestamp}-rooms.csv"
    old_backup.write_text("old", encoding='utf-8')
    
    # Manually set the modification time to 8 days ago to simulate old file
    import os
    old_time = (datetime.now() - timedelta(days=8)).timestamp()
    os.utime(old_backup, (old_time, old_time))
    
    # Run backup again (should delete old)
    backup_now(cfg, fps)
    
    # Old backup should be gone
    assert not old_backup.exists()


def test_ensure_dirs_creates_structure(tmp_path: Path):
    """Test that ensure_dirs creates data directory and CSV files with headers."""
    cfg = AppConfig(
        data_dir=tmp_path / "data",
        backup_dir=tmp_path / "backups",
        use_sqlite=False,
        check_in_time="14:00",
        check_out_time="11:00",
        backup_time="02:30",
        backup_retention_days=7,
        service_charge_rate=0.10,
        tax_rate=0.06,
        currency="MYR"
    )
    
    fps = ensure_dirs(cfg)
    
    assert cfg.data_dir.exists()
    assert cfg.backup_dir.exists()
    assert fps.rooms.exists()
    assert fps.reservations.exists()
    
    # Check headers
    rooms_content = fps.rooms.read_text(encoding='utf-8')
    assert "room_id,room_type,base_price" in rooms_content
    
    reservations_content = fps.reservations.read_text(encoding='utf-8')
    assert "reservation_id" in reservations_content
    assert "check_in_date" in reservations_content
