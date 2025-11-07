from __future__ import annotations
import configparser
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import logging


# ============================================================================
# Configuration Management (merged from config.py)
# ============================================================================

DEFAULT_CONFIG = {
    'paths': {
        'data_dir': 'data',
        'backup_dir': 'backups'
    },
    'storage': {
        'use_sqlite': 'true'
    },
    'ops': {
        'check_in_time': '14:00',
        'check_out_time': '11:00',
        'backup_time': '02:30',
        'backup_retention_days': '7',
        'timezone': 'Asia/Kuala_Lumpur'
    },
    'finance': {
        'service_charge_rate': '0.10',
        'tax_rate': '0.06',
        'currency': 'MYR'
    }
}


@dataclass
class AppConfig:
    data_dir: Path
    backup_dir: Path
    use_sqlite: bool
    check_in_time: str
    check_out_time: str
    backup_time: str
    backup_retention_days: int
    service_charge_rate: float
    tax_rate: float
    currency: str
    timezone: str


def load_config(config_path: Path) -> AppConfig:
    from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
    
    cfg = configparser.ConfigParser()
    cfg.read_dict(DEFAULT_CONFIG)
    if config_path.exists():
        cfg.read(config_path)

    data_dir = Path(cfg['paths']['data_dir'])
    backup_dir = Path(cfg['paths']['backup_dir'])
    use_sqlite = cfg.getboolean('storage', 'use_sqlite', fallback=True)
    
    # Validate timezone
    timezone_str = cfg['ops']['timezone']
    try:
        ZoneInfo(timezone_str)
    except ZoneInfoNotFoundError:
        raise ValueError(
            f"Invalid timezone '{timezone_str}' in config.ini. "
            f"Please use a valid IANA timezone name (e.g., 'Asia/Kuala_Lumpur', 'UTC', 'America/New_York'). "
            f"See https://en.wikipedia.org/wiki/List_of_tz_database_time_zones for a complete list."
        )

    return AppConfig(
        data_dir=data_dir,
        backup_dir=backup_dir,
        use_sqlite=use_sqlite,
        check_in_time=cfg['ops']['check_in_time'],
        check_out_time=cfg['ops']['check_out_time'],
        backup_time=cfg['ops']['backup_time'],
        backup_retention_days=int(cfg['ops']['backup_retention_days']),
        service_charge_rate=float(cfg['finance']['service_charge_rate']),
        tax_rate=float(cfg['finance']['tax_rate']),
        currency=cfg['finance']['currency'],
        timezone=timezone_str
    )


# ============================================================================
# Room Management
# ============================================================================


@dataclass
class Room:
    room_id: str
    room_type: str
    base_price: float
    image_path: str = ""  # Relative path to room image (e.g., "images/rooms/101.png")


def load_rooms(path: Path) -> List[Room]:
    from .storage import read_csv
    rows = read_csv(path)
    required = {"room_id", "room_type", "base_price"}
    if rows:
        missing = required - set(rows[0].keys())
        if missing:
            raise ValueError(f"rooms.csv missing columns: {missing}")
    result: List[Room] = []
    for r in rows:
        result.append(Room(
            room_id=str(r.get("room_id", "")).strip(),
            room_type=str(r.get("room_type", "")).strip(),
            base_price=float(r.get("base_price", 0) or 0),
            image_path=str(r.get("image_path", "")).strip(),
        ))
    return result


def index_by_id(rooms: List[Room]) -> Dict[str, Room]:
    return {r.room_id: r for r in rooms}


# Image cache to prevent garbage collection of PhotoImage objects
_image_cache: Dict[str, object] = {}


def load_room_image(image_path: str, size: Tuple[int, int]) -> Optional[object]:
    """
    Load and resize a room image for display in Tkinter UI.
    
    Args:
        image_path: Relative path to the image file (e.g., "images/rooms/101.png")
        size: Target size as (width, height) tuple
    
    Returns:
        PhotoImage object ready for Tkinter display, or None if loading fails
    
    Note:
        - Falls back to placeholder.png if image_path is empty or file not found
        - Caches loaded images to prevent garbage collection
        - Logs warnings for invalid/missing images
    """
    import tkinter as tk
    from pathlib import Path
    
    # Generate cache key
    cache_key = f"{image_path}_{size[0]}x{size[1]}"
    
    # Return cached image if available
    if cache_key in _image_cache:
        return _image_cache[cache_key]
    
    # Determine actual file path
    if not image_path or not Path(image_path).exists():
        if image_path:
            logging.getLogger(__name__).warning(f"Room image not found: {image_path}, using placeholder")
        file_path = Path("images/rooms/placeholder.png")
        if not file_path.exists():
            logging.getLogger(__name__).error("Placeholder image not found")
            return None
    else:
        file_path = Path(image_path)
    
    try:
        # Load image using PhotoImage (supports PNG, GIF)
        # Note: PhotoImage doesn't support resizing, so we load at original size
        # For production, consider using PIL/Pillow for better image handling
        img = tk.PhotoImage(file=str(file_path))
        
        # Subsample to approximate target size (simple downscaling)
        # Calculate subsample factor based on original vs target dimensions
        if img.width() > size[0] or img.height() > size[1]:
            x_factor = max(1, img.width() // size[0])
            y_factor = max(1, img.height() // size[1])
            subsample_factor = max(x_factor, y_factor)
            img = img.subsample(subsample_factor, subsample_factor)
        
        # Cache the image
        _image_cache[cache_key] = img
        return img
        
    except Exception as e:
        error_msg = str(e) if str(e) else type(e).__name__
        logging.getLogger(__name__).warning(f"Failed to load image {file_path}: {error_msg}")
        
        # Try placeholder as fallback
        if file_path != Path("images/rooms/placeholder.png"):
            return load_room_image("", size)
        
        return None


def clear_image_cache():
    """Clear the image cache. Useful when reloading room data."""
    global _image_cache
    _image_cache = {}
