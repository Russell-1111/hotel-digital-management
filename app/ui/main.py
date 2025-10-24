from __future__ import annotations
import tkinter as tk
from tkinter import ttk
from pathlib import Path
from datetime import datetime

from app.config import load_config
from app.storage import ensure_dirs, start_daily_backup_scheduler
from app.reporting import daily_checkin_list, daily_checkout_list, monthly_revenue_summary
from app.rooms import load_rooms, index_by_id
from app.reservations import (
    list_reservations,
    create_reservation,
    cancel_reservation,
    modify_reservation,
    is_room_available,
    auto_status_transitions,
)


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Hotel Digital Management - Front Desk")
        self.geometry("800x500")

        self.cfg = load_config(Path("config.ini"))
        self.paths = ensure_dirs(self.cfg)
        start_daily_backup_scheduler(self.cfg)

        nb = ttk.Notebook(self)
        nb.pack(fill=tk.BOTH, expand=True)

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

    def _build_ops(self):
        # Date input
        row = ttk.Frame(self.ops_frame)
        row.pack(fill=tk.X, pady=5, padx=8)
        ttk.Label(row, text="Date (YYYY-MM-DD):").pack(side=tk.LEFT)
        self.ops_date_var = tk.StringVar(value=datetime.now().strftime('%Y-%m-%d'))
        ttk.Entry(row, textvariable=self.ops_date_var, width=12).pack(side=tk.LEFT, padx=6)
        ttk.Button(row, text="Refresh", command=self.refresh_ops).pack(side=tk.LEFT)

        # Lists
        lists = ttk.Frame(self.ops_frame)
        lists.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)
        left = ttk.LabelFrame(lists, text="Today's Check-Ins")
        right = ttk.LabelFrame(lists, text="Today's Check-Outs")
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0,4))
        right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(4,0))

        self.ins_list = tk.Listbox(left)
        self.outs_list = tk.Listbox(right)
        self.ins_list.pack(fill=tk.BOTH, expand=True)
        self.outs_list.pack(fill=tk.BOTH, expand=True)

        self.refresh_ops()

    def refresh_ops(self):
        date_str = self.ops_date_var.get().strip()
        try:
            datetime.strptime(date_str, '%Y-%m-%d')
        except ValueError:
            return
        # Apply automatic status transitions before showing lists
        auto_status_transitions(
            self.paths.reservations,
            datetime.now(),
            self.cfg.check_in_time,
            self.cfg.check_out_time,
        )
        ins = daily_checkin_list(self.paths.reservations, date_str)
        outs = daily_checkout_list(self.paths.reservations, date_str)
        self.ins_list.delete(0, tk.END)
        self.outs_list.delete(0, tk.END)
        for r in ins:
            self.ins_list.insert(tk.END, f"{r.reservation_id} | Room {r.room_id} | {r.guest_name}")
        for r in outs:
            self.outs_list.insert(tk.END, f"{r.reservation_id} | Room {r.room_id} | {r.guest_name}")

    # --- Reservations tab ---
    def _build_reservations(self):
        form = ttk.LabelFrame(self.res_frame, text="New Reservation")
        form.pack(fill=tk.X, padx=8, pady=8)

        # Row 1: Guest info
        r1 = ttk.Frame(form)
        r1.pack(fill=tk.X, pady=4)
        ttk.Label(r1, text="Guest Name").grid(row=0, column=0, sticky=tk.W)
        self.guest_name = tk.StringVar()
        ttk.Entry(r1, textvariable=self.guest_name, width=24).grid(row=0, column=1, padx=6)
        ttk.Label(r1, text="Phone").grid(row=0, column=2, sticky=tk.W)
        self.guest_phone = tk.StringVar()
        ttk.Entry(r1, textvariable=self.guest_phone, width=16).grid(row=0, column=3, padx=6)
        ttk.Label(r1, text="Email").grid(row=0, column=4, sticky=tk.W)
        self.guest_email = tk.StringVar()
        ttk.Entry(r1, textvariable=self.guest_email, width=24).grid(row=0, column=5, padx=6)

        # Row 2: Dates and guests
        r2 = ttk.Frame(form)
        r2.pack(fill=tk.X, pady=4)
        ttk.Label(r2, text="Check-in (YYYY-MM-DD)").grid(row=0, column=0, sticky=tk.W)
        self.ci_var = tk.StringVar(value=datetime.now().strftime('%Y-%m-%d'))
        ttk.Entry(r2, textvariable=self.ci_var, width=12).grid(row=0, column=1, padx=6)
        ttk.Label(r2, text="Check-out (YYYY-MM-DD)").grid(row=0, column=2, sticky=tk.W)
        self.co_var = tk.StringVar(value=(datetime.now()).strftime('%Y-%m-%d'))
        ttk.Entry(r2, textvariable=self.co_var, width=12).grid(row=0, column=3, padx=6)
        ttk.Label(r2, text="Guests").grid(row=0, column=4, sticky=tk.W)
        self.num_guests = tk.StringVar(value="1")
        ttk.Entry(r2, textvariable=self.num_guests, width=5).grid(row=0, column=5, padx=6)

        # Row 3: Room selection
        r3 = ttk.Frame(form)
        r3.pack(fill=tk.X, pady=4)
        ttk.Label(r3, text="Available Room").grid(row=0, column=0, sticky=tk.W)
        self.room_choice = tk.StringVar()
        self.room_combo = ttk.Combobox(r3, textvariable=self.room_choice, width=20, state="readonly")
        self.room_combo.grid(row=0, column=1, padx=6)
        ttk.Button(r3, text="Check Availability", command=self.refresh_available_rooms).grid(row=0, column=2)
        ttk.Button(r3, text="Create Reservation", command=self.create_reservation_click).grid(row=0, column=3, padx=6)

        # Existing reservations list
        list_frame = ttk.LabelFrame(self.res_frame, text="Existing Reservations")
        list_frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)
        self.res_list = tk.Listbox(list_frame)
        self.res_list.pack(fill=tk.BOTH, expand=True)
        btns = ttk.Frame(self.res_frame)
        btns.pack(fill=tk.X, padx=8, pady=(0,8))
        ttk.Button(btns, text="Refresh", command=self.refresh_reservations_list).pack(side=tk.LEFT)
        ttk.Button(btns, text="Modify Selected", command=self.modify_selected).pack(side=tk.LEFT, padx=6)
        ttk.Button(btns, text="Cancel Selected", command=self.cancel_selected).pack(side=tk.LEFT)

        # Initial population
        self.refresh_available_rooms()
        self.refresh_reservations_list()

    def refresh_reservations_list(self):
        self.res_list.delete(0, tk.END)
        for r in list_reservations(self.paths.reservations):
            self.res_list.insert(tk.END, f"{r.reservation_id} | Room {r.room_id} | {r.guest_name} | {r.check_in_date}->{r.check_out_date} | {r.status} | MYR {r.total_cost:.2f}")

    def refresh_available_rooms(self):
        # Determine available rooms for the entered date range
        ci = self.ci_var.get().strip()
        co = self.co_var.get().strip()
        # Basic validation
        try:
            datetime.strptime(ci, '%Y-%m-%d')
            datetime.strptime(co, '%Y-%m-%d')
        except ValueError:
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
        else:
            self.room_choice.set('')

    def create_reservation_click(self):
        choice = self.room_choice.get()
        if not choice:
            return
        room_id = choice.split()[0]
        room = self.rooms_by_id.get(room_id)
        if not room:
            return
        try:
            num_guests = int(self.num_guests.get())
        except ValueError:
            num_guests = 1
        try:
            create_reservation(
                self.cfg,
                self.paths.reservations,
                room,
                self.guest_name.get().strip(),
                self.guest_phone.get().strip(),
                self.guest_email.get().strip(),
                self.ci_var.get().strip(),
                self.co_var.get().strip(),
                num_guests,
            )
        except Exception:
            # Minimal: ignore detailed error UI for now
            return
        self.refresh_available_rooms()
        self.refresh_reservations_list()
        self.refresh_ops()

    def cancel_selected(self):
        # Expect reservation_id at the start of the list item
        sel = self.res_list.curselection()
        if not sel:
            return
        text = self.res_list.get(sel[0])
        rid = text.split('|')[0].strip()
        try:
            cancel_reservation(self.paths.reservations, rid)
        except Exception:
            return
        self.refresh_reservations_list()
        self.refresh_ops()

    def modify_selected(self):
        """Open a dialog to modify the selected reservation."""
        sel = self.res_list.curselection()
        if not sel:
            return
        text = self.res_list.get(sel[0])
        rid = text.split('|')[0].strip()
        
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
        mod_ci = tk.StringVar(value=target.check_in_date)
        ttk.Entry(frm, textvariable=mod_ci, width=30).grid(row=3, column=1, pady=4)

        ttk.Label(frm, text="Check-out (YYYY-MM-DD)").grid(row=4, column=0, sticky=tk.W, pady=4)
        mod_co = tk.StringVar(value=target.check_out_date)
        ttk.Entry(frm, textvariable=mod_co, width=30).grid(row=4, column=1, pady=4)

        ttk.Label(frm, text="Number of Guests").grid(row=5, column=0, sticky=tk.W, pady=4)
        mod_guests = tk.StringVar(value=str(target.num_guests))
        ttk.Entry(frm, textvariable=mod_guests, width=30).grid(row=5, column=1, pady=4)

        ttk.Label(frm, text="Room").grid(row=6, column=0, sticky=tk.W, pady=4)
        mod_room_var = tk.StringVar()
        mod_room_combo = ttk.Combobox(frm, textvariable=mod_room_var, width=28, state="readonly")
        mod_room_combo.grid(row=6, column=1, pady=4)

        # Populate available rooms for new dates
        def refresh_mod_rooms():
            ci = mod_ci.get().strip()
            co = mod_co.get().strip()
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
            new_ci = mod_ci.get().strip()
            new_co = mod_co.get().strip()
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
        frm = ttk.Frame(self.avail_frame)
        frm.pack(fill=tk.X, padx=8, pady=8)
        ttk.Label(frm, text="Start (YYYY-MM-DD)").grid(row=0, column=0, sticky=tk.W)
        self.av_start = tk.StringVar(value=datetime.now().strftime('%Y-%m-%d'))
        ttk.Entry(frm, textvariable=self.av_start, width=12).grid(row=0, column=1, padx=6)
        ttk.Label(frm, text="End (YYYY-MM-DD)").grid(row=0, column=2, sticky=tk.W)
        self.av_end = tk.StringVar(value=datetime.now().strftime('%Y-%m-%d'))
        ttk.Entry(frm, textvariable=self.av_end, width=12).grid(row=0, column=3, padx=6)
        ttk.Button(frm, text="Check", command=self.refresh_availability).grid(row=0, column=4, padx=6)

        self.av_list = tk.Listbox(self.avail_frame)
        self.av_list.pack(fill=tk.BOTH, expand=True, padx=8, pady=(0,8))

        self.refresh_availability()

    def refresh_availability(self):
        start = self.av_start.get().strip()
        end = self.av_end.get().strip()
        try:
            datetime.strptime(start, '%Y-%m-%d')
            datetime.strptime(end, '%Y-%m-%d')
        except ValueError:
            return
        reservations = list_reservations(self.paths.reservations)
        self.av_list.delete(0, tk.END)
        for room in self.rooms:
            ok = is_room_available(reservations, room.room_id, start, end)
            status = "Available" if ok else "Unavailable"
            self.av_list.insert(tk.END, f"Room {room.room_id} ({room.room_type}) - {status}")

    def _build_reports(self):
        row = ttk.Frame(self.report_frame)
        row.pack(fill=tk.X, pady=5, padx=8)
        ttk.Label(row, text="Month (YYYY-MM):").pack(side=tk.LEFT)
        self.month_var = tk.StringVar(value=datetime.now().strftime('%Y-%m'))
        ttk.Entry(row, textvariable=self.month_var, width=8).pack(side=tk.LEFT, padx=6)
        ttk.Button(row, text="Compute Revenue", command=self.refresh_revenue).pack(side=tk.LEFT)

        self.revenue_var = tk.StringVar(value="MYR 0.00")
        ttk.Label(self.report_frame, textvariable=self.revenue_var, font=("Segoe UI", 14, "bold")).pack(pady=10)

        self.refresh_revenue()

    def refresh_revenue(self):
        ym = self.month_var.get().strip()
        total = monthly_revenue_summary(self.paths.reservations, ym)
        self.revenue_var.set(f"MYR {total:.2f}")


def run():
    app = App()
    app.mainloop()
