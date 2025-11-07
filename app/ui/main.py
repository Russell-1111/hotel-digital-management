from __future__ import annotations
import logging
import sys
import tkinter as tk
from tkinter import ttk
from pathlib import Path
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo
try:
    # Use the robust subclass that refreshes the popup to avoid arrow glitches
    from app.ui.fixed_dateentry import FixedDateEntry as DateEntry
except Exception:
    # Fallback to standard DateEntry if the subclass cannot be imported for any reason
    from tkcalendar import DateEntry

from app.rooms import load_config
from app.storage import ensure_dirs, start_daily_backup_scheduler
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
        self.paths = ensure_dirs(self.cfg)
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
        
        # Add timezone info in footer status bar
        footer = ttk.Frame(self)
        footer.pack(side=tk.BOTTOM, fill=tk.X, padx=8, pady=4)
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
