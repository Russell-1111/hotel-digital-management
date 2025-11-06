"""
Storage layer compatibility shim for Hotel Digital Management System.

This module acts as a wrapper that routes storage operations to either the
SQLite backend (storage_sqlite.py) or the legacy CSV backend based on
configuration settings.

DEPRECATION NOTICE:
The CSV backend is deprecated and maintained only for backward compatibility.
New deployments should use SQLite (use_sqlite=true in config.ini).

Migration Path:
1. On first run with use_sqlite=true, CSV data is automatically migrated
2. Future operations use SQLite exclusively
3. CSV export available via storage_sqlite.export_csv() for legacy needs
"""

from __future__ import annotations
import csv
import os
import shutil
import tempfile
import threading
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Iterable, List, Dict

from .rooms import AppConfig


# ============================================================================
# Backend Selection - Routes to SQLite or CSV based on config
# ============================================================================

def _get_backend(cfg: AppConfig):
    """
    Get the appropriate storage backend based on configuration.
    
    Args:
        cfg: Application configuration
        
    Returns:
        Module object (storage_sqlite or this module's CSV functions)
    """
    if getattr(cfg, 'use_sqlite', True):  # Default to SQLite
        from . import storage_sqlite
        return storage_sqlite
    else:
        # Return self for CSV backend (functions defined below)
        import sys
        return sys.modules[__name__]


# ============================================================================
# CSV Backend - Legacy Implementation (Deprecated)
# ============================================================================

@dataclass
class FilePaths:
    """Legacy CSV file paths structure."""
    data_dir: Path
    backup_dir: Path
    rooms: Path
    reservations: Path


def ensure_dirs(cfg: AppConfig) -> FilePaths:
    """
    Ensure CSV data directories and files exist.
    
    DEPRECATED: Use storage_sqlite.ensure_db() for new code.
    """
    cfg.data_dir.mkdir(parents=True, exist_ok=True)
    cfg.backup_dir.mkdir(parents=True, exist_ok=True)
    rooms = cfg.data_dir / 'rooms.csv'
    reservations = cfg.data_dir / 'reservations.csv'
    if not rooms.exists():
        rooms.write_text('room_id,room_type,base_price\n', encoding='utf-8')
    if not reservations.exists():
        reservations.write_text('reservation_id,room_id,guest_name,phone,email,check_in_date,check_out_date,num_guests,status,total_cost,created_at,updated_at\n', encoding='utf-8')
    return FilePaths(cfg.data_dir, cfg.backup_dir, rooms, reservations)


@contextmanager
def file_lock(lock_path: Path, timeout: float = 5.0):
    """
    Acquire exclusive file lock for atomic CSV operations.
    
    DEPRECATED: SQLite uses transactions instead of file locks.
    """
    lock_file = lock_path.with_suffix(lock_path.suffix + '.lock')
    start = datetime.now()
    while True:
        try:
            # O_CREAT|O_EXCL ensures exclusive creation
            fd = os.open(str(lock_file), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            os.close(fd)
            break
        except FileExistsError:
            if (datetime.now() - start).total_seconds() > timeout:
                raise TimeoutError(f"Timeout acquiring lock: {lock_file}")
    try:
        yield
    finally:
        try:
            lock_file.unlink(missing_ok=True)
        except Exception:
            pass


def read_csv(path: Path) -> List[Dict[str, str]]:
    """
    Read CSV file into list of dictionaries.
    
    DEPRECATED: Use storage_sqlite functions for new code.
    """
    if not path.exists():
        return []
    with path.open('r', newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        return list(reader)


def write_csv_atomic(path: Path, fieldnames: Iterable[str], rows: Iterable[Dict[str, str]]):
    """
    Atomically write CSV file using temp file + rename.
    
    DEPRECATED: SQLite uses transactions instead of atomic file writes.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    with file_lock(path):
        with tempfile.NamedTemporaryFile('w', delete=False, dir=str(path.parent), newline='', encoding='utf-8') as tf:
            writer = csv.DictWriter(tf, fieldnames=fieldnames)
            writer.writeheader()
            for row in rows:
                writer.writerow(row)
            tmp_name = tf.name
        os.replace(tmp_name, path)


def backup_now(cfg: AppConfig, fps: FilePaths | None = None):
    """
    Create backup of data files (CSV or SQLite based on config).
    
    Args:
        cfg: Application configuration
        fps: Legacy FilePaths (used only for CSV backend)
        
    Notes:
        Routes to appropriate backend's backup mechanism.
    """
    backend = _get_backend(cfg)
    
    if backend.__name__ == 'app.storage_sqlite':
        # Use SQLite backup
        backend.backup_db(cfg)
    else:
        # Use CSV backup (legacy)
        fps = fps or ensure_dirs(cfg)
        timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
        for csv_path in [fps.rooms, fps.reservations]:
            if csv_path.exists():
                dest = cfg.backup_dir / f"{timestamp}-{csv_path.name}"
                shutil.copy2(csv_path, dest)
        # Retention by modified time
        cutoff = datetime.now() - timedelta(days=cfg.backup_retention_days)
        for p in cfg.backup_dir.glob('*.csv'):
            try:
                mtime = datetime.fromtimestamp(p.stat().st_mtime)
                if mtime < cutoff:
                    p.unlink()
            except Exception:
                continue


def _parse_time(hhmm: str) -> datetime:
    """Parse HH:MM time string to next occurrence datetime."""
    now = datetime.now()
    hour, minute = map(int, hhmm.split(':'))
    target = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
    if target <= now:
        target += timedelta(days=1)
    return target


def start_daily_backup_scheduler(cfg: AppConfig):
    """
    Start background thread for daily backups.
    
    Args:
        cfg: Application configuration
        
    Returns:
        Thread object
        
    Notes:
        Works with both SQLite and CSV backends via backup_now() routing.
    """
    def _runner():
        while True:
            next_run = _parse_time(cfg.backup_time)
            sleep_secs = (next_run - datetime.now()).total_seconds()
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
