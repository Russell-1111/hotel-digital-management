"""
Integration test for reservation validation.
This test verifies that reservations cannot be created with invalid data.
"""

from pathlib import Path
from datetime import datetime, timedelta
from app.reservations import create_reservation, validate_guest_info
from app.rooms import load_config, Room


def test_create_reservation_validation():
    """Test that create_reservation properly validates inputs."""
    print("Testing reservation creation validation...\n")
    
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
    check_in = today.strftime("%Y-%m-%d")
    check_out = (today + timedelta(days=2)).strftime("%Y-%m-%d")
    
    # Test 1: Empty guest name
    print("Test 1: Empty guest name")
    try:
        create_reservation(
            cfg, reservations_path, mock_room,
            "", "1234567890", "test@gmail.com",
            check_in, check_out, 2
        )
        print("  ✗ FAILED: Should have raised ValueError\n")
    except ValueError as e:
        print(f"  ✓ PASSED: {e}\n")
    
    # Test 2: Invalid phone (with dashes)
    print("Test 2: Invalid phone number (with dashes)")
    try:
        create_reservation(
            cfg, reservations_path, mock_room,
            "John Doe", "123-456-7890", "test@gmail.com",
            check_in, check_out, 2
        )
        print("  ✗ FAILED: Should have raised ValueError\n")
    except ValueError as e:
        print(f"  ✓ PASSED: {e}\n")
    
    # Test 3: Invalid phone (with letters)
    print("Test 3: Invalid phone number (with letters)")
    try:
        create_reservation(
            cfg, reservations_path, mock_room,
            "John Doe", "123abc4567", "test@gmail.com",
            check_in, check_out, 2
        )
        print("  ✗ FAILED: Should have raised ValueError\n")
    except ValueError as e:
        print(f"  ✓ PASSED: {e}\n")
    
    # Test 4: Invalid email (yahoo.com)
    print("Test 4: Invalid email domain (yahoo.com)")
    try:
        create_reservation(
            cfg, reservations_path, mock_room,
            "John Doe", "1234567890", "test@yahoo.com",
            check_in, check_out, 2
        )
        print("  ✗ FAILED: Should have raised ValueError\n")
    except ValueError as e:
        print(f"  ✓ PASSED: {e}\n")
    
    # Test 5: Invalid email (no domain extension)
    print("Test 5: Invalid email (no proper domain)")
    try:
        create_reservation(
            cfg, reservations_path, mock_room,
            "John Doe", "1234567890", "testuser",
            check_in, check_out, 2
        )
        print("  ✗ FAILED: Should have raised ValueError\n")
    except ValueError as e:
        print(f"  ✓ PASSED: {e}\n")
    
    # Test 6: Valid gmail.com email
    print("Test 6: Valid email (@gmail.com)")
    try:
        # Just validate, don't actually create to avoid duplicates
        validate_guest_info("John Doe", "1234567890", "john.doe@gmail.com")
        print("  ✓ PASSED: Email accepted\n")
    except ValueError as e:
        print(f"  ✗ FAILED: {e}\n")
    
    # Test 7: Valid outlook.com email
    print("Test 7: Valid email (@outlook.com)")
    try:
        validate_guest_info("Jane Smith", "9876543210", "jane.smith@outlook.com")
        print("  ✓ PASSED: Email accepted\n")
    except ValueError as e:
        print(f"  ✗ FAILED: {e}\n")
    
    # Test 8: Empty email
    print("Test 8: Empty email")
    try:
        create_reservation(
            cfg, reservations_path, mock_room,
            "John Doe", "1234567890", "",
            check_in, check_out, 2
        )
        print("  ✗ FAILED: Should have raised ValueError\n")
    except ValueError as e:
        print(f"  ✓ PASSED: {e}\n")
    
    # Test 9: Empty phone
    print("Test 9: Empty phone")
    try:
        create_reservation(
            cfg, reservations_path, mock_room,
            "John Doe", "", "test@gmail.com",
            check_in, check_out, 2
        )
        print("  ✗ FAILED: Should have raised ValueError\n")
    except ValueError as e:
        print(f"  ✓ PASSED: {e}\n")
    
    # Test 10: All fields valid (case insensitive email)
    print("Test 10: Valid data with uppercase email domain")
    try:
        validate_guest_info("John Doe", "1234567890", "TEST@GMAIL.COM")
        print("  ✓ PASSED: All validation checks passed\n")
    except ValueError as e:
        print(f"  ✗ FAILED: {e}\n")


if __name__ == "__main__":
    print("=" * 70)
    print("RESERVATION VALIDATION INTEGRATION TESTS")
    print("=" * 70)
    print()
    test_create_reservation_validation()
    print("=" * 70)
    print("ALL TESTS COMPLETED")
    print("=" * 70)
