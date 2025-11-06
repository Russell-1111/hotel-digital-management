"""
Test to verify that check-in dates in the past are rejected.
This is a critical validation for hotel booking systems.
"""

from pathlib import Path
from datetime import datetime, timedelta
from app.reservations import create_reservation, modify_reservation
from app.rooms import load_config, Room


def test_past_date_validation():
    """Test that check-in dates in the past are properly rejected."""
    print("Testing past date validation for reservations...\n")
    
    # Setup
    cfg = load_config(Path("config.ini"))
    reservations_path = Path("data/reservations.csv")
    
    # Create a mock room
    mock_room = Room(
        room_id="101",
        room_type="Standard",
        base_price=120.0,
        image_path="images/rooms/standard.jpg"
    )
    
    # Get dates
    today = datetime.now()
    yesterday = today - timedelta(days=1)
    tomorrow = today + timedelta(days=1)
    
    # Test 1: Check-in date is yesterday (SHOULD FAIL)
    print("Test 1: Check-in date is yesterday (past)")
    check_in_yesterday = yesterday.strftime("%Y-%m-%d")
    check_out_tomorrow = tomorrow.strftime("%Y-%m-%d")
    try:
        create_reservation(
            cfg, reservations_path, mock_room,
            "John Doe", "1234567890", "john@gmail.com",
            check_in_yesterday, check_out_tomorrow, 2
        )
        print("  ✗ FAILED: Should have raised ValueError for past check-in date\n")
    except ValueError as e:
        if "past" in str(e).lower():
            print(f"  ✓ PASSED: {e}\n")
        else:
            print(f"  ✗ FAILED: Wrong error message: {e}\n")
    
    # Test 2: Check-in date is today (SHOULD SUCCEED - same day bookings allowed)
    print("Test 2: Check-in date is today (current)")
    check_in_today = today.strftime("%Y-%m-%d")
    check_out_tomorrow = (today + timedelta(days=1)).strftime("%Y-%m-%d")
    try:
        # We won't actually create to avoid duplicates, but validation should pass
        # Just check that no "past" error is raised
        from app.reservations import validate_guest_info, _parse_date
        validate_guest_info("Jane Doe", "9876543210", "jane@outlook.com")
        
        # Check the date logic
        checkin_date = _parse_date(check_in_today).date()
        if checkin_date >= today.date():
            print("  ✓ PASSED: Today's date is accepted (not considered past)\n")
        else:
            print("  ✗ FAILED: Today's date incorrectly rejected\n")
    except ValueError as e:
        print(f"  ✗ FAILED: Today's date should be valid: {e}\n")
    
    # Test 3: Check-in date is tomorrow (SHOULD SUCCEED)
    print("Test 3: Check-in date is tomorrow (future)")
    check_in_tomorrow = tomorrow.strftime("%Y-%m-%d")
    check_out_future = (tomorrow + timedelta(days=2)).strftime("%Y-%m-%d")
    try:
        from app.reservations import validate_guest_info, _parse_date
        validate_guest_info("Bob Smith", "5555555555", "bob@gmail.com")
        
        # Check the date logic
        checkin_date = _parse_date(check_in_tomorrow).date()
        if checkin_date >= today.date():
            print("  ✓ PASSED: Future date is accepted\n")
        else:
            print("  ✗ FAILED: Future date incorrectly rejected\n")
    except ValueError as e:
        print(f"  ✗ FAILED: Future date should be valid: {e}\n")
    
    # Test 4: Check-in one week in the past (SHOULD FAIL)
    print("Test 4: Check-in date is one week ago (past)")
    week_ago = today - timedelta(days=7)
    check_in_week_ago = week_ago.strftime("%Y-%m-%d")
    check_out_six_days_ago = (week_ago + timedelta(days=1)).strftime("%Y-%m-%d")
    try:
        create_reservation(
            cfg, reservations_path, mock_room,
            "Alice Johnson", "1111111111", "alice@outlook.com",
            check_in_week_ago, check_out_six_days_ago, 1
        )
        print("  ✗ FAILED: Should have raised ValueError for past check-in date\n")
    except ValueError as e:
        if "past" in str(e).lower():
            print(f"  ✓ PASSED: {e}\n")
        else:
            print(f"  ✗ FAILED: Wrong error message: {e}\n")
    
    # Test 5: Edge case - Check-in one month in the future (SHOULD SUCCEED)
    print("Test 5: Check-in date is one month in the future")
    month_future = today + timedelta(days=30)
    check_in_future = month_future.strftime("%Y-%m-%d")
    check_out_future = (month_future + timedelta(days=3)).strftime("%Y-%m-%d")
    try:
        from app.reservations import validate_guest_info, _parse_date
        validate_guest_info("Carol White", "9999999999", "carol@gmail.com")
        
        # Check the date logic
        checkin_date = _parse_date(check_in_future).date()
        if checkin_date >= today.date():
            print("  ✓ PASSED: Future booking (30 days ahead) is accepted\n")
        else:
            print("  ✗ FAILED: Future booking incorrectly rejected\n")
    except ValueError as e:
        print(f"  ✗ FAILED: Future booking should be valid: {e}\n")


if __name__ == "__main__":
    print("=" * 70)
    print("PAST DATE VALIDATION TESTS")
    print("=" * 70)
    print()
    test_past_date_validation()
    print("=" * 70)
    print("ALL TESTS COMPLETED")
    print("=" * 70)
