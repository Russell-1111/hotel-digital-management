"""
Test script to verify validation in both create and modify operations.
"""

from pathlib import Path
from datetime import datetime, timedelta
from app.reservations import (
    create_reservation, 
    modify_reservation, 
    list_reservations,
    cancel_reservation
)
from app.rooms import load_config, Room


def test_modify_validation():
    """Test validation when modifying reservations."""
    print("Testing reservation modification validation...\n")
    
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
    check_in = (today + timedelta(days=30)).strftime("%Y-%m-%d")
    check_out = (today + timedelta(days=32)).strftime("%Y-%m-%d")
    
    # First, create a valid reservation for testing modifications
    print("Creating a valid test reservation...")
    try:
        reservation = create_reservation(
            cfg, reservations_path, mock_room,
            "Test User", "1111111111", "test.validation@gmail.com",
            check_in, check_out, 1
        )
        print(f"  ✓ Test reservation created: {reservation.reservation_id}\n")
        res_id = reservation.reservation_id
    except Exception as e:
        print(f"  ✗ Failed to create test reservation: {e}\n")
        return
    
    try:
        # Test 1: Modify with invalid phone
        print("Test 1: Modify with invalid phone number")
        try:
            modify_reservation(
                cfg, reservations_path, res_id,
                new_phone="123-456-7890"
            )
            print("  ✗ FAILED: Should have raised ValueError\n")
        except ValueError as e:
            print(f"  ✓ PASSED: {e}\n")
        
        # Test 2: Modify with invalid email
        print("Test 2: Modify with invalid email domain")
        try:
            modify_reservation(
                cfg, reservations_path, res_id,
                new_email="test@yahoo.com"
            )
            print("  ✗ FAILED: Should have raised ValueError\n")
        except ValueError as e:
            print(f"  ✓ PASSED: {e}\n")
        
        # Test 3: Modify with empty name
        print("Test 3: Modify with empty guest name")
        try:
            modify_reservation(
                cfg, reservations_path, res_id,
                new_guest_name=""
            )
            print("  ✗ FAILED: Should have raised ValueError\n")
        except ValueError as e:
            print(f"  ✓ PASSED: {e}\n")
        
        # Test 4: Modify with valid phone (digits only)
        print("Test 4: Modify with valid phone number")
        try:
            result = modify_reservation(
                cfg, reservations_path, res_id,
                new_phone="9999999999"
            )
            if result:
                print("  ✓ PASSED: Phone number updated successfully\n")
            else:
                print("  ✗ FAILED: Modification returned False\n")
        except ValueError as e:
            print(f"  ✗ FAILED: {e}\n")
        
        # Test 5: Modify with valid email (@outlook.com)
        print("Test 5: Modify with valid email (@outlook.com)")
        try:
            result = modify_reservation(
                cfg, reservations_path, res_id,
                new_email="updated.email@outlook.com"
            )
            if result:
                print("  ✓ PASSED: Email updated successfully\n")
            else:
                print("  ✗ FAILED: Modification returned False\n")
        except ValueError as e:
            print(f"  ✗ FAILED: {e}\n")
        
        # Test 6: Modify with valid name
        print("Test 6: Modify with valid guest name")
        try:
            result = modify_reservation(
                cfg, reservations_path, res_id,
                new_guest_name="Updated Test User"
            )
            if result:
                print("  ✓ PASSED: Guest name updated successfully\n")
            else:
                print("  ✗ FAILED: Modification returned False\n")
        except ValueError as e:
            print(f"  ✗ FAILED: {e}\n")
        
        # Test 7: Verify the modifications were saved
        print("Test 7: Verify modifications were saved")
        reservations = list_reservations(reservations_path)
        updated = next((r for r in reservations if r.reservation_id == res_id), None)
        
        if updated:
            checks = [
                (updated.guest_name == "Updated Test User", "Guest name"),
                (updated.phone == "9999999999", "Phone number"),
                (updated.email == "updated.email@outlook.com", "Email")
            ]
            
            all_passed = True
            for check, field in checks:
                if check:
                    print(f"  ✓ {field} correctly updated")
                else:
                    print(f"  ✗ {field} not updated correctly")
                    all_passed = False
            
            if all_passed:
                print("\n  ✓ PASSED: All modifications saved correctly\n")
            else:
                print("\n  ✗ FAILED: Some modifications not saved\n")
        else:
            print("  ✗ FAILED: Could not find updated reservation\n")
        
    finally:
        # Clean up: Cancel the test reservation
        print("Cleaning up test reservation...")
        try:
            cancel_reservation(reservations_path, res_id)
            print(f"  ✓ Test reservation {res_id} cancelled\n")
        except Exception as e:
            print(f"  ✗ Failed to cancel test reservation: {e}\n")


if __name__ == "__main__":
    print("=" * 70)
    print("RESERVATION MODIFICATION VALIDATION TESTS")
    print("=" * 70)
    print()
    test_modify_validation()
    print("=" * 70)
    print("ALL TESTS COMPLETED")
    print("=" * 70)
