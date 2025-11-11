"""
Quick visual test for login dialog improvements.
This script demonstrates the new UX features:
1. Clear button (✕) next to username field
2. Placeholder text when username is empty
3. Visual distinction for remembered vs. new usernames
"""

import tkinter as tk
from pathlib import Path
from app.ui.main import LoginDialog
from app.rooms import load_config

def test_login_dialog():
    """Test the improved login dialog."""
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    
    cfg = load_config(Path("config.ini"))
    db_path = Path("data/reservations.db")
    
    # Create and show the login dialog
    dialog = LoginDialog(root, db_path, cfg)
    
    print("Login Dialog Test")
    print("=" * 50)
    print("New features to test:")
    print("1. Clear button (✕) - Click to clear username")
    print("2. Placeholder text - 'Enter your username' when empty")
    print("3. Visual feedback - Gray text for remembered username")
    print("4. Editable field - You can change the username")
    print("=" * 50)
    
    root.mainloop()

if __name__ == "__main__":
    test_login_dialog()
