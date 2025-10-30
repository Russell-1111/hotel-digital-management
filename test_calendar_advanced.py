"""
Advanced test to verify calendar navigation with detailed event tracking.
"""

import tkinter as tk
from tkinter import ttk
from app.ui.fixed_dateentry import FixedDateEntry


class CalendarTester(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Calendar Navigation Tester")
        self.geometry("600x500")
        
        # Instructions
        instructions = """
🎯 TESTING INSTRUCTIONS:

1. Click calendar icon to open dropdown
2. Click the NEXT MONTH arrow (→) - should work ✓
3. Click a GRAYED OUT date from next month
   Expected: Calendar navigates to that month and STAYS OPEN
4. Click the NEXT MONTH arrow again - should still work ✓
5. Repeat steps 3-4 several times
6. Finally, click a date in the CURRENT month - calendar should close

✅ SUCCESS: If you can navigate continuously after clicking grayed dates
❌ FAIL: If navigation arrows stop working after clicking grayed dates
"""
        
        tk.Label(self, text=instructions, justify='left', 
                font=('Consolas', 9), bg='lightyellow', 
                padx=10, pady=10).pack(fill='x')
        
        # Date Entry
        frame = tk.Frame(self, bg='white', pady=20)
        frame.pack(fill='x')
        
        tk.Label(frame, text="Test Date Entry:", font=('Arial', 11, 'bold'), 
                bg='white').pack(side='left', padx=20)
        
        self.date_entry = FixedDateEntry(frame, width=15, 
                                        date_pattern='yyyy-mm-dd', 
                                        firstweekday='sunday')
        self.date_entry.pack(side='left', padx=10)
        
        # Status indicator
        self.status_var = tk.StringVar(value="Ready to test")
        status_label = tk.Label(self, textvariable=self.status_var, 
                               font=('Arial', 10, 'bold'), 
                               fg='blue', pady=10)
        status_label.pack()
        
        # Event log
        tk.Label(self, text="Event Log:", font=('Arial', 10, 'bold')).pack(pady=5)
        
        log_frame = tk.Frame(self)
        log_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        scrollbar = tk.Scrollbar(log_frame)
        scrollbar.pack(side='right', fill='y')
        
        self.log_text = tk.Text(log_frame, height=15, yscrollcommand=scrollbar.set, 
                               font=('Consolas', 8))
        self.log_text.pack(fill='both', expand=True)
        scrollbar.config(command=self.log_text.yview)
        
        # Control buttons
        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=10)
        
        tk.Button(btn_frame, text="Clear Log", command=self.clear_log).pack(side='left', padx=5)
        tk.Button(btn_frame, text="Force Open Calendar", 
                 command=self.force_open).pack(side='left', padx=5)
        tk.Button(btn_frame, text="Check State", 
                 command=self.check_state).pack(side='left', padx=5)
        
        # Bind events
        self.date_entry.bind('<<DateEntrySelected>>', self.on_date_selected)
        
        # Monitor calendar window state
        self.check_calendar_state()
        
        self.log("✓ Application started")
        self.log("📅 Click the calendar icon to begin testing")
    
    def log(self, message):
        """Add message to log."""
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        self.log_text.insert('end', f"[{timestamp}] {message}\n")
        self.log_text.see('end')
        print(f"[{timestamp}] {message}")
    
    def on_date_selected(self, event):
        """Handle date selection."""
        selected = self.date_entry.get()
        self.log(f"✓ Date selected: {selected}")
        self.status_var.set(f"Selected: {selected}")
    
    def clear_log(self):
        """Clear the event log."""
        self.log_text.delete('1.0', 'end')
        self.log("📝 Log cleared")
    
    def force_open(self):
        """Force open the calendar."""
        try:
            self.date_entry.drop_down()
            self.log("📅 Calendar forced open")
        except Exception as e:
            self.log(f"❌ Error opening calendar: {e}")
    
    def check_state(self):
        """Check current calendar state."""
        try:
            nav_mode = getattr(self.date_entry, '_navigation_mode', 'N/A')
            has_top = hasattr(self.date_entry, '_top_cal')
            
            if has_top:
                try:
                    state = self.date_entry._top_cal.state()
                    self.log(f"ℹ️  Calendar window state: {state}")
                    self.log(f"ℹ️  Navigation mode: {nav_mode}")
                except:
                    self.log("ℹ️  Calendar window: not visible")
                    self.log(f"ℹ️  Navigation mode: {nav_mode}")
            else:
                self.log("ℹ️  Calendar window: doesn't exist yet")
                
        except Exception as e:
            self.log(f"❌ Error checking state: {e}")
    
    def check_calendar_state(self):
        """Periodically check if calendar is open."""
        if hasattr(self.date_entry, '_top_cal'):
            try:
                state = self.date_entry._top_cal.state()
                if state == 'normal':
                    self.status_var.set("🟢 Calendar OPEN - Try navigating!")
                else:
                    self.status_var.set("🔴 Calendar CLOSED")
            except:
                self.status_var.set("🔴 Calendar CLOSED")
        
        # Check again in 200ms
        self.after(200, self.check_calendar_state)


if __name__ == "__main__":
    app = CalendarTester()
    app.mainloop()
