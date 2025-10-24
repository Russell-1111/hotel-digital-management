from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List

from .storage import read_csv


@dataclass
class Room:
    room_id: str
    room_type: str
    base_price: float


def load_rooms(path: Path) -> List[Room]:
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
        ))
    return result


def index_by_id(rooms: List[Room]) -> Dict[str, Room]:
    return {r.room_id: r for r in rooms}
