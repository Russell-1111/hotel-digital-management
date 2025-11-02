"""
Interactive demonstration of the validation system.
Run this to see validation in action with example inputs.
"""

from app.reservations import validate_guest_info


def demo_validation():
    """Interactive demonstration of validation rules."""
    print("\n" + "=" * 70)
    print("RESERVATION VALIDATION SYSTEM - INTERACTIVE DEMO")
    print("=" * 70)
    print("\nThis demo shows how the validation system works.\n")
    
    # Demo 1: Valid reservation
    print("─" * 70)
    print("EXAMPLE 1: Valid Reservation")
    print("─" * 70)
    print("Input:")
    print("  Guest Name: John Doe")
    print("  Phone: 1234567890")
    print("  Email: john.doe@gmail.com")
    print("\nValidation Result:")
    try:
        validate_guest_info("John Doe", "1234567890", "john.doe@gmail.com")
        print("  ✅ SUCCESS - All fields are valid!")
        print("  → Reservation would be created")
    except ValueError as e:
        print(f"  ❌ ERROR: {e}")
    
    # Demo 2: Invalid phone (with dashes)
    print("\n" + "─" * 70)
    print("EXAMPLE 2: Invalid Phone Number (contains dashes)")
    print("─" * 70)
    print("Input:")
    print("  Guest Name: Jane Smith")
    print("  Phone: 123-456-7890")
    print("  Email: jane.smith@outlook.com")
    print("\nValidation Result:")
    try:
        validate_guest_info("Jane Smith", "123-456-7890", "jane.smith@outlook.com")
        print("  ✅ SUCCESS")
    except ValueError as e:
        print(f"  ❌ ERROR: {e}")
        print("  → Staff must remove dashes and enter: 1234567890")
    
    # Demo 3: Invalid email domain
    print("\n" + "─" * 70)
    print("EXAMPLE 3: Invalid Email Domain")
    print("─" * 70)
    print("Input:")
    print("  Guest Name: Bob Johnson")
    print("  Phone: 9876543210")
    print("  Email: bob@yahoo.com")
    print("\nValidation Result:")
    try:
        validate_guest_info("Bob Johnson", "9876543210", "bob@yahoo.com")
        print("  ✅ SUCCESS")
    except ValueError as e:
        print(f"  ❌ ERROR: {e}")
        print("  → Staff must request Gmail or Outlook email")
    
    # Demo 4: Empty fields
    print("\n" + "─" * 70)
    print("EXAMPLE 4: Empty Guest Name")
    print("─" * 70)
    print("Input:")
    print("  Guest Name: (empty)")
    print("  Phone: 5555555555")
    print("  Email: guest@gmail.com")
    print("\nValidation Result:")
    try:
        validate_guest_info("", "5555555555", "guest@gmail.com")
        print("  ✅ SUCCESS")
    except ValueError as e:
        print(f"  ❌ ERROR: {e}")
        print("  → Staff must fill in the guest name")
    
    # Demo 5: Phone with spaces
    print("\n" + "─" * 70)
    print("EXAMPLE 5: Phone Number with Spaces")
    print("─" * 70)
    print("Input:")
    print("  Guest Name: Alice Wong")
    print("  Phone: 012 345 6789")
    print("  Email: alice@outlook.com")
    print("\nValidation Result:")
    try:
        validate_guest_info("Alice Wong", "012 345 6789", "alice@outlook.com")
        print("  ✅ SUCCESS")
    except ValueError as e:
        print(f"  ❌ ERROR: {e}")
        print("  → Staff must remove spaces and enter: 0123456789")
    
    # Demo 6: Valid with uppercase email
    print("\n" + "─" * 70)
    print("EXAMPLE 6: Valid with Uppercase Email")
    print("─" * 70)
    print("Input:")
    print("  Guest Name: Charlie Brown")
    print("  Phone: 7777777777")
    print("  Email: CHARLIE@GMAIL.COM")
    print("\nValidation Result:")
    try:
        validate_guest_info("Charlie Brown", "7777777777", "CHARLIE@GMAIL.COM")
        print("  ✅ SUCCESS - All fields are valid!")
        print("  → Email case doesn't matter (case-insensitive)")
        print("  → Reservation would be created")
    except ValueError as e:
        print(f"  ❌ ERROR: {e}")
    
    # Demo 7: Multiple errors
    print("\n" + "─" * 70)
    print("EXAMPLE 7: Multiple Validation Errors")
    print("─" * 70)
    print("Input:")
    print("  Guest Name: (empty)")
    print("  Phone: (empty)")
    print("  Email: (empty)")
    print("\nValidation Result:")
    try:
        validate_guest_info("", "", "")
        print("  ✅ SUCCESS")
    except ValueError as e:
        print(f"  ❌ ERROR: {e}")
        print("  → System shows the first error encountered")
        print("  → Staff must fill in all required fields")
    
    # Summary
    print("\n" + "=" * 70)
    print("VALIDATION RULES SUMMARY")
    print("=" * 70)
    print("\n✓ Guest Name: Must not be empty")
    print("✓ Phone: Must contain only digits (0-9)")
    print("✓ Email: Must end with @gmail.com or @outlook.com")
    print("\n" + "=" * 70)
    print("\nFor more information, see:")
    print("  • STAFF_VALIDATION_GUIDE.md - Quick reference for staff")
    print("  • VALIDATION_IMPLEMENTATION.md - Technical details")
    print("  • VALIDATION_SUMMARY.md - Implementation summary")
    print("\n" + "=" * 70 + "\n")


if __name__ == "__main__":
    demo_validation()
