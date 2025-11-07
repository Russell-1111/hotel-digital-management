"""
UI dialogs and integration for authentication system.

This file contains the sample implementation for:
- InitialSetupDialog: Creates first admin account on fresh install
- LoginDialog: Modal authentication dialog on startup
- ChangePasswordDialog: Password change for logged-in users
- Role enforcement helpers for protecting admin-only actions
"""

import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
import logging

# These would be imported from app.auth in actual implementation
# from app.auth import create_user, verify_user, change_password, get_user_count, check_lockout

logger = logging.getLogger(__name__)


class InitialSetupDialog(tk.Toplevel):
    """
    Modal dialog for creating the first administrator account.
    
    Displayed only when the users table is empty (first run).
    """
    
    def __init__(self, parent, db_path: Path):
        super().__init__(parent)
        self.db_path = db_path
        self.admin_created = False
        
        self.title("Initial Setup - Create Administrator Account")
        self.geometry("400x300")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()  # Modal
        
        # Prevent closing without creating admin
        self.protocol("WM_DELETE_WINDOW", self._on_close_attempt)
        
        self._build_ui()
        self.username_entry.focus()
        
    def _build_ui(self):
        """Build the initial setup form."""
        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header
        ttk.Label(
            main_frame,
            text="Welcome! Create your administrator account.",
            font=('Segoe UI', 11, 'bold')
        ).pack(pady=(0, 20))
        
        # Username
        ttk.Label(main_frame, text="Username:").pack(anchor=tk.W)
        self.username_entry = ttk.Entry(main_frame, width=30)
        self.username_entry.pack(fill=tk.X, pady=(0, 10))
        
        # Password
        ttk.Label(main_frame, text="Password (min 8 characters):").pack(anchor=tk.W)
        password_frame = ttk.Frame(main_frame)
        password_frame.pack(fill=tk.X, pady=(0, 10))
        self.password_entry = ttk.Entry(password_frame, width=30, show='*')
        self.password_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.show_password_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            password_frame,
            text="Show",
            variable=self.show_password_var,
            command=self._toggle_password
        ).pack(side=tk.LEFT, padx=(5, 0))
        
        # Confirm Password
        ttk.Label(main_frame, text="Confirm Password:").pack(anchor=tk.W)
        confirm_frame = ttk.Frame(main_frame)
        confirm_frame.pack(fill=tk.X, pady=(0, 15))
        self.confirm_entry = ttk.Entry(confirm_frame, width=30, show='*')
        self.confirm_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Status Label (for errors/success)
        self.status_label = ttk.Label(main_frame, text="", foreground="red")
        self.status_label.pack(pady=(0, 10))
        
        # Create Button
        self.create_btn = ttk.Button(
            main_frame,
            text="Create Admin Account",
            command=self._create_admin
        )
        self.create_btn.pack(pady=10)
        
        # Bind Enter key
        self.username_entry.bind('<Return>', lambda e: self._create_admin())
        self.password_entry.bind('<Return>', lambda e: self._create_admin())
        self.confirm_entry.bind('<Return>', lambda e: self._create_admin())
        
    def _toggle_password(self):
        """Toggle password visibility."""
        if self.show_password_var.get():
            self.password_entry.config(show='')
            self.confirm_entry.config(show='')
        else:
            self.password_entry.config(show='*')
            self.confirm_entry.config(show='*')
    
    def _create_admin(self):
        """Validate and create the admin account."""
        username = self.username_entry.get().strip()
        password = self.password_entry.get()
        confirm = self.confirm_entry.get()
        
        # Validation
        if not username:
            self.status_label.config(text="Username cannot be empty", foreground="red")
            return
        
        if len(password) < 8:
            self.status_label.config(text="Password must be at least 8 characters", foreground="red")
            return
        
        if password != confirm:
            self.status_label.config(text="Passwords do not match", foreground="red")
            return
        
        # Create user
        try:
            # In actual implementation:
            # from app.auth import create_user
            # create_user(self.db_path, username, password, 'admin')
            
            self.status_label.config(text="Administrator account created!", foreground="green")
            self.admin_created = True
            self.after(1000, self.destroy)  # Close after 1 second
            
        except ValueError as e:
            self.status_label.config(text=str(e), foreground="red")
        except Exception as e:
            logger.error(f"Failed to create admin: {e}")
            self.status_label.config(text="An error occurred. Check logs.", foreground="red")
    
    def _on_close_attempt(self):
        """Handle window close - require admin creation or exit app."""
        if not self.admin_created:
            if messagebox.askyesno("Exit Application", 
                                   "You must create an admin account to continue.\nExit application?"):
                self.master.destroy()  # Exit entire application


class LoginDialog(tk.Toplevel):
    """
    Modal login dialog displayed on application startup.
    
    Blocks access until successful authentication.
    """
    
    def __init__(self, parent, db_path: Path, config):
        super().__init__(parent)
        self.db_path = db_path
        self.config = config
        self.authenticated = False
        self.current_user = None
        self.lockout_job = None
        
        self.title("Login - Hotel Digital Management")
        self.geometry("400x280")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()  # Modal
        
        # Exit app if closed without login
        self.protocol("WM_DELETE_WINDOW", self._on_close_attempt)
        
        self._build_ui()
        self._load_remembered_username()
        self.username_entry.focus()
        
    def _build_ui(self):
        """Build the login form."""
        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header
        ttk.Label(
            main_frame,
            text="Please log in to continue",
            font=('Segoe UI', 11, 'bold')
        ).pack(pady=(0, 20))
        
        # Username
        ttk.Label(main_frame, text="Username:").pack(anchor=tk.W)
        self.username_entry = ttk.Entry(main_frame, width=30)
        self.username_entry.pack(fill=tk.X, pady=(0, 10))
        
        # Password
        ttk.Label(main_frame, text="Password:").pack(anchor=tk.W)
        password_frame = ttk.Frame(main_frame)
        password_frame.pack(fill=tk.X, pady=(0, 10))
        self.password_entry = ttk.Entry(password_frame, width=30, show='*')
        self.password_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.show_password_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            password_frame,
            text="Show",
            variable=self.show_password_var,
            command=self._toggle_password
        ).pack(side=tk.LEFT, padx=(5, 0))
        
        # Remember Username
        self.remember_var = tk.BooleanVar(
            value=self.config.get('auth', {}).get('remember_username', False)
        )
        ttk.Checkbutton(
            main_frame,
            text="Remember Username",
            variable=self.remember_var
        ).pack(anchor=tk.W, pady=(0, 10))
        
        # Status Label
        self.status_label = ttk.Label(main_frame, text="", foreground="red")
        self.status_label.pack(pady=(0, 10))
        
        # Login Button
        self.login_btn = ttk.Button(
            main_frame,
            text="Login",
            command=self._login
        )
        self.login_btn.pack(pady=10)
        
        # Bind Enter key
        self.username_entry.bind('<Return>', lambda e: self._login())
        self.password_entry.bind('<Return>', lambda e: self._login())
        
    def _toggle_password(self):
        """Toggle password visibility."""
        if self.show_password_var.get():
            self.password_entry.config(show='')
        else:
            self.password_entry.config(show='*')
    
    def _load_remembered_username(self):
        """Load remembered username from config if enabled."""
        if self.remember_var.get():
            last_username = self.config.get('auth', {}).get('last_username', '')
            if last_username:
                self.username_entry.insert(0, last_username)
    
    def _login(self):
        """Attempt to authenticate the user."""
        username = self.username_entry.get().strip()
        password = self.password_entry.get()
        
        if not username or not password:
            self.status_label.config(text="Please enter username and password", foreground="red")
            return
        
        # Check lockout first
        # In actual implementation:
        # from app.auth import check_lockout
        # lockout_remaining = check_lockout(username)
        lockout_remaining = None  # Placeholder
        
        if lockout_remaining is not None:
            self._show_lockout(lockout_remaining)
            return
        
        # Verify credentials
        # In actual implementation:
        # from app.auth import verify_user
        # role = verify_user(self.db_path, username, password)
        role = None  # Placeholder - replace with actual call
        
        if role is not None:
            # Success!
            self.current_user = {'username': username, 'role': role}
            self.authenticated = True
            self._save_remember_preference(username)
            self.destroy()
        else:
            # Failed
            self.status_label.config(text="Invalid username or password", foreground="red")
            self.password_entry.delete(0, tk.END)
            # Check if now locked out
            # lockout_remaining = check_lockout(username)
            # if lockout_remaining:
            #     self._show_lockout(lockout_remaining)
    
    def _show_lockout(self, seconds_remaining: int):
        """Display lockout countdown."""
        self.login_btn.config(state='disabled')
        self._update_lockout_countdown(seconds_remaining)
    
    def _update_lockout_countdown(self, seconds: int):
        """Update lockout countdown message."""
        if seconds > 0:
            self.status_label.config(
                text=f"Account locked. Try again in {seconds} seconds.",
                foreground="red"
            )
            self.lockout_job = self.after(1000, self._update_lockout_countdown, seconds - 1)
        else:
            self.status_label.config(text="")
            self.login_btn.config(state='normal')
    
    def _save_remember_preference(self, username: str):
        """Save remember username preference to config."""
        # In actual implementation, update config.ini
        # This would require extending load_config/save_config functions
        pass
    
    def _on_close_attempt(self):
        """Handle window close - exit application."""
        if not self.authenticated:
            self.master.destroy()  # Exit entire application


class ChangePasswordDialog(tk.Toplevel):
    """Dialog for changing the current user's password."""
    
    def __init__(self, parent, db_path: Path, username: str):
        super().__init__(parent)
        self.db_path = db_path
        self.username = username
        
        self.title("Change Password")
        self.geometry("400x280")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()  # Modal
        
        self._build_ui()
        self.old_password_entry.focus()
        
    def _build_ui(self):
        """Build the password change form."""
        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header
        ttk.Label(
            main_frame,
            text=f"Change password for: {self.username}",
            font=('Segoe UI', 10, 'bold')
        ).pack(pady=(0, 20))
        
        # Old Password
        ttk.Label(main_frame, text="Old Password:").pack(anchor=tk.W)
        self.old_password_entry = ttk.Entry(main_frame, width=30, show='*')
        self.old_password_entry.pack(fill=tk.X, pady=(0, 10))
        
        # New Password
        ttk.Label(main_frame, text="New Password (min 8 characters):").pack(anchor=tk.W)
        self.new_password_entry = ttk.Entry(main_frame, width=30, show='*')
        self.new_password_entry.pack(fill=tk.X, pady=(0, 10))
        
        # Confirm New Password
        ttk.Label(main_frame, text="Confirm New Password:").pack(anchor=tk.W)
        self.confirm_entry = ttk.Entry(main_frame, width=30, show='*')
        self.confirm_entry.pack(fill=tk.X, pady=(0, 15))
        
        # Status Label
        self.status_label = ttk.Label(main_frame, text="", foreground="red")
        self.status_label.pack(pady=(0, 10))
        
        # Buttons
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack()
        ttk.Button(btn_frame, text="Change Password", command=self._change_password).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Cancel", command=self.destroy).pack(side=tk.LEFT, padx=5)
        
        # Bind Enter key
        self.old_password_entry.bind('<Return>', lambda e: self._change_password())
        self.new_password_entry.bind('<Return>', lambda e: self._change_password())
        self.confirm_entry.bind('<Return>', lambda e: self._change_password())
    
    def _change_password(self):
        """Validate and change password."""
        old_password = self.old_password_entry.get()
        new_password = self.new_password_entry.get()
        confirm = self.confirm_entry.get()
        
        # Validation
        if not old_password:
            self.status_label.config(text="Old password is required", foreground="red")
            return
        
        if len(new_password) < 8:
            self.status_label.config(text="New password must be at least 8 characters", foreground="red")
            return
        
        if new_password != confirm:
            self.status_label.config(text="New passwords do not match", foreground="red")
            return
        
        # Attempt password change
        try:
            # In actual implementation:
            # from app.auth import change_password
            # success = change_password(self.db_path, self.username, old_password, new_password)
            success = True  # Placeholder
            
            if success:
                self.status_label.config(text="Password changed successfully!", foreground="green")
                self.after(1000, self.destroy)
            else:
                self.status_label.config(text="Incorrect old password", foreground="red")
                self.old_password_entry.delete(0, tk.END)
        except Exception as e:
            logger.error(f"Password change error: {e}")
            self.status_label.config(text="An error occurred. Check logs.", foreground="red")


# Role enforcement helper functions for App class

def require_admin(app_instance, action_name: str) -> bool:
    """
    Check if current user is admin. Show error dialog if not.
    
    Args:
        app_instance: The main App instance with current_user attribute
        action_name: Name of the action being attempted (for logging)
        
    Returns:
        True if user is admin, False otherwise
        
    Usage in App class:
        def _cancel_reservation(self):
            if not require_admin(self, "Cancel Reservation"):
                return
            # Proceed with cancellation...
    """
    if app_instance.current_user['role'] != 'admin':
        messagebox.showerror(
            "Administrator Required",
            "This action requires administrator privileges."
        )
        logger.warning(
            f"User '{app_instance.current_user['username']}' (staff) "
            f"attempted admin action: {action_name}"
        )
        return False
    return True


# Sample integration into App.__init__ method

def integrate_authentication_in_app_init(app_instance):
    """
    Sample code to integrate authentication into App.__init__() method.
    
    This should be added to app/ui/main.py in the App class __init__ method,
    BEFORE building the UI tabs.
    """
    # Add current_user attribute
    app_instance.current_user = None
    
    # Check if initial setup is needed
    from app.auth import get_user_count
    user_count = get_user_count(app_instance.paths.db)  # Assuming paths.db exists
    
    if user_count == 0:
        # Show initial setup dialog
        setup_dialog = InitialSetupDialog(app_instance, app_instance.paths.db)
        app_instance.wait_window(setup_dialog)
        
        if not setup_dialog.admin_created:
            # User closed setup without creating admin - exit app
            app_instance.destroy()
            return
    
    # Show login dialog
    login_dialog = LoginDialog(app_instance, app_instance.paths.db, app_instance.cfg)
    app_instance.wait_window(login_dialog)
    
    if not login_dialog.authenticated:
        # User closed login without authenticating - exit app
        app_instance.destroy()
        return
    
    # Store authenticated user
    app_instance.current_user = login_dialog.current_user
    logger.info(f"User '{app_instance.current_user['username']}' logged in with role '{app_instance.current_user['role']}'")
    
    # Continue with normal UI building...
