"""
Storage layer for Hotel Digital Management System.

This module provides backup scheduling functionality for the SQLite backend.
All data persistence is handled by storage_sqlite.py.
"""

from __future__ import annotations
import threading
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

from .rooms import AppConfig
from .timezone_utils import now_utc


def backup_now(cfg: AppConfig):
    """
    Create backup of SQLite database.
    
    Args:
        cfg: Application configuration
    """
    from . import storage_sqlite
    storage_sqlite.backup_db(cfg)


def ensure_dirs(cfg: AppConfig):
    """
    Ensure SQLite database and directories exist.
    
    Args:
        cfg: Application configuration
        
    Returns:
        Path to SQLite database
        
    Note:
        Kept for backward compatibility. Delegates to storage_sqlite.ensure_db()
    """
    from . import storage_sqlite
    return storage_sqlite.ensure_db(cfg)


def _parse_time(hhmm: str, hotel_tz: ZoneInfo) -> datetime:
    """
    Parse HH:MM time string to next occurrence in hotel timezone, return as UTC.
    
    Args:
        hhmm: Time string in HH:MM format (e.g., "02:30")
        hotel_tz: Hotel's configured timezone
        
    Returns:
        Next occurrence of the time as timezone-aware datetime in UTC
    """
    now_hotel = now_utc().astimezone(hotel_tz)
    hour, minute = map(int, hhmm.split(':'))
    target = now_hotel.replace(hour=hour, minute=minute, second=0, microsecond=0)
    if target <= now_hotel:
        target += timedelta(days=1)
    return target.astimezone(timezone.utc)


def start_daily_backup_scheduler(cfg: AppConfig):
    """
    Start background thread for daily SQLite backups.
    
    Args:
        cfg: Application configuration
        
    Returns:
        Thread object
    """
    from .timezone_utils import get_hotel_tz
    hotel_tz = get_hotel_tz(cfg.timezone)
    
    def _runner():
        while True:
            next_run = _parse_time(cfg.backup_time, hotel_tz)
            sleep_secs = (next_run - now_utc()).total_seconds()
            if sleep_secs > 0:
                threading.Event().wait(timeout=sleep_secs)
            try:
                backup_now(cfg)
            except Exception:
                # Logging will capture details in the app layer
                pass

    t = threading.Thread(target=_runner, name='backup-scheduler', daemon=True)
    t.start()
    return t
