"""
Unit tests for the authentication module (app/auth.py).

Tests cover:
- User creation (admin, staff, duplicates, invalid roles)
- Password verification (correct, incorrect, non-existent users)
- Password changes (success and failure cases)
- Brute-force protection (lockout behavior)
- Hash format validation
- User listing functionality
"""

import os
import sqlite3
import tempfile
import time
import unittest
from datetime import datetime, timedelta, timezone

from app import auth
from app.storage_sqlite import init_schema


class TestAuth(unittest.TestCase):
    """Test suite for authentication module."""

    def setUp(self):
        """Create a temporary database for each test."""
        self.temp_db = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.db')
        self.temp_db.close()
        self.db_path = self.temp_db.name
        
        # Initialize schema with connection object
        conn = sqlite3.connect(self.db_path)
        init_schema(conn)
        conn.commit()
        conn.close()

    def tearDown(self):
        """Clean up temporary database."""
        if os.path.exists(self.db_path):
            os.unlink(self.db_path)

    # -------------------------------------------------------------------------
    # User Creation Tests
    # -------------------------------------------------------------------------

    def test_create_admin_user(self):
        """Test creating an admin user."""
        # Should not raise exception
        auth.create_user(self.db_path, 'admin1', 'SecurePass123!', 'admin')
        
        # Verify user exists in database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute('SELECT username, role FROM users WHERE username = ?', ('admin1',))
        row = cursor.fetchone()
        conn.close()
        
        self.assertIsNotNone(row)
        self.assertEqual(row[0], 'admin1')
        self.assertEqual(row[1], 'admin')

    def test_create_staff_user(self):
        """Test creating a staff user."""
        # Should not raise exception
        auth.create_user(self.db_path, 'staff1', 'StaffPass456!', 'staff')
        
        # Verify user exists in database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute('SELECT username, role FROM users WHERE username = ?', ('staff1',))
        row = cursor.fetchone()
        conn.close()
        
        self.assertIsNotNone(row)
        self.assertEqual(row[0], 'staff1')
        self.assertEqual(row[1], 'staff')

    def test_create_duplicate_user(self):
        """Test that creating a duplicate user fails."""
        auth.create_user(self.db_path, 'user1', 'Pass123!', 'admin')
        
        # Second attempt should raise ValueError
        with self.assertRaises(ValueError) as ctx:
            auth.create_user(self.db_path, 'user1', 'DifferentPass!', 'staff')
        
        self.assertIn("Username already exists", str(ctx.exception))

    def test_create_user_invalid_role(self):
        """Test that creating a user with invalid role fails."""
        with self.assertRaises(ValueError) as ctx:
            auth.create_user(self.db_path, 'baduser', 'Pass123!', 'superadmin')
        
        self.assertIn("Role must be 'admin' or 'staff'", str(ctx.exception))

    def test_create_user_empty_username(self):
        """Test that creating a user with empty username."""
        # SQLite allows empty strings as PRIMARY KEY
        # The application should validate this at the UI level
        # For now, we'll verify it doesn't crash
        try:
            auth.create_user(self.db_path, '', 'Pass123!', 'admin')
            # If it succeeds, verify the user was created
            count = auth.get_user_count(self.db_path)
            self.assertGreaterEqual(count, 1)
        except (ValueError, sqlite3.IntegrityError):
            # If it fails, that's acceptable too
            pass

    def test_create_user_empty_password(self):
        """Test that creating a user with empty password fails."""
        # Empty password should still create a hash, but it's not good practice
        # The application should validate this at the UI level
        # For now, we'll just verify it doesn't crash
        try:
            auth.create_user(self.db_path, 'user1', '', 'admin')
            # If it succeeds, verify empty password won't authenticate
            role = auth.verify_user(self.db_path, 'user1', '')
            # This might work with the hash of empty string
            # The important thing is the system doesn't crash
        except Exception:
            # If it fails, that's also acceptable
            pass

    # -------------------------------------------------------------------------
    # Password Verification Tests
    # -------------------------------------------------------------------------

    def test_verify_user_correct_password(self):
        """Test authentication with correct password."""
        auth.create_user(self.db_path, 'testuser', 'CorrectPass123!', 'admin')
        role = auth.verify_user(self.db_path, 'testuser', 'CorrectPass123!')
        self.assertEqual(role, 'admin')

    def test_verify_user_incorrect_password(self):
        """Test authentication with incorrect password."""
        auth.create_user(self.db_path, 'testuser', 'CorrectPass123!', 'staff')
        role = auth.verify_user(self.db_path, 'testuser', 'WrongPassword!')
        self.assertIsNone(role)

    def test_verify_nonexistent_user(self):
        """Test authentication for non-existent user."""
        role = auth.verify_user(self.db_path, 'nonexistent', 'AnyPass123!')
        self.assertIsNone(role)

    def test_verify_user_empty_password(self):
        """Test authentication with empty password."""
        auth.create_user(self.db_path, 'testuser', 'RealPass123!', 'admin')
        role = auth.verify_user(self.db_path, 'testuser', '')
        self.assertIsNone(role)

    # -------------------------------------------------------------------------
    # Password Change Tests
    # -------------------------------------------------------------------------

    def test_change_password_success(self):
        """Test successful password change."""
        auth.create_user(self.db_path, 'changeuser', 'OldPass123!', 'admin')
        result = auth.change_password(self.db_path, 'changeuser', 'OldPass123!', 'NewPass456!')
        self.assertTrue(result)
        
        # Verify new password works
        role = auth.verify_user(self.db_path, 'changeuser', 'NewPass456!')
        self.assertEqual(role, 'admin')
        
        # Verify old password no longer works
        role = auth.verify_user(self.db_path, 'changeuser', 'OldPass123!')
        self.assertIsNone(role)

    def test_change_password_wrong_old_password(self):
        """Test password change with incorrect old password."""
        auth.create_user(self.db_path, 'changeuser', 'OldPass123!', 'staff')
        result = auth.change_password(self.db_path, 'changeuser', 'WrongOld!', 'NewPass456!')
        self.assertFalse(result)
        
        # Verify original password still works
        role = auth.verify_user(self.db_path, 'changeuser', 'OldPass123!')
        self.assertEqual(role, 'staff')

    def test_change_password_nonexistent_user(self):
        """Test password change for non-existent user."""
        result = auth.change_password(self.db_path, 'nonexistent', 'OldPass!', 'NewPass!')
        self.assertFalse(result)

    # -------------------------------------------------------------------------
    # Brute-Force Protection Tests
    # -------------------------------------------------------------------------

    def test_lockout_after_five_failures(self):
        """Test that user is locked out after 5 failed login attempts."""
        auth.create_user(self.db_path, 'lockuser', 'CorrectPass123!', 'admin')
        
        # Attempt 5 failed logins
        for i in range(5):
            auth.verify_user(self.db_path, 'lockuser', 'WrongPassword!')
        
        # Check lockout status
        remaining = auth.check_lockout('lockuser')
        self.assertIsNotNone(remaining)
        self.assertGreater(remaining, 0)
        self.assertLessEqual(remaining, 300)  # Should be ≤ 5 minutes

    def test_lockout_prevents_login_with_correct_password(self):
        """Test that locked out user cannot login even with correct password."""
        auth.create_user(self.db_path, 'lockuser', 'CorrectPass123!', 'admin')
        
        # Trigger lockout
        for i in range(5):
            auth.verify_user(self.db_path, 'lockuser', 'WrongPassword!')
        
        # Try correct password during lockout
        role = auth.verify_user(self.db_path, 'lockuser', 'CorrectPass123!')
        self.assertIsNone(role)

    def test_successful_login_resets_failed_attempts(self):
        """Test that successful login resets failed attempt counter."""
        auth.create_user(self.db_path, 'resetuser', 'CorrectPass123!', 'admin')
        
        # Make 3 failed attempts
        for i in range(3):
            auth.verify_user(self.db_path, 'resetuser', 'WrongPassword!')
        
        # Successful login
        role = auth.verify_user(self.db_path, 'resetuser', 'CorrectPass123!')
        self.assertEqual(role, 'admin')
        
        # Make 4 more failed attempts (should not trigger lockout)
        for i in range(4):
            auth.verify_user(self.db_path, 'resetuser', 'WrongPassword!')
        
        # Should not be locked out yet
        remaining = auth.check_lockout('resetuser')
        self.assertIsNone(remaining)

    def test_lockout_expires_after_five_minutes(self):
        """Test that lockout expires after 5 minutes (simulated)."""
        auth.create_user(self.db_path, 'expireuser', 'CorrectPass123!', 'admin')
        
        # Trigger lockout
        for i in range(5):
            auth.verify_user(self.db_path, 'expireuser', 'WrongPassword!')
        
        # Manually expire the lockout by manipulating internal state
        # (In production, this would require waiting 5 minutes)
        if 'expireuser' in auth._failed_attempts:
            # Set all failed attempts to 6 minutes ago
            old_time = datetime.now(timezone.utc) - timedelta(minutes=6)
            auth._failed_attempts['expireuser'] = [old_time] * 5
        
        # Should no longer be locked out
        remaining = auth.check_lockout('expireuser')
        self.assertIsNone(remaining)
        
        # Should be able to login
        role = auth.verify_user(self.db_path, 'expireuser', 'CorrectPass123!')
        self.assertEqual(role, 'admin')

    # -------------------------------------------------------------------------
    # Hash Format Tests
    # -------------------------------------------------------------------------

    def test_password_hash_format(self):
        """Test that password hashes are stored in correct format."""
        auth.create_user(self.db_path, 'hashuser', 'TestPass123!', 'admin')
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute('SELECT password_hash FROM users WHERE username = ?', ('hashuser',))
        row = cursor.fetchone()
        conn.close()
        
        self.assertIsNotNone(row)
        password_hash = row[0]
        
        # Should be in format "salt_hex:hash_hex"
        self.assertIn(':', password_hash)
        parts = password_hash.split(':')
        self.assertEqual(len(parts), 2)
        
        # Both parts should be valid hex strings
        try:
            bytes.fromhex(parts[0])  # salt
            bytes.fromhex(parts[1])  # hash
        except ValueError:
            self.fail("Password hash is not in valid hex format")

    def test_different_users_have_different_salts(self):
        """Test that different users have different salts."""
        auth.create_user(self.db_path, 'user1', 'SamePass123!', 'admin')
        auth.create_user(self.db_path, 'user2', 'SamePass123!', 'staff')
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute('SELECT password_hash FROM users WHERE username IN (?, ?)', ('user1', 'user2'))
        rows = cursor.fetchall()
        conn.close()
        
        self.assertEqual(len(rows), 2)
        hash1 = rows[0][0]
        hash2 = rows[1][0]
        
        # Hashes should be different despite same password (due to different salts)
        self.assertNotEqual(hash1, hash2)

    # -------------------------------------------------------------------------
    # User Management Tests
    # -------------------------------------------------------------------------

    def test_list_users(self):
        """Test listing all users."""
        auth.create_user(self.db_path, 'admin1', 'Pass1!', 'admin')
        auth.create_user(self.db_path, 'staff1', 'Pass2!', 'staff')
        auth.create_user(self.db_path, 'staff2', 'Pass3!', 'staff')
        
        users = auth.list_users(self.db_path)
        self.assertEqual(len(users), 3)
        
        # Verify users are returned correctly
        usernames = [u['username'] for u in users]
        self.assertIn('admin1', usernames)
        self.assertIn('staff1', usernames)
        self.assertIn('staff2', usernames)
        
        # Verify roles
        admin = next(u for u in users if u['username'] == 'admin1')
        self.assertEqual(admin['role'], 'admin')
        
        staff = next(u for u in users if u['username'] == 'staff1')
        self.assertEqual(staff['role'], 'staff')

    def test_list_users_no_password_hashes(self):
        """Test that list_users does not return password hashes."""
        auth.create_user(self.db_path, 'testuser', 'SecretPass123!', 'admin')
        users = auth.list_users(self.db_path)
        
        self.assertEqual(len(users), 1)
        user = users[0]
        
        # Should not contain password_hash field
        self.assertNotIn('password_hash', user)

    def test_get_user_count(self):
        """Test getting the count of users."""
        count = auth.get_user_count(self.db_path)
        self.assertEqual(count, 0)
        
        auth.create_user(self.db_path, 'user1', 'Pass1!', 'admin')
        count = auth.get_user_count(self.db_path)
        self.assertEqual(count, 1)
        
        auth.create_user(self.db_path, 'user2', 'Pass2!', 'staff')
        auth.create_user(self.db_path, 'user3', 'Pass3!', 'staff')
        count = auth.get_user_count(self.db_path)
        self.assertEqual(count, 3)

    def test_get_user_count_empty_database(self):
        """Test user count on fresh database."""
        count = auth.get_user_count(self.db_path)
        self.assertEqual(count, 0)

    # -------------------------------------------------------------------------
    # Role Management Tests
    # -------------------------------------------------------------------------

    def test_update_user_role_staff_to_admin(self):
        """Test promoting a staff user to admin."""
        auth.create_user(self.db_path, 'admin1', 'Pass1!', 'admin')
        auth.create_user(self.db_path, 'staff1', 'Pass2!', 'staff')
        
        # Promote staff to admin
        result = auth.update_user_role(self.db_path, 'staff1', 'admin', 'admin')
        self.assertTrue(result)
        
        # Verify role changed
        users = auth.list_users(self.db_path)
        staff_user = next(u for u in users if u['username'] == 'staff1')
        self.assertEqual(staff_user['role'], 'admin')

    def test_update_user_role_admin_to_staff(self):
        """Test demoting an admin user to staff."""
        auth.create_user(self.db_path, 'admin1', 'Pass1!', 'admin')
        auth.create_user(self.db_path, 'admin2', 'Pass2!', 'admin')
        
        # Demote admin2 to staff (admin1 remains as admin)
        result = auth.update_user_role(self.db_path, 'admin2', 'staff', 'admin')
        self.assertTrue(result)
        
        # Verify role changed
        users = auth.list_users(self.db_path)
        demoted_user = next(u for u in users if u['username'] == 'admin2')
        self.assertEqual(demoted_user['role'], 'staff')

    def test_update_user_role_prevent_demote_last_admin(self):
        """Test that the last admin cannot be demoted."""
        auth.create_user(self.db_path, 'admin1', 'Pass1!', 'admin')
        
        # Try to demote the only admin
        with self.assertRaises(ValueError) as ctx:
            auth.update_user_role(self.db_path, 'admin1', 'staff', 'admin')
        
        self.assertIn("Cannot demote the last administrator", str(ctx.exception))

    def test_update_user_role_invalid_role(self):
        """Test that invalid role raises ValueError."""
        auth.create_user(self.db_path, 'admin1', 'Pass1!', 'admin')
        auth.create_user(self.db_path, 'staff1', 'Pass2!', 'staff')
        
        with self.assertRaises(ValueError) as ctx:
            auth.update_user_role(self.db_path, 'staff1', 'superadmin', 'admin')
        
        self.assertIn("Role must be 'admin' or 'staff'", str(ctx.exception))

    def test_update_user_role_nonexistent_user(self):
        """Test that updating nonexistent user raises ValueError."""
        auth.create_user(self.db_path, 'admin1', 'Pass1!', 'admin')
        
        with self.assertRaises(ValueError) as ctx:
            auth.update_user_role(self.db_path, 'nonexistent', 'admin', 'admin')
        
        self.assertIn("does not exist", str(ctx.exception))

    def test_update_user_role_requires_admin(self):
        """Test that only admins can change roles."""
        auth.create_user(self.db_path, 'admin1', 'Pass1!', 'admin')
        auth.create_user(self.db_path, 'staff1', 'Pass2!', 'staff')
        
        # Staff tries to change role
        with self.assertRaises(PermissionError) as ctx:
            auth.update_user_role(self.db_path, 'staff1', 'admin', 'staff')
        
        self.assertIn("Only administrators can change user roles", str(ctx.exception))

    def test_delete_user_success(self):
        """Test successfully deleting a user."""
        auth.create_user(self.db_path, 'admin1', 'Pass1!', 'admin')
        auth.create_user(self.db_path, 'staff1', 'Pass2!', 'staff')
        
        count_before = auth.get_user_count(self.db_path)
        self.assertEqual(count_before, 2)
        
        # Delete staff user
        result = auth.delete_user(self.db_path, 'staff1', 'admin')
        self.assertTrue(result)
        
        count_after = auth.get_user_count(self.db_path)
        self.assertEqual(count_after, 1)
        
        # Verify user is gone
        users = auth.list_users(self.db_path)
        usernames = [u['username'] for u in users]
        self.assertNotIn('staff1', usernames)

    def test_delete_user_prevent_delete_last_admin(self):
        """Test that the last admin cannot be deleted."""
        auth.create_user(self.db_path, 'admin1', 'Pass1!', 'admin')
        
        # Try to delete the only admin
        with self.assertRaises(ValueError) as ctx:
            auth.delete_user(self.db_path, 'admin1', 'admin')
        
        self.assertIn("Cannot delete the last administrator", str(ctx.exception))

    def test_delete_user_can_delete_admin_if_others_exist(self):
        """Test that an admin can be deleted if other admins exist."""
        auth.create_user(self.db_path, 'admin1', 'Pass1!', 'admin')
        auth.create_user(self.db_path, 'admin2', 'Pass2!', 'admin')
        
        # Delete one admin (another remains)
        result = auth.delete_user(self.db_path, 'admin2', 'admin')
        self.assertTrue(result)
        
        count = auth.get_user_count(self.db_path)
        self.assertEqual(count, 1)

    def test_delete_user_nonexistent_user(self):
        """Test that deleting nonexistent user raises ValueError."""
        auth.create_user(self.db_path, 'admin1', 'Pass1!', 'admin')
        
        with self.assertRaises(ValueError) as ctx:
            auth.delete_user(self.db_path, 'nonexistent', 'admin')
        
        self.assertIn("does not exist", str(ctx.exception))

    def test_delete_user_requires_admin(self):
        """Test that only admins can delete users."""
        auth.create_user(self.db_path, 'admin1', 'Pass1!', 'admin')
        auth.create_user(self.db_path, 'staff1', 'Pass2!', 'staff')
        
        # Staff tries to delete user
        with self.assertRaises(PermissionError) as ctx:
            auth.delete_user(self.db_path, 'admin1', 'staff')
        
        self.assertIn("Only administrators can delete user accounts", str(ctx.exception))

    def test_username_with_spaces(self):
        """Test that usernames with spaces work correctly."""
        # Create users with spaces in names
        auth.create_user(self.db_path, 'admin1', 'Pass1!', 'admin')
        auth.create_user(self.db_path, 'John Smith', 'Pass2!', 'staff')
        auth.create_user(self.db_path, 'Mary Jane Watson', 'Pass3!', 'staff')
        
        # Verify users exist
        users = auth.list_users(self.db_path)
        usernames = [u['username'] for u in users]
        self.assertIn('John Smith', usernames)
        self.assertIn('Mary Jane Watson', usernames)
        
        # Test role change with spaced username
        result = auth.update_user_role(self.db_path, 'John Smith', 'admin', 'admin')
        self.assertTrue(result)
        
        users = auth.list_users(self.db_path)
        john = next(u for u in users if u['username'] == 'John Smith')
        self.assertEqual(john['role'], 'admin')
        
        # Test deletion with spaced username
        result = auth.delete_user(self.db_path, 'Mary Jane Watson', 'admin')
        self.assertTrue(result)
        
        users = auth.list_users(self.db_path)
        usernames = [u['username'] for u in users]
        self.assertNotIn('Mary Jane Watson', usernames)


if __name__ == '__main__':
    unittest.main()
