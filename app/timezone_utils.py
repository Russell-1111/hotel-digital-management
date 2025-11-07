"""Timezone utilities for hotel management system.

This module provides helper functions for timezone-aware datetime operations,
ensuring all timestamps are stored in UTC while allowing hotel operations to
follow the configured local timezone.
"""

from datetime import datetime, timezone
from zoneinfo import ZoneInfo


def get_hotel_tz(tz_name: str) -> ZoneInfo:
    """
    Load and return a timezone object for the hotel's configured timezone.
    
    Args:
        tz_name: IANA timezone name (e.g., 'Asia/Kuala_Lumpur', 'UTC')
        
    Returns:
        ZoneInfo object for the specified timezone
        
    Raises:
        ZoneInfoNotFoundError: If timezone name is invalid
    """
    return ZoneInfo(tz_name)


def now_utc() -> datetime:
    """
    Get current time in UTC as a timezone-aware datetime.
    
    Returns:
        Timezone-aware datetime in UTC
        
    Example:
        >>> dt = now_utc()
        >>> dt.tzinfo == timezone.utc
        True
    """
    return datetime.now(timezone.utc)


def now_hotel(tz: ZoneInfo) -> datetime:
    """
    Get current time in the hotel's timezone as a timezone-aware datetime.
    
    Args:
        tz: Hotel's timezone (from get_hotel_tz)
        
    Returns:
        Timezone-aware datetime in hotel's local timezone
        
    Example:
        >>> tz = get_hotel_tz('Asia/Kuala_Lumpur')
        >>> dt = now_hotel(tz)
        >>> dt.tzinfo == tz
        True
    """
    return datetime.now(timezone.utc).astimezone(tz)


def to_utc(dt: datetime, tz: ZoneInfo) -> datetime:
    """
    Convert a naive or timezone-aware datetime to UTC.
    
    Args:
        dt: Datetime to convert (if naive, assumed to be in tz)
        tz: Timezone to assume if dt is naive
        
    Returns:
        Timezone-aware datetime in UTC
        
    Example:
        >>> tz = get_hotel_tz('Asia/Kuala_Lumpur')
        >>> local_dt = datetime(2025, 11, 7, 14, 0, 0)  # naive
        >>> utc_dt = to_utc(local_dt, tz)
        >>> utc_dt.hour
        6  # 14:00 +08:00 = 06:00 UTC
    """
    if dt.tzinfo is None:
        # Naive datetime - assume it's in the specified timezone
        dt = dt.replace(tzinfo=tz)
    return dt.astimezone(timezone.utc)


def to_hotel_tz(dt_utc: datetime, tz: ZoneInfo) -> datetime:
    """
    Convert a UTC datetime to the hotel's local timezone.
    
    Args:
        dt_utc: Timezone-aware datetime in UTC
        tz: Hotel's timezone
        
    Returns:
        Timezone-aware datetime in hotel's local timezone
        
    Example:
        >>> tz = get_hotel_tz('Asia/Kuala_Lumpur')
        >>> utc_dt = datetime(2025, 11, 7, 6, 0, 0, tzinfo=timezone.utc)
        >>> local_dt = to_hotel_tz(utc_dt, tz)
        >>> local_dt.hour
        14  # 06:00 UTC = 14:00 +08:00
    """
    return dt_utc.astimezone(tz)


def naive_to_aware_utc(naive_dt: datetime, assume_tz: ZoneInfo) -> datetime:
    """
    Convert a naive datetime to timezone-aware UTC datetime.
    
    This is a migration helper that interprets naive timestamps as being
    in the hotel's local timezone and converts them to UTC.
    
    Args:
        naive_dt: Naive datetime (no tzinfo)
        assume_tz: Timezone to assume for the naive datetime
        
    Returns:
        Timezone-aware datetime in UTC
        
    Raises:
        ValueError: If dt is already timezone-aware
        
    Example:
        >>> tz = get_hotel_tz('Asia/Kuala_Lumpur')
        >>> naive = datetime(2025, 11, 7, 14, 30, 0)
        >>> aware = naive_to_aware_utc(naive, tz)
        >>> aware.tzinfo == timezone.utc
        True
        >>> aware.hour
        6  # 14:30 +08:00 = 06:30 UTC
    """
    if naive_dt.tzinfo is not None:
        raise ValueError(f"Expected naive datetime, got timezone-aware: {naive_dt}")
    
    # Attach the assumed timezone to the naive datetime
    local_dt = naive_dt.replace(tzinfo=assume_tz)
    
    # Convert to UTC
    return local_dt.astimezone(timezone.utc)
