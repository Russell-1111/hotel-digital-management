from pathlib import Path
from app.rooms import load_rooms, index_by_id
from app.storage import write_csv_atomic


def test_load_rooms_valid(tmp_path: Path):
    """Test loading rooms from valid CSV."""
    rooms_path = tmp_path / "rooms.csv"
    fieldnames = ["room_id", "room_type", "base_price"]
    rows = [
        {"room_id": "101", "room_type": "Standard", "base_price": "120.00"},
        {"room_id": "102", "room_type": "Deluxe", "base_price": "180.00"},
        {"room_id": "103", "room_type": "Suite", "base_price": "250.00"},
    ]
    write_csv_atomic(rooms_path, fieldnames, rows)
    
    rooms = load_rooms(rooms_path)
    
    assert len(rooms) == 3
    assert rooms[0].room_id == "101"
    assert rooms[0].room_type == "Standard"
    assert rooms[0].base_price == 120.0
    assert rooms[2].base_price == 250.0


def test_load_rooms_missing_columns(tmp_path: Path):
    """Test that missing required columns raises ValueError."""
    rooms_path = tmp_path / "rooms.csv"
    fieldnames = ["room_id", "room_type"]  # Missing base_price
    rows = [{"room_id": "101", "room_type": "Standard"}]
    write_csv_atomic(rooms_path, fieldnames, rows)
    
    try:
        load_rooms(rooms_path)
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "missing columns" in str(e)


def test_load_rooms_empty(tmp_path: Path):
    """Test loading empty rooms CSV."""
    rooms_path = tmp_path / "rooms.csv"
    rooms_path.write_text("room_id,room_type,base_price\n", encoding='utf-8')
    
    rooms = load_rooms(rooms_path)
    assert rooms == []


def test_index_by_id(tmp_path: Path):
    """Test indexing rooms by ID."""
    rooms_path = tmp_path / "rooms.csv"
    fieldnames = ["room_id", "room_type", "base_price"]
    rows = [
        {"room_id": "101", "room_type": "Standard", "base_price": "120.00"},
        {"room_id": "102", "room_type": "Deluxe", "base_price": "180.00"},
    ]
    write_csv_atomic(rooms_path, fieldnames, rows)
    
    rooms = load_rooms(rooms_path)
    index = index_by_id(rooms)
    
    assert len(index) == 2
    assert "101" in index
    assert index["101"].room_type == "Standard"
    assert index["102"].base_price == 180.0
