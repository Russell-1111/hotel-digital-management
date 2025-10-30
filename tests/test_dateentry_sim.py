import sys
import pathlib
import tkinter as tk
import datetime
import traceback

# Ensure project root is on sys.path so 'app' package can be imported when
# running the script from the tests/ folder.
proj_root = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(proj_root))

from app.ui.fixed_dateentry import FixedDateEntry

out = []

def safe_call(obj, name):
    fn = getattr(obj, name, None)
    if fn is None:
        out.append(f"{name}: MISSING")
        return False, None
    try:
        fn()
        out.append(f"{name}: OK")
        return True, None
    except Exception as e:
        out.append(f"{name}: EXCEPTION {e}")
        out.append(traceback.format_exc())
        return False, e

root = tk.Tk()
root.title('FixedDateEntry Test')
# keep window small but visible
root.geometry('300x100')

fe = FixedDateEntry(root, width=12, date_pattern='yyyy-mm-dd')
fe.pack(padx=10, pady=10)
root.update()

out.append('--- Step 1: Open popup (initial)')
try:
    # call private show (our subclass provides it)
    fe._show_calendar()
    root.update()
    out.append('popup1: opened')
except Exception as e:
    out.append('popup1: failed to open')
    out.append(traceback.format_exc())

cal = getattr(fe, '_calendar', None)
if cal is None:
    out.append('calendar1: MISSING')
else:
    out.append(f'calendar1: type={type(cal)}')

# Try navigating next month while open
if cal is not None:
    ok, err = safe_call(cal, '_next_month')

# Simulate selecting a date: set the text and withdraw the popup
out.append('--- Step 2: Simulate selection and close')
try:
    today = datetime.date.today()
    fe._date = today
    # Use public method if available
    try:
        fe._set_text(fe.format_date(today))
    except Exception:
        try:
            fe.set_date(today)
        except Exception:
            pass
    # withdraw popup
    top = getattr(fe, '_top_cal', None)
    if top is not None:
        try:
            top.withdraw()
            out.append('popup1: withdrawn')
        except Exception:
            out.append('popup1: withdraw failed')
            out.append(traceback.format_exc())
    else:
        out.append('popup1: _top_cal missing')
except Exception:
    out.append('simulate selection: exception')
    out.append(traceback.format_exc())

root.update()

out.append('--- Step 3: Reopen popup')
try:
    fe._show_calendar()
    root.update()
    out.append('popup2: opened')
except Exception:
    out.append('popup2: failed to open')
    out.append(traceback.format_exc())

cal2 = getattr(fe, '_calendar', None)
if cal2 is None:
    out.append('calendar2: MISSING')
else:
    out.append(f'calendar2: type={type(cal2)}')

# Try navigating next and prev month while open after reopen
if cal2 is not None:
    ok1, err1 = safe_call(cal2, '_next_month')
    ok2, err2 = safe_call(cal2, '_prev_month')

out.append('--- Final attributes dump')
for name in ('_top_cal', '_calendar', '_date'):
    out.append(f"{name} present: {hasattr(fe, name)}")

# Print results
print('\n'.join(out))

# Keep window open briefly so user can observe if running interactively
root.after(2000, root.destroy)
root.mainloop()
