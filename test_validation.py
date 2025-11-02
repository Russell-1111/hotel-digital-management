"""
Test script for reservation validation functionality.
"""

from app.reservations import validate_phone, validate_email, validate_guest_info


def test_phone_validation():
    """Test phone number validation."""
    print("Testing phone validation...")
    
    # Valid cases
    try:
        validate_phone("1234567890")
        print("✓ Valid phone: 1234567890")
    except ValueError as e:
        print(f"✗ Unexpected error: {e}")
    
    # Invalid cases
    test_cases = [
        ("123-456-7890", "Phone with dashes"),
        ("(123) 456-7890", "Phone with parentheses"),
        ("123 456 7890", "Phone with spaces"),
        ("123abc456", "Phone with letters"),
        ("", "Empty phone"),
        ("   ", "Whitespace phone"),
    ]
    
    for phone, description in test_cases:
        try:
            validate_phone(phone)
            print(f"✗ {description}: Should have raised error")
        except ValueError as e:
            print(f"✓ {description}: {e}")


def test_email_validation():
    """Test email validation."""
    print("\nTesting email validation...")
    
    # Valid cases
    valid_emails = [
        "user@gmail.com",
        "test.user@gmail.com",
        "contact@outlook.com",
        "USER@GMAIL.COM",
        "MixedCase@Outlook.com",
    ]
    
    for email in valid_emails:
        try:
            validate_email(email)
            print(f"✓ Valid email: {email}")
        except ValueError as e:
            print(f"✗ Unexpected error for {email}: {e}")
    
    # Invalid cases
    invalid_cases = [
        ("user@yahoo.com", "Yahoo email"),
        ("test@hotmail.com", "Hotmail email"),
        ("contact@company.com", "Generic domain"),
        ("plaintext", "No @ symbol"),
        ("user@", "No domain"),
        ("@gmail.com", "No username"),
        ("", "Empty email"),
        ("   ", "Whitespace email"),
        ("user@gmail", "Incomplete domain"),
    ]
    
    for email, description in invalid_cases:
        try:
            validate_email(email)
            print(f"✗ {description} ({email}): Should have raised error")
        except ValueError as e:
            print(f"✓ {description} ({email}): {e}")


def test_guest_info_validation():
    """Test complete guest info validation."""
    print("\nTesting complete guest info validation...")
    
    # Valid case
    try:
        validate_guest_info("John Doe", "1234567890", "john@gmail.com")
        print("✓ Valid guest info: All fields correct")
    except ValueError as e:
        print(f"✗ Unexpected error: {e}")
    
    # Invalid cases
    test_cases = [
        ("", "1234567890", "john@gmail.com", "Empty name"),
        ("   ", "1234567890", "john@gmail.com", "Whitespace name"),
        ("John Doe", "123-456-7890", "john@gmail.com", "Invalid phone"),
        ("John Doe", "1234567890", "john@yahoo.com", "Invalid email"),
        ("", "", "", "All empty"),
    ]
    
    for name, phone, email, description in test_cases:
        try:
            validate_guest_info(name, phone, email)
            print(f"✗ {description}: Should have raised error")
        except ValueError as e:
            print(f"✓ {description}: {e}")


if __name__ == "__main__":
    print("=" * 60)
    print("RESERVATION VALIDATION TESTS")
    print("=" * 60)
    test_phone_validation()
    test_email_validation()
    test_guest_info_validation()
    print("\n" + "=" * 60)
    print("TESTS COMPLETED")
    print("=" * 60)
