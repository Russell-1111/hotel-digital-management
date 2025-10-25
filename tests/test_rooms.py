from pathlib import Path
import tkinter as tk
from app.rooms import load_rooms, index_by_id, load_room_image, clear_image_cache
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


import pytest


# Fixture to provide a shared Tkinter root for all image tests
@pytest.fixture(scope="module")
def tk_root():
    """Create a single Tkinter root for all tests in this module."""
    root = tk.Tk()
    root.withdraw()
    yield root
    root.destroy()
    clear_image_cache()


def test_load_room_image_valid(tk_root):
    """Test loading a valid room image."""
    # Use the existing room images
    img = load_room_image("images/rooms/101.png", (80, 60))
    
    # Should return a PhotoImage object
    assert img is not None
    assert isinstance(img, tk.PhotoImage)
    clear_image_cache()


def test_load_room_image_missing_file(tk_root):
    """Test loading a non-existent image falls back to placeholder."""
    # Non-existent image should fall back to placeholder
    img = load_room_image("nonexistent/path.png", (80, 60))
    
    # Should still return an image (placeholder)
    assert img is not None
    assert isinstance(img, tk.PhotoImage)
    clear_image_cache()


def test_load_room_image_empty_path(tk_root):
    """Test loading with empty path returns placeholder."""
    # Empty path should load placeholder
    img = load_room_image("", (80, 60))
    
    assert img is not None
    assert isinstance(img, tk.PhotoImage)
    clear_image_cache()


def test_load_room_image_caching(tk_root):
    """Test that images are cached properly."""
    # Load same image twice
    img1 = load_room_image("images/rooms/101.png", (80, 60))
    img2 = load_room_image("images/rooms/101.png", (80, 60))
    
    # Should return the same cached object
    assert img1 is img2
    
    # Different size should create new cache entry
    img3 = load_room_image("images/rooms/101.png", (320, 240))
    assert img3 is not img1
    clear_image_cache()


def test_clear_image_cache(tk_root):
    """Test clearing the image cache."""
    # Load an image
    img1 = load_room_image("images/rooms/101.png", (80, 60))
    
    # Clear cache
    clear_image_cache()
    
    # Load again - should be a new object
    img2 = load_room_image("images/rooms/101.png", (80, 60))
    assert img1 is not img2
    clear_image_cache()


def test_load_rooms_with_image_path(tmp_path: Path):
    """Test loading rooms with image_path field."""
    rooms_path = tmp_path / "rooms.csv"
    fieldnames = ["room_id", "room_type", "base_price", "image_path"]
    rows = [
        {
            "room_id": "101",
            "room_type": "Standard",
            "base_price": "120.00",
            "image_path": "images/rooms/101.png"
        },
        {
            "room_id": "102",
            "room_type": "Deluxe",
            "base_price": "180.00",
            "image_path": ""
        },
    ]
    write_csv_atomic(rooms_path, fieldnames, rows)
    
    rooms = load_rooms(rooms_path)
    
    assert len(rooms) == 2
    assert rooms[0].image_path == "images/rooms/101.png"
    assert rooms[1].image_path == ""
