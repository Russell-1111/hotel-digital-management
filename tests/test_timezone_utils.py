"""
Tests for timezone utility functions.
Validates timezone conversions, DST handling, and edge cases.
"""

from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo
import pytest

from app.timezone_utils import (
    get_hotel_tz,
    now_utc,
    now_hotel,
    to_utc,
    to_hotel_tz,
    naive_to_aware_utc
)


class TestGetHotelTz:
    """Test get_hotel_tz function."""
    
    def test_valid_timezone_string(self):
        """Valid timezone string returns ZoneInfo object."""
        tz = get_hotel_tz("Asia/Kuala_Lumpur")
        assert isinstance(tz, ZoneInfo)
        assert str(tz) == "Asia/Kuala_Lumpur"
    
    def test_utc_timezone(self):
        """UTC timezone works correctly."""
        tz = get_hotel_tz("UTC")
        assert isinstance(tz, ZoneInfo)
        assert str(tz) == "UTC"
    
    def test_american_timezone(self):
        """American timezone with DST works."""
        tz = get_hotel_tz("America/New_York")
        assert isinstance(tz, ZoneInfo)
        assert str(tz) == "America/New_York"
    
    def test_invalid_timezone_raises_error(self):
        """Invalid timezone string raises ZoneInfoNotFoundError."""
        with pytest.raises(Exception):  # ZoneInfoNotFoundError in Python 3.9+
            get_hotel_tz("Invalid/Timezone")


class TestNowUtc:
    """Test now_utc function."""
    
    def test_returns_utc_datetime(self):
        """Returns datetime with UTC timezone."""
        dt = now_utc()
        assert isinstance(dt, datetime)
        assert dt.tzinfo == timezone.utc
    
    def test_is_current_time(self):
        """Returns current time (within 1 second)."""
        dt = now_utc()
        now = datetime.now(timezone.utc)
        delta = abs((dt - now).total_seconds())
        assert delta < 1.0  # Within 1 second


class TestNowHotel:
    """Test now_hotel function."""
    
    def test_returns_hotel_timezone_datetime(self):
        """Returns datetime in hotel timezone."""
        hotel_tz = ZoneInfo("Asia/Kuala_Lumpur")
        dt = now_hotel(hotel_tz)
        assert isinstance(dt, datetime)
        assert dt.tzinfo == hotel_tz
    
    def test_matches_utc_converted(self):
        """Hotel time matches UTC time converted to hotel timezone."""
        hotel_tz = ZoneInfo("America/New_York")
        dt_hotel = now_hotel(hotel_tz)
        dt_utc = now_utc().astimezone(hotel_tz)
        delta = abs((dt_hotel - dt_utc).total_seconds())
        assert delta < 1.0  # Within 1 second


class TestToUtc:
    """Test to_utc conversion function."""
    
    def test_converts_hotel_to_utc(self):
        """Converts hotel timezone datetime to UTC."""
        hotel_tz = ZoneInfo("Asia/Kuala_Lumpur")  # UTC+8
        hotel_dt = datetime(2025, 10, 24, 14, 30, 0, tzinfo=hotel_tz)
        utc_dt = to_utc(hotel_dt, hotel_tz)
        
        assert utc_dt.tzinfo == timezone.utc
        # 14:30 in KL is 06:30 UTC
        assert utc_dt.hour == 6
        assert utc_dt.minute == 30
    
    def test_converts_naive_to_utc(self):
        """Converts naive datetime (assumed hotel TZ) to UTC."""
        hotel_tz = ZoneInfo("Asia/Kuala_Lumpur")  # UTC+8
        naive_dt = datetime(2025, 10, 24, 14, 30, 0)  # No tzinfo
        utc_dt = to_utc(naive_dt, hotel_tz)
        
        assert utc_dt.tzinfo == timezone.utc
        # 14:30 in KL is 06:30 UTC
        assert utc_dt.hour == 6
        assert utc_dt.minute == 30
    
    def test_handles_dst_transition(self):
        """Correctly handles DST transitions."""
        ny_tz = ZoneInfo("America/New_York")
        # Before DST ends (EDT, UTC-4)
        before = datetime(2025, 11, 1, 14, 0, 0, tzinfo=ny_tz)
        utc_before = to_utc(before, ny_tz)
        # After DST ends (EST, UTC-5)
        after = datetime(2025, 12, 1, 14, 0, 0, tzinfo=ny_tz)
        utc_after = to_utc(after, ny_tz)
        
        # Both should be in UTC
        assert utc_before.tzinfo == timezone.utc
        assert utc_after.tzinfo == timezone.utc
        # Time difference should account for DST
        assert (utc_after.hour - utc_before.hour) % 24 == 1  # 1-hour offset difference


class TestToHotelTz:
    """Test to_hotel_tz conversion function."""
    
    def test_converts_utc_to_hotel(self):
        """Converts UTC datetime to hotel timezone."""
        hotel_tz = ZoneInfo("Asia/Kuala_Lumpur")  # UTC+8
        utc_dt = datetime(2025, 10, 24, 6, 30, 0, tzinfo=timezone.utc)
        hotel_dt = to_hotel_tz(utc_dt, hotel_tz)
        
        assert hotel_dt.tzinfo == hotel_tz
        # 06:30 UTC is 14:30 in KL
        assert hotel_dt.hour == 14
        assert hotel_dt.minute == 30
    
    def test_already_hotel_tz_unchanged(self):
        """Hotel timezone datetime remains unchanged."""
        hotel_tz = ZoneInfo("Asia/Tokyo")
        dt = datetime(2025, 10, 24, 15, 0, 0, tzinfo=hotel_tz)
        result = to_hotel_tz(dt, hotel_tz)
        assert result == dt
        assert result.tzinfo == hotel_tz
    
    def test_different_timezone_converts(self):
        """Converts from different timezone to hotel timezone."""
        source_tz = ZoneInfo("Europe/London")  # UTC+1 in summer
        hotel_tz = ZoneInfo("America/Los_Angeles")  # UTC-7 in summer
        
        source_dt = datetime(2025, 7, 15, 12, 0, 0, tzinfo=source_tz)
        hotel_dt = to_hotel_tz(source_dt, hotel_tz)
        
        assert hotel_dt.tzinfo == hotel_tz
        # Should maintain same instant in time, different local time


class TestNaiveToAwareUtc:
    """Test naive_to_aware_utc function."""
    
    def test_converts_naive_to_utc(self):
        """Converts naive datetime to UTC-aware."""
        hotel_tz = ZoneInfo("Asia/Kuala_Lumpur")
        naive_dt = datetime(2025, 10, 24, 14, 30, 0)
        assert naive_dt.tzinfo is None
        
        aware_dt = naive_to_aware_utc(naive_dt, hotel_tz)
        assert aware_dt.tzinfo == timezone.utc
        # 14:30 in KL is 06:30 UTC
        assert aware_dt.hour == 6
        assert aware_dt.minute == 30
    
    def test_raises_on_aware_datetime(self):
        """Raises ValueError if datetime is already aware."""
        hotel_tz = ZoneInfo("Asia/Kuala_Lumpur")
        aware_dt = datetime(2025, 10, 24, 14, 30, 0, tzinfo=timezone.utc)
        
        with pytest.raises(ValueError, match="Expected naive datetime"):
            naive_to_aware_utc(aware_dt, hotel_tz)
    
    def test_different_timezone_assumptions(self):
        """Different assumption timezones produce different UTC times."""
        naive_dt = datetime(2025, 10, 24, 14, 30, 0)
        
        kl_tz = ZoneInfo("Asia/Kuala_Lumpur")  # UTC+8
        ny_tz = ZoneInfo("America/New_York")  # UTC-4/5
        
        kl_utc = naive_to_aware_utc(naive_dt, kl_tz)
        ny_utc = naive_to_aware_utc(naive_dt, ny_tz)
        
        # Same local time, different timezones = different UTC times
        assert kl_utc != ny_utc
        assert kl_utc.tzinfo == timezone.utc
        assert ny_utc.tzinfo == timezone.utc


class TestTimezoneConversionRoundTrip:
    """Test round-trip conversions maintain correctness."""
    
    def test_utc_to_hotel_to_utc(self):
        """UTC → Hotel → UTC round trip."""
        hotel_tz = ZoneInfo("America/Chicago")
        original = datetime(2025, 10, 24, 10, 30, 0, tzinfo=timezone.utc)
        
        # Convert to hotel
        hotel = to_hotel_tz(original, hotel_tz)
        # Convert back to UTC
        back = to_utc(hotel, hotel_tz)
        
        assert back == original
    
    def test_hotel_to_utc_to_hotel(self):
        """Hotel → UTC → Hotel round trip."""
        hotel_tz = ZoneInfo("Europe/Paris")
        original = datetime(2025, 10, 24, 18, 0, 0, tzinfo=hotel_tz)
        
        # Convert to UTC
        utc = to_utc(original, hotel_tz)
        # Convert back to hotel
        back = to_hotel_tz(utc, hotel_tz)
        
        assert back == original
    
    def test_multiple_timezone_conversions(self):
        """Multiple conversions maintain same instant."""
        utc_dt = datetime(2025, 10, 24, 12, 0, 0, tzinfo=timezone.utc)
        
        # Convert through multiple timezones
        kl_tz = ZoneInfo("Asia/Kuala_Lumpur")
        ny_tz = ZoneInfo("America/New_York")
        la_tz = ZoneInfo("America/Los_Angeles")
        
        kl_dt = to_hotel_tz(utc_dt, kl_tz)
        ny_dt = to_utc(kl_dt, kl_tz)
        la_dt = to_hotel_tz(ny_dt, la_tz)
        final_utc = to_utc(la_dt, la_tz)
        
        # Should end up at same UTC time
        assert final_utc == utc_dt


class TestEdgeCases:
    """Test edge cases and boundary conditions."""
    
    def test_leap_year_february_29(self):
        """Handles leap year dates correctly."""
        hotel_tz = ZoneInfo("Asia/Singapore")
        leap_day = datetime(2024, 2, 29, 12, 0, 0, tzinfo=hotel_tz)
        utc = to_utc(leap_day, hotel_tz)
        back = to_hotel_tz(utc, hotel_tz)
        assert back.day == 29
        assert back.month == 2
    
    def test_year_boundary(self):
        """Handles year boundary (New Year's Eve/Day)."""
        hotel_tz = ZoneInfo("Pacific/Auckland")  # UTC+13 in summer
        # Dec 31, 2025, 23:00 in Auckland
        nye = datetime(2025, 12, 31, 23, 0, 0, tzinfo=hotel_tz)
        utc = to_utc(nye, hotel_tz)
        # Should be Dec 31, 2025 in UTC (10:00)
        assert utc.year == 2025
        assert utc.month == 12
        assert utc.day == 31
    
    def test_dst_spring_forward(self):
        """Handles DST spring forward (clock moves ahead)."""
        ny_tz = ZoneInfo("America/New_York")
        # In March 2025, DST starts (2:00 AM becomes 3:00 AM)
        # 1:30 AM exists
        before = datetime(2025, 3, 9, 1, 30, 0, tzinfo=ny_tz)
        # 3:30 AM exists (2:30 AM is skipped)
        after = datetime(2025, 3, 9, 3, 30, 0, tzinfo=ny_tz)
        
        utc_before = to_utc(before, ny_tz)
        utc_after = to_utc(after, ny_tz)
        
        # Time difference should be 1 hour (2 hours clock time - 1 hour DST skip)
        delta = (utc_after - utc_before).total_seconds()
        assert delta == 3600  # 1 hour
    
    def test_dst_fall_back(self):
        """Handles DST fall back (clock moves back)."""
        ny_tz = ZoneInfo("America/New_York")
        # In November 2025, DST ends (2:00 AM becomes 1:00 AM)
        # 1:30 AM occurs twice
        before = datetime(2025, 11, 2, 0, 30, 0, tzinfo=ny_tz, fold=0)
        after = datetime(2025, 11, 2, 2, 30, 0, tzinfo=ny_tz, fold=1)
        
        utc_before = to_utc(before, ny_tz)
        utc_after = to_utc(after, ny_tz)
        
        # Both should convert correctly
        assert utc_before.tzinfo == timezone.utc
        assert utc_after.tzinfo == timezone.utc
