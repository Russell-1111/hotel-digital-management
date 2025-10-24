from __future__ import annotations
import csv
import os
import shutil
import tempfile
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Iterable, List, Dict

from .config import AppConfig


@dataclass
class FilePaths:
    data_dir: Path
    backup_dir: Path
    rooms: Path
    reservations: Path


def ensure_dirs(cfg: AppConfig) -> FilePaths:
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
    if not path.exists():
        return []
    with path.open('r', newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        return list(reader)


def write_csv_atomic(path: Path, fieldnames: Iterable[str], rows: Iterable[Dict[str, str]]):
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
    now = datetime.now()
    hour, minute = map(int, hhmm.split(':'))
    target = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
    if target <= now:
        target += timedelta(days=1)
    return target


def start_daily_backup_scheduler(cfg: AppConfig):
    import threading

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
