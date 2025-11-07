from __future__ import annotations
import logging
import sys
import tkinter as tk
from tkinter import ttk
from pathlib import Path
from datetime import datetime, timedelta, timezone
from typing import Dict, Optional
from zoneinfo import ZoneInfo
try:
    # Use the robust subclass that refreshes the popup to avoid arrow glitches
    from app.ui.fixed_dateentry import FixedDateEntry as DateEntry
except Exception:
    # Fallback to standard DateEntry if the subclass cannot be imported for any reason
    from tkcalendar import DateEntry

from app.rooms import load_config
from app.storage import ensure_dirs, start_daily_backup_scheduler
from app.storage_sqlite import ensure_db
from app.reporting import daily_checkin_list, daily_checkout_list, monthly_revenue_summary, guest_reservation_detail_report, compute_nights
from app.rooms import load_rooms, index_by_id, load_room_image
from app.reservations import (
    list_reservations,
    create_reservation,
    cancel_reservation,
    modify_reservation,
    is_room_available,
    auto_status_transitions,
)
from app.timezone_utils import now_hotel, get_hotel_tz
from app import auth


class InitialSetupDialog(tk.Toplevel):
    """Modal dialog for creating the first administrator account."""
    
    def __init__(self, parent, db_path: Path):
        super().__init__(parent)
        self.db_path = db_path
        self.admin_created = False
        
        self.title("Initial Setup - Create Administrator Account")
        self.geometry("400x300")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        
        self.protocol("WM_DELETE_WINDOW", self._on_close_attempt)
        
        self._build_ui()
        self.username_entry.focus()
        
    def _build_ui(self):
        """Build the initial setup form."""
        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(
            main_frame,
            text="Welcome! Create your administrator account.",
            font=('Segoe UI', 11, 'bold')
        ).pack(pady=(0, 20))
        
        ttk.Label(main_frame, text="Username:").pack(anchor=tk.W)
        self.username_entry = ttk.Entry(main_frame, width=30)
        self.username_entry.pack(fill=tk.X, pady=(0, 10))
        
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
        
        ttk.Label(main_frame, text="Confirm Password:").pack(anchor=tk.W)
        self.confirm_entry = ttk.Entry(main_frame, width=30, show='*')
        self.confirm_entry.pack(fill=tk.X, pady=(0, 15))
        
        self.status_label = ttk.Label(main_frame, text="", foreground="red")
        self.status_label.pack(pady=(0, 10))
        
        self.create_btn = ttk.Button(
            main_frame,
            text="Create Admin Account",
            command=self._create_admin
        )
        self.create_btn.pack(pady=10)
        
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
        
        if not username:
            self.status_label.config(text="Username cannot be empty", foreground="red")
            return
        
        if len(password) < 8:
            self.status_label.config(text="Password must be at least 8 characters", foreground="red")
            return
        
        if password != confirm:
            self.status_label.config(text="Passwords do not match", foreground="red")
            return
        
        try:
            auth.create_user(self.db_path, username, password, 'admin')
            self.status_label.config(text="Administrator account created!", foreground="green")
            self.admin_created = True
            self.after(1000, self.destroy)
        except ValueError as e:
            self.status_label.config(text=str(e), foreground="red")
        except Exception as e:
            logging.getLogger(__name__).error(f"Failed to create admin: {e}")
            self.status_label.config(text="An error occurred. Check logs.", foreground="red")
    
    def _on_close_attempt(self):
        """Handle window close - require admin creation or exit app."""
        from tkinter import messagebox
        if not self.admin_created:
            if messagebox.askyesno("Exit Application", 
                                   "You must create an admin account to continue.\nExit application?"):
                self.master.destroy()


class LoginDialog(tk.Toplevel):
    """Modal login dialog displayed on application startup."""
    
    def __init__(self, parent, db_path: Path, cfg):
        super().__init__(parent)
        self.db_path = db_path
        self.cfg = cfg
        self.authenticated = False
        self.current_user = None
        self.lockout_job = None
        
        self.title("Login - Hotel Digital Management")
        self.geometry("400x280")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        
        self.protocol("WM_DELETE_WINDOW", self._on_close_attempt)
        
        self._build_ui()
        self._load_remembered_username()
        self.username_entry.focus()
        
    def _build_ui(self):
        """Build the login form."""
        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(
            main_frame,
            text="Please log in to continue",
            font=('Segoe UI', 11, 'bold')
        ).pack(pady=(0, 20))
        
        ttk.Label(main_frame, text="Username:").pack(anchor=tk.W)
        self.username_entry = ttk.Entry(main_frame, width=30)
        self.username_entry.pack(fill=tk.X, pady=(0, 10))
        
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
        
        self.remember_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            main_frame,
            text="Remember Username",
            variable=self.remember_var
        ).pack(anchor=tk.W, pady=(0, 10))
        
        self.status_label = ttk.Label(main_frame, text="", foreground="red")
        self.status_label.pack(pady=(0, 10))
        
        self.login_btn = ttk.Button(
            main_frame,
            text="Login",
            command=self._login
        )
        self.login_btn.pack(pady=10)
        
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
        remember = getattr(self.cfg, 'remember_username', False)
        last_username = getattr(self.cfg, 'last_username', '')
        if remember and last_username:
            self.username_entry.insert(0, last_username)
            self.remember_var.set(True)
    
    def _login(self):
        """Attempt to authenticate the user."""
        username = self.username_entry.get().strip()
        password = self.password_entry.get()
        
        if not username or not password:
            self.status_label.config(text="Please enter username and password", foreground="red")
            return
        
        lockout_remaining = auth.check_lockout(username)
        if lockout_remaining is not None:
            self._show_lockout(lockout_remaining)
            return
        
        role = auth.verify_user(self.db_path, username, password)
        
        if role is not None:
            self.current_user = {'username': username, 'role': role}
            self.authenticated = True
            self._save_remember_preference(username)
            self.destroy()
        else:
            self.status_label.config(text="Invalid username or password", foreground="red")
            self.password_entry.delete(0, tk.END)
            lockout_remaining = auth.check_lockout(username)
            if lockout_remaining:
                self._show_lockout(lockout_remaining)
    
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
        import configparser
        config = configparser.ConfigParser()
        config.read('config.ini')
        
        if 'auth' not in config:
            config['auth'] = {}
        
        if self.remember_var.get():
            config['auth']['remember_username'] = 'true'
            config['auth']['last_username'] = username
        else:
            config['auth']['remember_username'] = 'false'
            config['auth']['last_username'] = ''
        
        with open('config.ini', 'w') as f:
            config.write(f)
    
    def _on_close_attempt(self):
        """Handle window close - exit application."""
        if not self.authenticated:
            self.master.destroy()


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
        self.grab_set()
        
        self._build_ui()
        self.old_password_entry.focus()
        
    def _build_ui(self):
        """Build the password change form."""
        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(
            main_frame,
            text=f"Change password for: {self.username}",
            font=('Segoe UI', 10, 'bold')
        ).pack(pady=(0, 20))
        
        ttk.Label(main_frame, text="Old Password:").pack(anchor=tk.W)
        self.old_password_entry = ttk.Entry(main_frame, width=30, show='*')
        self.old_password_entry.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(main_frame, text="New Password (min 8 characters):").pack(anchor=tk.W)
        self.new_password_entry = ttk.Entry(main_frame, width=30, show='*')
        self.new_password_entry.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(main_frame, text="Confirm New Password:").pack(anchor=tk.W)
        self.confirm_entry = ttk.Entry(main_frame, width=30, show='*')
        self.confirm_entry.pack(fill=tk.X, pady=(0, 15))
        
        self.status_label = ttk.Label(main_frame, text="", foreground="red")
        self.status_label.pack(pady=(0, 10))
        
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack()
        ttk.Button(btn_frame, text="Change Password", command=self._change_password).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Cancel", command=self.destroy).pack(side=tk.LEFT, padx=5)
        
        self.old_password_entry.bind('<Return>', lambda e: self._change_password())
        self.new_password_entry.bind('<Return>', lambda e: self._change_password())
        self.confirm_entry.bind('<Return>', lambda e: self._change_password())
    
    def _change_password(self):
        """Validate and change password."""
        old_password = self.old_password_entry.get()
        new_password = self.new_password_entry.get()
        confirm = self.confirm_entry.get()
        
        if not old_password:
            self.status_label.config(text="Old password is required", foreground="red")
            return
        
        if len(new_password) < 8:
            self.status_label.config(text="New password must be at least 8 characters", foreground="red")
            return
        
        if new_password != confirm:
            self.status_label.config(text="New passwords do not match", foreground="red")
            return
        
        try:
            success = auth.change_password(self.db_path, self.username, old_password, new_password)
            
            if success:
                self.status_label.config(text="Password changed successfully!", foreground="green")
                self.after(1000, self.destroy)
            else:
                self.status_label.config(text="Incorrect old password", foreground="red")
                self.old_password_entry.delete(0, tk.END)
        except Exception as e:
            logging.getLogger(__name__).error(f"Password change error: {e}")
            self.status_label.config(text="An error occurred. Check logs.", foreground="red")


class UserManagementDialog(tk.Toplevel):
    """Dialog for managing user accounts (admin-only)."""
    
    def __init__(self, parent, db_path: Path, current_user: Dict[str, str]):
        super().__init__(parent)
        self.db_path = db_path
        self.current_user = current_user
        self.user_index_map = {}  # Map listbox indices to usernames
        
        self.title("User Management")
        self.geometry("600x400")
        self.resizable(True, True)
        self.transient(parent)
        self.grab_set()
        
        self._build_ui()
        self._refresh_users()
        
    def _build_ui(self):
        """Build the user management interface."""
        main_frame = ttk.Frame(self, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header
        header = ttk.Label(
            main_frame,
            text="User Account Management",
            font=('Segoe UI', 12, 'bold')
        )
        header.pack(pady=(0, 10))
        
        # User list with scrollbar
        list_frame = ttk.Frame(main_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.user_listbox = tk.Listbox(
            list_frame,
            yscrollcommand=scrollbar.set,
            font=('Courier New', 10),
            height=12
        )
        self.user_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.user_listbox.yview)
        
        # Status label
        self.status_label = ttk.Label(main_frame, text="", foreground="blue")
        self.status_label.pack(pady=(0, 10))
        
        # Action buttons
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X)
        
        ttk.Button(
            btn_frame,
            text="Change Role (Admin ↔ Staff)",
            command=self._change_role
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            btn_frame,
            text="Delete User",
            command=self._delete_user
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            btn_frame,
            text="Create New User",
            command=self._create_user
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            btn_frame,
            text="Refresh",
            command=self._refresh_users
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            btn_frame,
            text="Close",
            command=self.destroy
        ).pack(side=tk.RIGHT, padx=5)
        
    def _refresh_users(self):
        """Refresh the user list."""
        self.user_listbox.delete(0, tk.END)
        self.status_label.config(text="", foreground="blue")
        
        # Store mapping of listbox indices to usernames for reliable lookup
        self.user_index_map = {}
        
        try:
            users = auth.list_users(self.db_path)
            
            # Add header
            self.user_listbox.insert(
                tk.END,
                f"{'Username':<20} {'Role':<10} {'Created':<20}"
            )
            self.user_listbox.insert(tk.END, "─" * 50)
            
            # Add users
            for idx, user in enumerate(users):
                created_str = user['created_at'][:19] if user['created_at'] else 'N/A'
                current_marker = " ← (You)" if user['username'] == self.current_user['username'] else ""
                display_line = f"{user['username']:<20} {user['role']:<10} {created_str}{current_marker}"
                self.user_listbox.insert(tk.END, display_line)
                
                # Store mapping: listbox_index (starting from 2 after headers) -> username
                self.user_index_map[2 + idx] = user['username']
            
            self.status_label.config(text=f"Total users: {len(users)}", foreground="green")
            
        except Exception as e:
            logging.getLogger(__name__).error(f"Failed to list users: {e}")
            self.status_label.config(text="Error loading users. Check logs.", foreground="red")
    
    def _get_selected_username(self) -> Optional[str]:
        """Extract username from selected listbox item using index map."""
        selection = self.user_listbox.curselection()
        if not selection:
            self.status_label.config(text="Please select a user first", foreground="orange")
            return None
        
        line_idx = selection[0]
        if line_idx < 2:  # Skip header rows
            self.status_label.config(text="Please select a user (not the header)", foreground="orange")
            return None
        
        # Use the index map for reliable username lookup
        username = self.user_index_map.get(line_idx)
        
        if not username:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"No username mapping found for listbox index {line_idx}")
            self.status_label.config(text="Error: User not found in index", foreground="red")
            return None
        
        return username
    
    def _change_role(self):
        """Change selected user's role."""
        username = self._get_selected_username()
        if not username:
            return
        
        # Get current role
        try:
            users = auth.list_users(self.db_path)
            user = next((u for u in users if u['username'] == username), None)
            
            if not user:
                self.status_label.config(text=f"User '{username}' not found", foreground="red")
                return
            
            current_role = user['role']
            new_role = 'staff' if current_role == 'admin' else 'admin'
            
            # Confirm action
            from tkinter import messagebox
            if not messagebox.askyesno(
                "Confirm Role Change",
                f"Change user '{username}' from '{current_role}' to '{new_role}'?",
                parent=self
            ):
                return
            
            # Update role
            auth.update_user_role(self.db_path, username, new_role, self.current_user['role'])
            self.status_label.config(
                text=f"✓ Changed '{username}' from {current_role} to {new_role}",
                foreground="green"
            )
            self._refresh_users()
            
        except PermissionError as e:
            self.status_label.config(text=str(e), foreground="red")
        except ValueError as e:
            from tkinter import messagebox
            messagebox.showerror("Cannot Change Role", str(e), parent=self)
            self.status_label.config(text="Role change failed", foreground="red")
        except Exception as e:
            logging.getLogger(__name__).error(f"Failed to change role: {e}")
            self.status_label.config(text="Error changing role. Check logs.", foreground="red")
    
    def _delete_user(self):
        """Delete selected user."""
        username = self._get_selected_username()
        if not username:
            return
        
        # Prevent deleting yourself
        if username == self.current_user['username']:
            from tkinter import messagebox
            messagebox.showwarning(
                "Cannot Delete Self",
                "You cannot delete your own account while logged in.",
                parent=self
            )
            return
        
        # Confirm deletion
        from tkinter import messagebox
        if not messagebox.askyesno(
            "Confirm Deletion",
            f"Permanently delete user '{username}'?\n\nThis action cannot be undone.",
            parent=self
        ):
            return
        
        try:
            auth.delete_user(self.db_path, username, self.current_user['role'])
            self.status_label.config(
                text=f"✓ Deleted user '{username}'",
                foreground="green"
            )
            self._refresh_users()
            
        except PermissionError as e:
            self.status_label.config(text=str(e), foreground="red")
        except ValueError as e:
            from tkinter import messagebox
            messagebox.showerror("Cannot Delete User", str(e), parent=self)
            self.status_label.config(text="Deletion failed", foreground="red")
        except Exception as e:
            logging.getLogger(__name__).error(f"Failed to delete user: {e}")
            self.status_label.config(text="Error deleting user. Check logs.", foreground="red")
    
    def _create_user(self):
        """Show dialog to create a new user."""
        dialog = CreateUserDialog(self, self.db_path, self.current_user['role'])
        self.wait_window(dialog)
        
        if dialog.user_created:
            self._refresh_users()


class CreateUserDialog(tk.Toplevel):
    """Dialog for creating a new user account."""
    
    def __init__(self, parent, db_path: Path, current_user_role: str):
        super().__init__(parent)
        self.db_path = db_path
        self.current_user_role = current_user_role
        self.user_created = False
        
        self.title("Create New User")
        self.geometry("400x320")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        
        self._build_ui()
        self.username_entry.focus()
        
    def _build_ui(self):
        """Build the user creation form."""
        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(
            main_frame,
            text="Create New User Account",
            font=('Segoe UI', 10, 'bold')
        ).pack(pady=(0, 15))
        
        ttk.Label(main_frame, text="Username:").pack(anchor=tk.W)
        self.username_entry = ttk.Entry(main_frame, width=30)
        self.username_entry.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(main_frame, text="Password (min 8 characters):").pack(anchor=tk.W)
        self.password_entry = ttk.Entry(main_frame, width=30, show='*')
        self.password_entry.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(main_frame, text="Confirm Password:").pack(anchor=tk.W)
        self.confirm_entry = ttk.Entry(main_frame, width=30, show='*')
        self.confirm_entry.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(main_frame, text="Role:").pack(anchor=tk.W)
        self.role_var = tk.StringVar(value='staff')
        role_frame = ttk.Frame(main_frame)
        role_frame.pack(fill=tk.X, pady=(0, 15))
        ttk.Radiobutton(role_frame, text="Staff", variable=self.role_var, value='staff').pack(side=tk.LEFT)
        ttk.Radiobutton(role_frame, text="Admin", variable=self.role_var, value='admin').pack(side=tk.LEFT, padx=20)
        
        self.status_label = ttk.Label(main_frame, text="", foreground="red")
        self.status_label.pack(pady=(0, 10))
        
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack()
        ttk.Button(btn_frame, text="Create User", command=self._create).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Cancel", command=self.destroy).pack(side=tk.LEFT, padx=5)
        
        self.username_entry.bind('<Return>', lambda e: self._create())
        self.password_entry.bind('<Return>', lambda e: self._create())
        self.confirm_entry.bind('<Return>', lambda e: self._create())
    
    def _create(self):
        """Validate and create new user."""
        username = self.username_entry.get().strip()
        password = self.password_entry.get()
        confirm = self.confirm_entry.get()
        role = self.role_var.get()
        
        if not username:
            self.status_label.config(text="Username is required", foreground="red")
            return
        
        if len(password) < 8:
            self.status_label.config(text="Password must be at least 8 characters", foreground="red")
            return
        
        if password != confirm:
            self.status_label.config(text="Passwords do not match", foreground="red")
            return
        
        try:
            auth.create_user(self.db_path, username, password, role)
            self.status_label.config(text="User created successfully!", foreground="green")
            self.user_created = True
            self.after(1000, self.destroy)
            
        except ValueError as e:
            self.status_label.config(text=str(e), foreground="red")
        except Exception as e:
            logging.getLogger(__name__).error(f"User creation error: {e}")
            self.status_label.config(text="An error occurred. Check logs.", foreground="red")


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Hotel Digital Management - Front Desk")
        self.geometry("900x600")
        self.minsize(800, 500)
        logging.getLogger(__name__).info("UI initializing")

        # Apply ttk theme and base styling
        self._setup_theme()

        self.cfg = load_config(Path("config.ini"))
        
        # Initialize storage based on backend configuration
        if getattr(self.cfg, 'use_sqlite', True):
            # SQLite backend: ensure_db returns Path to database
            self.db_path = ensure_db(self.cfg)
            self.paths = ensure_dirs(self.cfg)  # Still need this for backup_dir, etc.
        else:
            # CSV backend: ensure_dirs returns FilePaths
            self.paths = ensure_dirs(self.cfg)
            self.db_path = None  # CSV backend doesn't use database
        
        # Authentication: Check if initial setup is needed
        self.current_user = None
        user_count = auth.get_user_count(self.db_path)
        
        if user_count == 0:
            # Show initial setup dialog
            setup_dialog = InitialSetupDialog(self, self.db_path)
            self.wait_window(setup_dialog)
            
            if not setup_dialog.admin_created:
                # User closed setup without creating admin - exit app
                self.destroy()
                return
        
        # Show login dialog
        login_dialog = LoginDialog(self, self.db_path, self.cfg)
        self.wait_window(login_dialog)
        
        if not login_dialog.authenticated:
            # User closed login without authenticating - exit app
            self.destroy()
            return
        
        # Store authenticated user
        self.current_user = login_dialog.current_user
        logging.getLogger(__name__).info(
            f"User '{self.current_user['username']}' logged in with role '{self.current_user['role']}'"
        )
        
        # Continue with normal initialization
        start_daily_backup_scheduler(self.cfg)

        nb = ttk.Notebook(self)
        nb.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        self.ops_frame = ttk.Frame(nb)
        self.res_frame = ttk.Frame(nb)
        self.avail_frame = ttk.Frame(nb)
        self.report_frame = ttk.Frame(nb)
        nb.add(self.ops_frame, text="Daily Ops")
        nb.add(self.res_frame, text="Reservations")
        nb.add(self.avail_frame, text="Availability")
        nb.add(self.report_frame, text="Reports")

        # Cache rooms
        self.rooms = load_rooms(self.paths.rooms)
        self.rooms_by_id = index_by_id(self.rooms)

        self._build_ops()
        self._build_reservations()
        self._build_availability()
        self._build_reports()
        
        # Add timezone info and user info in footer status bar
        footer = ttk.Frame(self)
        footer.pack(side=tk.BOTTOM, fill=tk.X, padx=8, pady=4)
        user_label = ttk.Label(footer, 
                               text=f"Logged in as: {self.current_user['username']} ({self.current_user['role']})", 
                               font=('Segoe UI', 8), foreground='#666')
        user_label.pack(side=tk.LEFT)
        ttk.Button(footer, text="Change Password", command=self._show_change_password).pack(side=tk.LEFT, padx=(10, 0))
        
        # Show Manage Users button only for admins
        if self.current_user['role'] == 'admin':
            ttk.Button(footer, text="Manage Users", command=self._show_user_management).pack(side=tk.LEFT, padx=(5, 0))
        
        tz_label = ttk.Label(footer, text=f"Timezone: {self.cfg.timezone}", 
                            font=('Segoe UI', 8), foreground='#666')
        tz_label.pack(side=tk.RIGHT)

    def _setup_theme(self):
        """Configure ttk theme and consistent styling."""
        style = ttk.Style()
        # Use a modern theme (available on Windows)
        available_themes = style.theme_names()
        if 'vista' in available_themes:
            style.theme_use('vista')
        elif 'clam' in available_themes:
            style.theme_use('clam')
        
        # Configure base font (accessible size)
        default_font = ('Segoe UI', 10)
        self.option_add('*Font', default_font)
        
        # Configure ttk widget styles
        style.configure('TLabel', font=default_font)
        style.configure('TButton', font=default_font, padding=4)
        style.configure('TEntry', font=default_font, padding=4)
        style.configure('TLabelFrame', font=default_font)
        style.configure('TLabelFrame.Label', font=('Segoe UI', 10, 'bold'))

    def _show_error(self, title: str, message: str):
        """Display error dialog with log file reference."""
        from tkinter import messagebox
        log_path = Path("logs/app.log").absolute()
        full_msg = f"{message}\n\nCheck {log_path} for details."
        logging.getLogger(__name__).error(f"{title}: {message}")
        messagebox.showerror(title, full_msg)
    
    def _require_admin(self, action_name: str) -> bool:
        """
        Check if current user is admin. Show error dialog if not.
        
        Args:
            action_name: Name of the action being attempted (for logging)
            
        Returns:
            True if user is admin, False otherwise
        """
        from tkinter import messagebox
        if self.current_user['role'] != 'admin':
            messagebox.showerror(
                "Administrator Required",
                "This action requires administrator privileges."
            )
            logging.getLogger(__name__).warning(
                f"User '{self.current_user['username']}' (staff) "
                f"attempted admin action: {action_name}"
            )
            return False
        return True
    
    def _show_change_password(self):
        """Show the change password dialog for the current user."""
        dialog = ChangePasswordDialog(self, self.db_path, self.current_user['username'])
        self.wait_window(dialog)
    
    def _show_user_management(self):
        """Show the user management dialog (admin-only)."""
        if not self._require_admin("manage users"):
            return
        dialog = UserManagementDialog(self, self.db_path, self.current_user)
        self.wait_window(dialog)

    def _validate_date_range(self, start_entry, end_entry, auto_adjust_end=True):
        """
        Validate that start date is before end date and they are not the same.
        
        Args:
            start_entry: DateEntry widget for start date
            end_entry: DateEntry widget for end date
            auto_adjust_end: If True, automatically adjust end date to be one day after start
            
        Returns:
            bool: True if dates are valid, False otherwise
        """
        try:
            start_str = start_entry.get()
            end_str = end_entry.get()
            
            start_date = datetime.strptime(start_str, '%Y-%m-%d')
            end_date = datetime.strptime(end_str, '%Y-%m-%d')
            
            # Check if dates are the same
            if start_date == end_date:
                if auto_adjust_end:
                    # Auto-adjust end date to be one day after start
                    new_end = start_date + timedelta(days=1)
                    end_entry.set_date(new_end)
                    return True
                else:
                    from tkinter import messagebox
                    messagebox.showwarning("Invalid Date Range", "Start and end dates cannot be the same. End date must be at least one day after start date.")
                    return False
            
            # Check if start is after end
            if start_date >= end_date:
                if auto_adjust_end:
                    # Auto-adjust end date to be one day after start
                    new_end = start_date + timedelta(days=1)
                    end_entry.set_date(new_end)
                    return True
                else:
                    from tkinter import messagebox
                    messagebox.showwarning("Invalid Date Range", "Start date must be before end date.")
                    return False
            
            return True
            
        except ValueError:
            return False

    def _on_checkin_date_change(self):
        """Handler for when check-in date changes - auto-adjust check-out to be one day after."""
        try:
            checkin_str = self.ci_entry.get()
            checkin_date = datetime.strptime(checkin_str, '%Y-%m-%d')
            
            # Set check-out to one day after check-in
            new_checkout = checkin_date + timedelta(days=1)
            self.co_entry.set_date(new_checkout)
            
        except ValueError:
            pass  # Invalid date format, skip auto-adjustment

    def _on_availability_start_change(self):
        """Handler for when availability start date changes - auto-adjust end to be one day after."""
        try:
            start_str = self.av_start_entry.get()
            start_date = datetime.strptime(start_str, '%Y-%m-%d')
            
            # Set end to one day after start
            new_end = start_date + timedelta(days=1)
            self.av_end_entry.set_date(new_end)
            
        except ValueError:
            pass  # Invalid date format, skip auto-adjustment

    def _on_report_start_change(self):
        """Handler for when report start date changes - auto-adjust end to be one day after."""
        try:
            start_str = self.start_date_entry.get()
            start_date = datetime.strptime(start_str, '%Y-%m-%d')
            
            # Set end to one day after start
            new_end = start_date + timedelta(days=1)
            self.end_date_entry.set_date(new_end)
            
        except ValueError:
            pass  # Invalid date format, skip auto-adjustment

    def _on_modify_checkin_change(self, ci_entry, co_entry):
        """Handler for modify dialog check-in date changes - auto-adjust check-out to be one day after."""
        try:
            checkin_str = ci_entry.get()
            checkin_date = datetime.strptime(checkin_str, '%Y-%m-%d')
            
            # Set check-out to one day after check-in
            new_checkout = checkin_date + timedelta(days=1)
            co_entry.set_date(new_checkout)
            
        except ValueError:
            pass  # Invalid date format, skip auto-adjustment

    def _build_ops(self):
        # Date input with consistent padding
        row = ttk.Frame(self.ops_frame, padding=8)
        row.pack(fill=tk.X)
        ttk.Label(row, text="Date (YYYY-MM-DD):").pack(side=tk.LEFT, padx=(0, 8))
        self.ops_date_entry = DateEntry(row, width=12, date_pattern='yyyy-mm-dd', 
                                         firstweekday='sunday')
        self.ops_date_entry.pack(side=tk.LEFT, padx=(0, 8))
        ttk.Button(row, text="Refresh", command=self.refresh_ops).pack(side=tk.LEFT)

        # Lists with consistent padding
        lists = ttk.Frame(self.ops_frame, padding=(8, 0, 8, 8))
        lists.pack(fill=tk.BOTH, expand=True)
        left = ttk.LabelFrame(lists, text="Today's Check-Ins", padding=8)
        right = ttk.LabelFrame(lists, text="Today's Check-Outs", padding=8)
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 4))
        right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(4, 0))

        self.ins_list = tk.Listbox(left, font=('Segoe UI', 9))
        self.outs_list = tk.Listbox(right, font=('Segoe UI', 9))
        self.ins_list.pack(fill=tk.BOTH, expand=True)
        self.outs_list.pack(fill=tk.BOTH, expand=True)

        self.refresh_ops()

    def refresh_ops(self):
        date_str = self.ops_date_entry.get()
        try:
            datetime.strptime(date_str, '%Y-%m-%d')
        except ValueError:
            logging.getLogger(__name__).warning(f"Invalid date format in Daily Ops: {date_str}")
            # Add visual feedback for invalid date
            self.ops_date_entry.configure(foreground='red')
            self.after(2000, lambda: self.ops_date_entry.configure(foreground='black'))
            return
        # Apply automatic status transitions before showing lists
        from ..timezone_utils import get_hotel_tz
        hotel_tz = get_hotel_tz(self.cfg.timezone)
        auto_status_transitions(
            self.paths.reservations,
            hotel_tz,
            self.cfg.check_in_time,
            self.cfg.check_out_time,
        )
        ins = daily_checkin_list(self.paths.reservations, date_str, hotel_tz)
        outs = daily_checkout_list(self.paths.reservations, date_str, hotel_tz)
        self.ins_list.delete(0, tk.END)
        self.outs_list.delete(0, tk.END)
        for r in ins:
            self.ins_list.insert(tk.END, f"Room {r.room_id} | {r.guest_name}")
        for r in outs:
            self.outs_list.insert(tk.END, f"Room {r.room_id} | {r.guest_name}")

    # --- Reservations tab ---
    def _build_reservations(self):
        form = ttk.LabelFrame(self.res_frame, text="New Reservation", padding=8)
        form.pack(fill=tk.X, padx=8, pady=8)

        # Row 1: Guest info
        r1 = ttk.Frame(form)
        r1.pack(fill=tk.X, pady=4)
        ttk.Label(r1, text="Guest Name").grid(row=0, column=0, sticky=tk.W, padx=(0, 8))
        self.guest_name = tk.StringVar()
        ttk.Entry(r1, textvariable=self.guest_name, width=24).grid(row=0, column=1, padx=(0, 8))
        ttk.Label(r1, text="Phone").grid(row=0, column=2, sticky=tk.W, padx=(8, 8))
        self.guest_phone = tk.StringVar()
        ttk.Entry(r1, textvariable=self.guest_phone, width=16).grid(row=0, column=3, padx=(0, 8))
        ttk.Label(r1, text="Email").grid(row=0, column=4, sticky=tk.W, padx=(8, 8))
        self.guest_email = tk.StringVar()
        ttk.Entry(r1, textvariable=self.guest_email, width=24).grid(row=0, column=5)

        # Row 2: Dates and guests
        r2 = ttk.Frame(form)
        r2.pack(fill=tk.X, pady=4)
        ttk.Label(r2, text="Check-in (YYYY-MM-DD)").grid(row=0, column=0, sticky=tk.W, padx=(0, 8))
        self.ci_entry = DateEntry(r2, width=12, date_pattern='yyyy-mm-dd', firstweekday='sunday')
        self.ci_entry.grid(row=0, column=1, padx=(0, 8))
        # Bind check-in date change to auto-adjust check-out
        self.ci_entry.bind('<<DateEntrySelected>>', lambda e: self._on_checkin_date_change())
        ttk.Label(r2, text="Check-out (YYYY-MM-DD)").grid(row=0, column=2, sticky=tk.W, padx=(8, 8))
        self.co_entry = DateEntry(r2, width=12, date_pattern='yyyy-mm-dd', firstweekday='sunday')
        self.co_entry.grid(row=0, column=3, padx=(0, 8))
        # Bind check-out date change to validate date range
        self.co_entry.bind('<<DateEntrySelected>>', lambda e: self._validate_date_range(self.ci_entry, self.co_entry, auto_adjust_end=True))
        ttk.Label(r2, text="Guests").grid(row=0, column=4, sticky=tk.W, padx=(8, 8))
        self.num_guests = tk.StringVar(value="1")
        ttk.Entry(r2, textvariable=self.num_guests, width=6).grid(row=0, column=5)
        
        # Set default end date to one day after start date (in hotel timezone)
        hotel_tz = get_hotel_tz(self.cfg.timezone)
        today_hotel = now_hotel(hotel_tz)
        tomorrow = today_hotel + timedelta(days=1)
        self.co_entry.set_date(tomorrow)

        # Row 3: Room selection with image preview
        r3 = ttk.Frame(form)
        r3.pack(fill=tk.X, pady=4)
        ttk.Label(r3, text="Available Room").grid(row=0, column=0, sticky=tk.W, padx=(0, 8))
        self.room_choice = tk.StringVar()
        self.room_combo = ttk.Combobox(r3, textvariable=self.room_choice, width=28, state="readonly")
        self.room_combo.grid(row=0, column=1, padx=(0, 8))
        self.room_combo.bind('<<ComboboxSelected>>', self._on_room_selected)
        
        # Room thumbnail image preview
        self.room_thumbnail_label = ttk.Label(r3, text="")
        self.room_thumbnail_label.grid(row=0, column=2, padx=(0, 8))
        
        ttk.Button(r3, text="Check Availability", command=self.refresh_available_rooms).grid(row=0, column=3, padx=(0, 8))
        ttk.Button(r3, text="Create Reservation", command=self.create_reservation_click).grid(row=0, column=4)

        # Existing reservations list
        list_frame = ttk.LabelFrame(self.res_frame, text="Existing Reservations", padding=8)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)
        self.res_list = tk.Listbox(list_frame, font=('Segoe UI', 9))
        self.res_list.pack(fill=tk.BOTH, expand=True)
        btns = ttk.Frame(self.res_frame, padding=(8, 0, 8, 8))
        btns.pack(fill=tk.X)
        ttk.Button(btns, text="Refresh", command=self.refresh_reservations_list).pack(side=tk.LEFT, padx=(0, 8))
        ttk.Button(btns, text="Modify Selected", command=self.modify_selected).pack(side=tk.LEFT, padx=(0, 8))
        ttk.Button(btns, text="Cancel Selected", command=self.cancel_selected).pack(side=tk.LEFT)

        # Initial population
        self.refresh_available_rooms()
        self.refresh_reservations_list()

    def refresh_reservations_list(self):
        self.res_list.delete(0, tk.END)
        # Store reservation IDs separately for modify/cancel operations
        self.res_list_ids = []
        for r in list_reservations(self.paths.reservations):
            self.res_list.insert(tk.END, f"Room {r.room_id} | {r.guest_name} | {r.check_in_date}->{r.check_out_date} | {r.status} | MYR {r.total_cost:.2f}")
            self.res_list_ids.append(r.reservation_id)

    def refresh_available_rooms(self):
        # Determine available rooms for the entered date range
        ci = self.ci_entry.get()
        co = self.co_entry.get()
        # Basic validation with visual feedback
        try:
            datetime.strptime(ci, '%Y-%m-%d')
            datetime.strptime(co, '%Y-%m-%d')
            # Clear any validation styling
            self.ci_entry.configure(foreground='black')
            self.co_entry.configure(foreground='black')
        except ValueError:
            # Show validation error
            self.ci_entry.configure(foreground='red')
            self.co_entry.configure(foreground='red')
            self.room_combo['values'] = []
            self.room_choice.set('')
            return
        
        # Validate date range before proceeding
        if not self._validate_date_range(self.ci_entry, self.co_entry, auto_adjust_end=True):
            self.room_combo['values'] = []
            self.room_choice.set('')
            return
        
        reservations = list_reservations(self.paths.reservations)
        avail = []
        for room in self.rooms:
            if is_room_available(reservations, room.room_id, ci, co):
                avail.append(f"{room.room_id} ({room.room_type}) - MYR {room.base_price:.2f}")
        self.room_combo['values'] = avail
        if avail:
            self.room_choice.set(avail[0])
            self._on_room_selected()  # Update thumbnail for first room
        else:
            self.room_choice.set('')
            self.room_thumbnail_label.config(image='')

    def _on_room_selected(self, event=None):
        """Update room thumbnail when a room is selected from the dropdown."""
        choice = self.room_choice.get()
        if not choice:
            self.room_thumbnail_label.config(image='')
            return
        
        # Extract room_id from the choice string (format: "101 (Standard) - MYR 120.00")
        room_id = choice.split()[0]
        room = self.rooms_by_id.get(room_id)
        
        if room:
            # Load thumbnail image (80x60 pixels)
            thumbnail = load_room_image(room.image_path, (80, 60))
            if thumbnail:
                self.room_thumbnail_label.config(image=thumbnail)
                # Keep a reference to prevent garbage collection
                self.room_thumbnail_label.image = thumbnail
            else:
                self.room_thumbnail_label.config(image='')
        else:
            self.room_thumbnail_label.config(image='')

    def create_reservation_click(self):
        choice = self.room_choice.get()
        if not choice:
            self._show_error("Validation Error", "Please select an available room.")
            return
        
        # Validate date range before creating reservation
        if not self._validate_date_range(self.ci_entry, self.co_entry, auto_adjust_end=False):
            return
        
        room_id = choice.split()[0]
        room = self.rooms_by_id.get(room_id)
        if not room:
            self._show_error("Error", f"Room {room_id} not found in inventory.")
            return
        try:
            num_guests = int(self.num_guests.get())
        except ValueError:
            self._show_error("Validation Error", "Number of guests must be a valid integer.")
            return
        try:
            create_reservation(
                self.cfg,
                self.paths.reservations,
                room,
                self.guest_name.get().strip(),
                self.guest_phone.get().strip(),
                self.guest_email.get().strip(),
                self.ci_entry.get(),
                self.co_entry.get(),
                num_guests,
            )
        except Exception as e:
            self._show_error("Reservation Error", f"Failed to create reservation: {str(e)}")
            return
        self.refresh_available_rooms()
        self.refresh_reservations_list()
        self.refresh_ops()

    def cancel_selected(self):
        # Check admin privilege
        if not self._require_admin("Cancel Reservation"):
            return
        
        # Get reservation ID from the parallel list
        sel = self.res_list.curselection()
        if not sel:
            return
        idx = sel[0]
        rid = self.res_list_ids[idx]
        try:
            cancel_reservation(self.paths.reservations, rid)
        except Exception as e:
            self._show_error("Cancellation Error", f"Failed to cancel reservation: {str(e)}")
            return
        self.refresh_reservations_list()
        self.refresh_ops()

    def modify_selected(self):
        """Open a dialog to modify the selected reservation."""
        sel = self.res_list.curselection()
        if not sel:
            return
        idx = sel[0]
        rid = self.res_list_ids[idx]
        
        # Find the reservation
        reservations = list_reservations(self.paths.reservations)
        target = next((r for r in reservations if r.reservation_id == rid), None)
        if not target or target.status in {"Cancelled", "Checked-Out"}:
            return

        # Create modification dialog
        dialog = tk.Toplevel(self)
        dialog.title(f"Modify Reservation {rid}")
        dialog.geometry("500x400")
        dialog.transient(self)
        dialog.grab_set()

        # Pre-fill with current values
        frm = ttk.Frame(dialog, padding=10)
        frm.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frm, text="Guest Name").grid(row=0, column=0, sticky=tk.W, pady=4)
        mod_name = tk.StringVar(value=target.guest_name)
        ttk.Entry(frm, textvariable=mod_name, width=30).grid(row=0, column=1, pady=4)

        ttk.Label(frm, text="Phone").grid(row=1, column=0, sticky=tk.W, pady=4)
        mod_phone = tk.StringVar(value=target.phone)
        ttk.Entry(frm, textvariable=mod_phone, width=30).grid(row=1, column=1, pady=4)

        ttk.Label(frm, text="Email").grid(row=2, column=0, sticky=tk.W, pady=4)
        mod_email = tk.StringVar(value=target.email)
        ttk.Entry(frm, textvariable=mod_email, width=30).grid(row=2, column=1, pady=4)

        ttk.Label(frm, text="Check-in (YYYY-MM-DD)").grid(row=3, column=0, sticky=tk.W, pady=4)
        mod_ci_entry = DateEntry(frm, width=28, date_pattern='yyyy-mm-dd', firstweekday='sunday')
        mod_ci_entry.set_date(datetime.strptime(target.check_in_date, '%Y-%m-%d'))
        mod_ci_entry.grid(row=3, column=1, pady=4)
        # Bind check-in change to auto-adjust check-out
        mod_ci_entry.bind('<<DateEntrySelected>>', lambda e: self._on_modify_checkin_change(mod_ci_entry, mod_co_entry))

        ttk.Label(frm, text="Check-out (YYYY-MM-DD)").grid(row=4, column=0, sticky=tk.W, pady=4)
        mod_co_entry = DateEntry(frm, width=28, date_pattern='yyyy-mm-dd', firstweekday='sunday')
        mod_co_entry.set_date(datetime.strptime(target.check_out_date, '%Y-%m-%d'))
        mod_co_entry.grid(row=4, column=1, pady=4)
        # Bind check-out change to validate date range
        mod_co_entry.bind('<<DateEntrySelected>>', lambda e: self._validate_date_range(mod_ci_entry, mod_co_entry, auto_adjust_end=True))

        ttk.Label(frm, text="Number of Guests").grid(row=5, column=0, sticky=tk.W, pady=4)
        mod_guests = tk.StringVar(value=str(target.num_guests))
        ttk.Entry(frm, textvariable=mod_guests, width=30).grid(row=5, column=1, pady=4)

        ttk.Label(frm, text="Room").grid(row=6, column=0, sticky=tk.W, pady=4)
        mod_room_var = tk.StringVar()
        mod_room_combo = ttk.Combobox(frm, textvariable=mod_room_var, width=28, state="readonly")
        mod_room_combo.grid(row=6, column=1, pady=4)

        # Populate available rooms for new dates
        def refresh_mod_rooms():
            ci = mod_ci_entry.get()
            co = mod_co_entry.get()
            try:
                datetime.strptime(ci, '%Y-%m-%d')
                datetime.strptime(co, '%Y-%m-%d')
            except ValueError:
                mod_room_combo['values'] = []
                mod_room_var.set('')
                return
            # Exclude current reservation from availability check
            others = [r for r in reservations if r.reservation_id != rid]
            avail = []
            for room in self.rooms:
                if is_room_available(others, room.room_id, ci, co):
                    avail.append(f"{room.room_id} ({room.room_type}) - MYR {room.base_price:.2f}")
            mod_room_combo['values'] = avail
            # Try to keep current room selected
            current_room_label = f"{target.room_id} ({self.rooms_by_id.get(target.room_id, type('obj', (object,), {'room_type': '?'})).room_type}) - MYR {self.rooms_by_id.get(target.room_id, type('obj', (object,), {'base_price': 0})).base_price:.2f}"
            if current_room_label in avail:
                mod_room_var.set(current_room_label)
            elif avail:
                mod_room_var.set(avail[0])
            else:
                mod_room_var.set('')

        ttk.Button(frm, text="Refresh Rooms", command=refresh_mod_rooms).grid(row=7, column=1, sticky=tk.W, pady=4)
        refresh_mod_rooms()

        # Save button
        def save_changes():
            new_name = mod_name.get().strip()
            new_phone = mod_phone.get().strip()
            new_email = mod_email.get().strip()
            new_ci = mod_ci_entry.get()
            new_co = mod_co_entry.get()
            
            # Validate date range before saving
            if not self._validate_date_range(mod_ci_entry, mod_co_entry, auto_adjust_end=False):
                return
            
            try:
                new_guests = int(mod_guests.get())
            except ValueError:
                new_guests = target.num_guests

            room_choice = mod_room_var.get()
            new_room = None
            if room_choice:
                room_id = room_choice.split()[0]
                if room_id != target.room_id:
                    new_room = self.rooms_by_id.get(room_id)

            try:
                modify_reservation(
                    self.cfg,
                    self.paths.reservations,
                    rid,
                    new_room=new_room,
                    new_check_in=new_ci if new_ci != target.check_in_date else None,
                    new_check_out=new_co if new_co != target.check_out_date else None,
                    new_num_guests=new_guests if new_guests != target.num_guests else None,
                    new_guest_name=new_name if new_name != target.guest_name else None,
                    new_phone=new_phone if new_phone != target.phone else None,
                    new_email=new_email if new_email != target.email else None,
                )
                dialog.destroy()
                self.refresh_reservations_list()
                self.refresh_ops()
            except Exception as e:
                # Show error in dialog
                error_lbl = ttk.Label(frm, text=f"Error: {str(e)}", foreground="red")
                error_lbl.grid(row=9, column=0, columnspan=2, pady=4)

        ttk.Button(frm, text="Save Changes", command=save_changes).grid(row=8, column=1, sticky=tk.E, pady=10)

    # --- Availability tab ---
    def _build_availability(self):
        frm = ttk.Frame(self.avail_frame, padding=8)
        frm.pack(fill=tk.X)
        ttk.Label(frm, text="Start (YYYY-MM-DD)").grid(row=0, column=0, sticky=tk.W, padx=(0, 8))
        self.av_start_entry = DateEntry(frm, width=12, date_pattern='yyyy-mm-dd', firstweekday='sunday')
        self.av_start_entry.grid(row=0, column=1, padx=(0, 8))
        # Bind start date change to auto-adjust end date
        self.av_start_entry.bind('<<DateEntrySelected>>', lambda e: self._on_availability_start_change())
        ttk.Label(frm, text="End (YYYY-MM-DD)").grid(row=0, column=2, sticky=tk.W, padx=(8, 8))
        self.av_end_entry = DateEntry(frm, width=12, date_pattern='yyyy-mm-dd', firstweekday='sunday')
        self.av_end_entry.grid(row=0, column=3, padx=(0, 8))
        # Bind end date change to validate date range
        self.av_end_entry.bind('<<DateEntrySelected>>', lambda e: self._validate_date_range(self.av_start_entry, self.av_end_entry, auto_adjust_end=True))
        ttk.Button(frm, text="Check", command=self.refresh_availability).grid(row=0, column=4)
        
        # Set default end date to one day after start date (in hotel timezone)
        hotel_tz = get_hotel_tz(self.cfg.timezone)
        today = now_hotel(hotel_tz)
        tomorrow = today + timedelta(days=1)
        self.av_start_entry.set_date(today)
        self.av_end_entry.set_date(tomorrow)

        # Scrollable container for room availability with images
        list_container = ttk.Frame(self.avail_frame, padding=(8, 0, 8, 8))
        list_container.pack(fill=tk.BOTH, expand=True)
        
        # Create canvas with scrollbar for scrollable room list
        canvas = tk.Canvas(list_container, highlightthickness=0)
        scrollbar = ttk.Scrollbar(list_container, orient="vertical", command=canvas.yview)
        self.av_scrollable_frame = ttk.Frame(canvas)
        
        self.av_scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.av_scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill=tk.BOTH, expand=True)
        scrollbar.pack(side="right", fill="y")

        self.refresh_availability()

    def refresh_availability(self):
        start = self.av_start_entry.get()
        end = self.av_end_entry.get()
        try:
            datetime.strptime(start, '%Y-%m-%d')
            datetime.strptime(end, '%Y-%m-%d')
        except ValueError:
            return
        
        # Validate date range before proceeding
        if not self._validate_date_range(self.av_start_entry, self.av_end_entry, auto_adjust_end=True):
            return
        
        # Clear existing room widgets
        for widget in self.av_scrollable_frame.winfo_children():
            widget.destroy()
        
        reservations = list_reservations(self.paths.reservations)
        
        # Create a row for each room with image and status
        for idx, room in enumerate(self.rooms):
            ok = is_room_available(reservations, room.room_id, start, end)
            status = "Available" if ok else "Unavailable"
            
            # Room frame
            room_frame = ttk.Frame(self.av_scrollable_frame, padding=8)
            room_frame.pack(fill=tk.X, pady=4)
            
            # Load and display room preview image (320x240)
            preview_img = load_room_image(room.image_path, (320, 240))
            if preview_img:
                img_label = ttk.Label(room_frame, image=preview_img)
                img_label.image = preview_img  # Keep reference
                img_label.pack(side=tk.LEFT, padx=(0, 12))
            
            # Room info text
            info_frame = ttk.Frame(room_frame)
            info_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            
            room_title = ttk.Label(
                info_frame, 
                text=f"Room {room.room_id} ({room.room_type})",
                font=('Segoe UI', 11, 'bold')
            )
            room_title.pack(anchor=tk.W)
            
            status_label = ttk.Label(
                info_frame,
                text=f"Status: {status}",
                font=('Segoe UI', 10),
                foreground='green' if ok else 'red'
            )
            status_label.pack(anchor=tk.W, pady=2)
            
            price_label = ttk.Label(
                info_frame,
                text=f"Price: MYR {room.base_price:.2f}/night",
                font=('Segoe UI', 9)
            )
            price_label.pack(anchor=tk.W)
            
            # Separator line
            if idx < len(self.rooms) - 1:
                sep = ttk.Separator(self.av_scrollable_frame, orient='horizontal')
                sep.pack(fill=tk.X, pady=4)

    def _build_reports(self):
        # Monthly Revenue Summary Section
        revenue_section = ttk.LabelFrame(self.report_frame, text="Monthly Revenue Summary", padding=8)
        revenue_section.pack(fill=tk.X, padx=8, pady=8)
        
        row = ttk.Frame(revenue_section)
        row.pack(fill=tk.X)
        ttk.Label(row, text="Month (YYYY-MM):").pack(side=tk.LEFT, padx=(0, 8))
        # Use hotel timezone for current month display
        hotel_tz = get_hotel_tz(self.cfg.timezone)
        current_month = now_hotel(hotel_tz).strftime('%Y-%m')
        self.month_var = tk.StringVar(value=current_month)
        ttk.Entry(row, textvariable=self.month_var, width=10).pack(side=tk.LEFT, padx=(0, 8))
        ttk.Button(row, text="Compute Revenue", command=self.refresh_revenue).pack(side=tk.LEFT)

        result_frame = ttk.Frame(revenue_section)
        result_frame.pack(fill=tk.X, pady=8)
        self.revenue_var = tk.StringVar(value="MYR 0.00")
        ttk.Label(result_frame, textvariable=self.revenue_var, font=("Segoe UI", 16, "bold")).pack()

        self.refresh_revenue()

        # Guest Reservation Details Section
        detail_section = ttk.LabelFrame(self.report_frame, text="Guest Reservation Details", padding=8)
        detail_section.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        # Date range inputs
        input_row = ttk.Frame(detail_section)
        input_row.pack(fill=tk.X, pady=(0, 8))
        
        ttk.Label(input_row, text="Start Date (YYYY-MM-DD):").pack(side=tk.LEFT, padx=(0, 8))
        # Default to first day of current month (in hotel timezone)
        today = now_hotel(hotel_tz)
        first_day = today.replace(day=1)
        self.start_date_entry = DateEntry(input_row, width=12, date_pattern='yyyy-mm-dd', firstweekday='sunday')
        self.start_date_entry.set_date(first_day)
        self.start_date_entry.pack(side=tk.LEFT, padx=(0, 16))
        # Bind start date change to auto-adjust end date
        self.start_date_entry.bind('<<DateEntrySelected>>', lambda e: self._on_report_start_change())
        
        ttk.Label(input_row, text="End Date (YYYY-MM-DD):").pack(side=tk.LEFT, padx=(0, 8))
        self.end_date_entry = DateEntry(input_row, width=12, date_pattern='yyyy-mm-dd', firstweekday='sunday')
        self.end_date_entry.pack(side=tk.LEFT, padx=(0, 16))
        # Bind end date change to validate date range
        self.end_date_entry.bind('<<DateEntrySelected>>', lambda e: self._validate_date_range(self.start_date_entry, self.end_date_entry, auto_adjust_end=True))
        
        # Set default end date to one day after start
        default_end = first_day + timedelta(days=1)
        self.end_date_entry.set_date(default_end)
        
        ttk.Button(input_row, text="Generate Report", command=self.refresh_guest_detail_report).pack(side=tk.LEFT)

        # Table for results
        table_frame = ttk.Frame(detail_section)
        table_frame.pack(fill=tk.BOTH, expand=True)

        columns = ("guest", "room", "checkin", "checkout", "nights", "total")
        self.detail_tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=10)
        self.detail_tree.heading("guest", text="Guest Name")
        self.detail_tree.heading("room", text="Room ID")
        self.detail_tree.heading("checkin", text="Check-In")
        self.detail_tree.heading("checkout", text="Check-Out")
        self.detail_tree.heading("nights", text="Nights")
        self.detail_tree.heading("total", text="Total Cost (MYR)")

        self.detail_tree.column("guest", width=150)
        self.detail_tree.column("room", width=80)
        self.detail_tree.column("checkin", width=100)
        self.detail_tree.column("checkout", width=100)
        self.detail_tree.column("nights", width=60)
        self.detail_tree.column("total", width=120)

        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.detail_tree.yview)
        self.detail_tree.configure(yscrollcommand=scrollbar.set)
        
        self.detail_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Grand total display
        total_frame = ttk.Frame(detail_section)
        total_frame.pack(fill=tk.X, pady=(8, 0))
        ttk.Label(total_frame, text="Grand Total:", font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT, padx=(0, 8))
        self.grand_total_var = tk.StringVar(value="MYR 0.00")
        ttk.Label(total_frame, textvariable=self.grand_total_var, font=("Segoe UI", 12, "bold")).pack(side=tk.LEFT)

        # Initial load
        self.refresh_guest_detail_report()

    def refresh_revenue(self):
        # Check admin privilege
        if not self._require_admin("Export Revenue Report"):
            return
        
        ym = self.month_var.get().strip()
        try:
            total = monthly_revenue_summary(self.paths.reservations, ym)
            self.revenue_var.set(f"MYR {total:.2f}")
        except Exception as e:
            self._show_error("Revenue Error", f"Failed to compute revenue: {str(e)}")

    def refresh_guest_detail_report(self):
        """Generate and display guest reservation detail report."""
        start = self.start_date_entry.get()
        end = self.end_date_entry.get()
        
        try:
            # Clear existing data
            for item in self.detail_tree.get_children():
                self.detail_tree.delete(item)
            
            # Get filtered reservations
            reservations = guest_reservation_detail_report(self.paths.reservations, start, end)
            
            # Populate table
            grand_total = 0.0
            for res in reservations:
                nights = compute_nights(res.check_in_date, res.check_out_date)
                self.detail_tree.insert("", tk.END, values=(
                    res.guest_name,
                    res.room_id,
                    res.check_in_date,
                    res.check_out_date,
                    nights,
                    f"{res.total_cost:.2f}"
                ))
                grand_total += res.total_cost
            
            # Update grand total
            self.grand_total_var.set(f"MYR {grand_total:.2f}")
            
        except Exception as e:
            self._show_error("Report Error", f"Failed to generate report: {str(e)}")


def run():
    app = App()
    app.mainloop()
