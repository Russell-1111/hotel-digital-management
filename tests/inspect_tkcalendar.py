import sys, pathlib
proj_root = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(proj_root))
try:
    import tkcalendar
    from tkcalendar import DateEntry
    try:
        from tkcalendar import Calendar
        print('Calendar methods:', [n for n in dir(Calendar) if n.startswith('_')][:50])
    except Exception:
        print('Could not import Calendar class')
    print('tkcalendar version:', getattr(tkcalendar, '__version__', 'unknown'))
    names = [n for n in dir(DateEntry) if n.startswith('_')]
    print('DateEntry private attrs/methods:', names)
    import inspect
    try:
        src = inspect.getsource(DateEntry)
        print('\n--- DateEntry source start ---\n')
        print(src[:8000])
        print('\n--- DateEntry source truncated (first 8k chars) ---\n')
    except Exception as e:
        print('could not get source:', e)
    # Try to print drop_down implementation if present
    try:
        if hasattr(DateEntry, 'drop_down'):
            print('\n--- drop_down source ---\n')
            print(inspect.getsource(DateEntry.drop_down))
        else:
            print('DateEntry.drop_down: MISSING')
    except Exception as e:
        print('could not get drop_down source:', e)
    # Try to create a root and a DateEntry and inspect attributes after calling
    import tkinter as tk
    root = tk.Tk()
    de = DateEntry(root)
    print('has _top_cal before show:', hasattr(de, '_top_cal'))
    # Try different show/toggle method names
    for name in ('_show_calendar','_toggle_calendar','show_calendar','toggle_calendar','_open','open'):
        print(name, 'exists:', hasattr(de, name))
    root.destroy()
except Exception as e:
    print('inspect error:', e)
    raise
