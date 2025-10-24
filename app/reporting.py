from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List, Dict

from .reservations import list_reservations, Reservation


def daily_checkin_list(reservations_path: Path, date_str: str) -> List[Reservation]:
    return [r for r in list_reservations(reservations_path) if r.check_in_date == date_str and r.status in {"Confirmed"}]


def daily_checkout_list(reservations_path: Path, date_str: str) -> List[Reservation]:
    return [r for r in list_reservations(reservations_path) if r.check_out_date == date_str and r.status in {"Checked-In"}]


def monthly_revenue_summary(reservations_path: Path, year_month: str) -> float:
    # year_month format: YYYY-MM
    res = 0.0
    rs = list_reservations(reservations_path)
    for r in rs:
        if r.check_out_date.startswith(year_month):
            res += float(r.total_cost)
    return round(res, 2)
