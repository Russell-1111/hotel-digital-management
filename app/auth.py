"""
Authentication and authorization module for Hotel Digital Management System.

This module provides local user authentication with role-based access control (RBAC).
It uses PBKDF2-HMAC-SHA256 for secure password hashing and includes brute-force
protection via temporary account lockouts.

Key Features:
- User creation with hashed passwords (admin and staff roles)
- Password verification with constant-time comparison
- Password change functionality
- Brute-force protection (5 failed attempts = 5 minute lockout)
- User listing (admin-only)
- Comprehensive logging of security events

Security:
- PBKDF2-HMAC-SHA256 with 310,000 iterations (OWASP 2023 recommendation)
- 32-byte cryptographically secure random salt per user
- Constant-time hash comparison to prevent timing attacks
- No plaintext password storage
"""

from __future__ import annotations
import hashlib
import logging
import secrets
import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional, List, Dict

logger = logging.getLogger(__name__)

# Brute-force protection: in-memory tracking of failed login attempts
# Format: {username: [timestamp1, timestamp2, ...]}
_failed_attempts: Dict[str, List[datetime]] = {}

# Security parameters
PBKDF2_ITERATIONS = 310_000  # OWASP 2023 recommendation for PBKDF2-SHA256
SALT_BYTES = 32  # 256 bits
LOCKOUT_THRESHOLD = 5  # Failed attempts before lockout
LOCKOUT_DURATION_SECONDS = 300  # 5 minutes
LOCKOUT_WINDOW_SECONDS = 300  # 5 minute window for counting failures


def _hash_password(password: str) -> str:
    """
    Hash a password using PBKDF2-HMAC-SHA256 with a random salt.
    
    Args:
        password: Plaintext password to hash
        
    Returns:
        Formatted hash string: "salt_hex:hash_hex"
        
    Security:
        - Generates cryptographically secure 32-byte random salt
        - Uses PBKDF2-HMAC-SHA256 with 310,000 iterations
        - Both salt and hash are hex-encoded for storage
    """
    salt = secrets.token_bytes(SALT_BYTES)
    password_hash = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt,
        PBKDF2_ITERATIONS
    )
    return f"{salt.hex()}:{password_hash.hex()}"


def _verify_password(password: str, stored_hash: str) -> bool:
    """
    Verify a password against a stored hash using constant-time comparison.
    
    Args:
        password: Plaintext password to verify
        stored_hash: Stored hash in format "salt_hex:hash_hex"
        
    Returns:
        True if password matches, False otherwise
        
    Security:
        - Extracts salt from stored hash
        - Recomputes hash with same parameters
        - Uses secrets.compare_digest for constant-time comparison
    """
    try:
        salt_hex, hash_hex = stored_hash.split(':')
        salt = bytes.fromhex(salt_hex)
        expected_hash = bytes.fromhex(hash_hex)
        
        computed_hash = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt,
            PBKDF2_ITERATIONS
        )
        
        # Constant-time comparison to prevent timing attacks
        return secrets.compare_digest(computed_hash, expected_hash)
    except (ValueError, AttributeError) as e:
        logger.error(f"Invalid password hash format: {e}")
        return False


def create_user(db_path: Path, username: str, password: str, role: str) -> None:
    """
    Create a new user account with hashed password.
    
    Args:
        db_path: Path to SQLite database
        username: Unique username
        password: Plaintext password (will be hashed)
        role: User role ('admin' or 'staff')
        
    Raises:
        ValueError: If username already exists or role is invalid
        sqlite3.Error: If database operation fails
        
    Example:
        >>> create_user(Path("data/reservations.db"), "admin1", "secure123", "admin")
    """
    if role not in ('admin', 'staff'):
        raise ValueError("Role must be 'admin' or 'staff'")
    
    password_hash = _hash_password(password)
    now_utc = datetime.now(timezone.utc).isoformat()
    
    conn = sqlite3.connect(str(db_path))
    try:
        conn.execute("""
            INSERT INTO users (username, password_hash, role, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?)
        """, (username, password_hash, role, now_utc, now_utc))
        conn.commit()
        logger.info(f"Created user '{username}' with role '{role}'")
    except sqlite3.IntegrityError as e:
        if "UNIQUE constraint failed" in str(e):
            raise ValueError("Username already exists")
        raise
    finally:
        conn.close()


def verify_user(db_path: Path, username: str, password: str) -> Optional[str]:
    """
    Authenticate a user and return their role on success.
    
    Args:
        db_path: Path to SQLite database
        username: Username to authenticate
        password: Plaintext password to verify
        
    Returns:
        User role ('admin' or 'staff') if authentication succeeds, None otherwise
        
    Side Effects:
        - Increments failed login counter on failure
        - Resets failed login counter on success
        - Logs authentication events
        
    Example:
        >>> role = verify_user(Path("data/reservations.db"), "admin1", "secure123")
        >>> if role == "admin":
        ...     print("Admin access granted")
    """
    # Check if user is currently locked out
    lockout_remaining = check_lockout(username)
    if lockout_remaining is not None:
        logger.warning(f"Login attempt for locked out user '{username}' ({lockout_remaining}s remaining)")
        return None
    
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    try:
        cursor = conn.execute(
            "SELECT password_hash, role FROM users WHERE username = ?",
            (username,)
        )
        row = cursor.fetchone()
        
        if row is None:
            # Username doesn't exist - don't record as failed attempt (prevents enumeration)
            logger.warning(f"Login attempt for non-existent user '{username}'")
            return None
        
        if _verify_password(password, row['password_hash']):
            # Success - reset failed attempts and return role
            reset_failed_logins(username)
            logger.info(f"User '{username}' authenticated successfully")
            return row['role']
        else:
            # Failed - record attempt and return None
            record_failed_login(username)
            logger.warning(f"Failed login attempt for user '{username}'")
            return None
            
    finally:
        conn.close()


def change_password(db_path: Path, username: str, old_password: str, new_password: str) -> bool:
    """
    Change a user's password after verifying their current password.
    
    Args:
        db_path: Path to SQLite database
        username: Username whose password to change
        old_password: Current password for verification
        new_password: New password to set
        
    Returns:
        True if password was changed successfully, False if old password was incorrect
        
    Example:
        >>> success = change_password(db_path, "admin1", "old_pass", "new_pass")
        >>> if success:
        ...     print("Password changed successfully")
    """
    # Verify old password first
    if verify_user(db_path, username, old_password) is None:
        logger.warning(f"Password change failed for '{username}': incorrect old password")
        return False
    
    # Generate new hash and update database
    new_hash = _hash_password(new_password)
    now_utc = datetime.now(timezone.utc).isoformat()
    
    conn = sqlite3.connect(str(db_path))
    try:
        conn.execute("""
            UPDATE users 
            SET password_hash = ?, updated_at = ?
            WHERE username = ?
        """, (new_hash, now_utc, username))
        conn.commit()
        logger.info(f"User '{username}' changed password")
        return True
    finally:
        conn.close()


def list_users(db_path: Path) -> List[Dict[str, str]]:
    """
    List all users in the database (admin-only feature).
    
    Args:
        db_path: Path to SQLite database
        
    Returns:
        List of user dictionaries with keys: username, role, created_at
        Password hashes are NOT included.
        
    Example:
        >>> users = list_users(Path("data/reservations.db"))
        >>> for user in users:
        ...     print(f"{user['username']}: {user['role']}")
    """
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    try:
        cursor = conn.execute("""
            SELECT username, role, created_at
            FROM users
            ORDER BY username
        """)
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()


def check_lockout(username: str) -> Optional[int]:
    """
    Check if a user is currently locked out due to failed login attempts.
    
    Args:
        username: Username to check
        
    Returns:
        Number of seconds remaining in lockout period, or None if not locked out
        
    Note:
        Lockout state is stored in-memory and resets on application restart.
    """
    if username not in _failed_attempts:
        return None
    
    now = datetime.now(timezone.utc)
    recent_failures = [
        ts for ts in _failed_attempts[username]
        if (now - ts).total_seconds() <= LOCKOUT_WINDOW_SECONDS
    ]
    
    # Update the list to only recent failures
    _failed_attempts[username] = recent_failures
    
    if len(recent_failures) >= LOCKOUT_THRESHOLD:
        # Calculate time remaining in lockout
        oldest_recent = min(recent_failures)
        lockout_end = oldest_recent + timedelta(seconds=LOCKOUT_DURATION_SECONDS)
        remaining = (lockout_end - now).total_seconds()
        
        if remaining > 0:
            return int(remaining)
        else:
            # Lockout expired
            _failed_attempts[username] = []
            return None
    
    return None


def record_failed_login(username: str) -> None:
    """
    Record a failed login attempt for brute-force protection.
    
    Args:
        username: Username of failed attempt
        
    Side Effects:
        - Appends timestamp to in-memory tracking
        - Logs lockout event if threshold is reached
    """
    now = datetime.now(timezone.utc)
    
    if username not in _failed_attempts:
        _failed_attempts[username] = []
    
    _failed_attempts[username].append(now)
    
    # Check if this triggers a lockout
    lockout_remaining = check_lockout(username)
    if lockout_remaining is not None:
        logger.warning(
            f"User '{username}' locked out for {LOCKOUT_DURATION_SECONDS}s "
            f"after {LOCKOUT_THRESHOLD} failed attempts"
        )


def reset_failed_logins(username: str) -> None:
    """
    Reset failed login counter for a user (called on successful login).
    
    Args:
        username: Username to reset
    """
    if username in _failed_attempts:
        del _failed_attempts[username]


def get_user_count(db_path: Path) -> int:
    """
    Get the total number of users in the database.
    
    Args:
        db_path: Path to SQLite database
        
    Returns:
        Count of users
        
    Use Case:
        Used to determine if initial setup is needed (count == 0)
    """
    conn = sqlite3.connect(str(db_path))
    try:
        cursor = conn.execute("SELECT COUNT(*) FROM users")
        return cursor.fetchone()[0]
    finally:
        conn.close()


def update_user_role(db_path: Path, username: str, new_role: str, current_user_role: str) -> bool:
    """
    Update a user's role (admin-only operation).
    
    Args:
        db_path: Path to SQLite database
        username: Username whose role to change
        new_role: New role to assign ('admin' or 'staff')
        current_user_role: Role of the user performing this action (must be 'admin')
        
    Returns:
        True if role was changed successfully, False otherwise
        
    Raises:
        ValueError: If new_role is invalid, user doesn't exist, or attempting to demote last admin
        PermissionError: If current_user_role is not 'admin'
        
    Security:
        - Only admins can change roles
        - Prevents demoting the last admin (ensures system remains manageable)
        - Logs all role changes
        
    Example:
        >>> success = update_user_role(db_path, "john", "admin", "admin")
        >>> if success:
        ...     print("User promoted to admin")
    """
    # Role enforcement
    if current_user_role != 'admin':
        logger.warning(f"Non-admin user attempted to change role for '{username}'")
        raise PermissionError("Only administrators can change user roles")
    
    # Validate new role
    if new_role not in ('admin', 'staff'):
        raise ValueError("Role must be 'admin' or 'staff'")
    
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    try:
        # Check if user exists and get current role
        cursor = conn.execute(
            "SELECT role FROM users WHERE username = ?",
            (username,)
        )
        row = cursor.fetchone()
        
        if row is None:
            logger.warning(f"Attempt to change role for non-existent user '{username}'")
            raise ValueError(f"User '{username}' does not exist")
        
        current_role = row['role']
        
        # If demoting from admin to staff, ensure it's not the last admin
        if current_role == 'admin' and new_role == 'staff':
            admin_count = conn.execute(
                "SELECT COUNT(*) as count FROM users WHERE role = 'admin'"
            ).fetchone()['count']
            
            if admin_count <= 1:
                logger.warning(f"Attempt to demote last admin user '{username}'")
                raise ValueError(
                    "Cannot demote the last administrator. "
                    "Create another admin account first."
                )
        
        # Update role
        now_utc = datetime.now(timezone.utc).isoformat()
        conn.execute("""
            UPDATE users 
            SET role = ?, updated_at = ?
            WHERE username = ?
        """, (new_role, now_utc, username))
        conn.commit()
        
        logger.info(f"User '{username}' role changed from '{current_role}' to '{new_role}'")
        return True
        
    except (ValueError, PermissionError):
        raise
    except Exception as e:
        logger.error(f"Failed to update role for user '{username}': {e}")
        return False
    finally:
        conn.close()


def delete_user(db_path: Path, username: str, current_user_role: str) -> bool:
    """
    Delete a user account (admin-only operation).
    
    Args:
        db_path: Path to SQLite database
        username: Username to delete
        current_user_role: Role of the user performing this action (must be 'admin')
        
    Returns:
        True if user was deleted successfully, False otherwise
        
    Raises:
        ValueError: If user doesn't exist or attempting to delete last admin
        PermissionError: If current_user_role is not 'admin'
        
    Security:
        - Only admins can delete users
        - Prevents deleting the last admin (ensures system remains manageable)
        - Logs all user deletions
        
    Warning:
        This operation is irreversible. User will need to be recreated to regain access.
        
    Example:
        >>> success = delete_user(db_path, "old_staff", "admin")
        >>> if success:
        ...     print("User account deleted")
    """
    # Role enforcement
    if current_user_role != 'admin':
        logger.warning(f"Non-admin user attempted to delete user '{username}'")
        raise PermissionError("Only administrators can delete user accounts")
    
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    try:
        # Check if user exists and get role
        cursor = conn.execute(
            "SELECT role FROM users WHERE username = ?",
            (username,)
        )
        row = cursor.fetchone()
        
        if row is None:
            logger.warning(f"Attempt to delete non-existent user '{username}'")
            raise ValueError(f"User '{username}' does not exist")
        
        user_role = row['role']
        
        # If deleting an admin, ensure it's not the last one
        if user_role == 'admin':
            admin_count = conn.execute(
                "SELECT COUNT(*) as count FROM users WHERE role = 'admin'"
            ).fetchone()['count']
            
            if admin_count <= 1:
                logger.warning(f"Attempt to delete last admin user '{username}'")
                raise ValueError(
                    "Cannot delete the last administrator. "
                    "Create another admin account first."
                )
        
        # Delete user
        conn.execute("DELETE FROM users WHERE username = ?", (username,))
        conn.commit()
        
        logger.info(f"User '{username}' (role: {user_role}) deleted")
        return True
        
    except (ValueError, PermissionError):
        raise
    except Exception as e:
        logger.error(f"Failed to delete user '{username}': {e}")
        return False
    finally:
        conn.close()
