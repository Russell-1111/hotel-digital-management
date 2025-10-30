from __future__ import annotations

"""
FixedDateEntry
----------------
Lightweight subclass of tkcalendar.DateEntry that defensively rebuilds the
calendar popup each time it is opened. This mitigates an intermittent issue
where, after selecting a date and reopening the popup, the month navigation
arrows appear but don't change the displayed month on some systems.

Design goals:
- Keep the same public API as tkcalendar.DateEntry
- Avoid touching application logic; fix is fully encapsulated
- Be resilient to tkcalendar private method/name changes across 1.6.x

Approach:
- When the popup is about to be shown, destroy any previous toplevel/calendar
  so tkcalendar recreates fresh widgets with fresh bindings.
- Fall back safely if private methods differ across versions.

This is intentionally conservative. If tkcalendar changes internals, the
fallbacks become no-ops without breaking the app.
"""

from typing import Any
try:
	from tkcalendar import DateEntry as _BaseDateEntry  # type: ignore
except Exception:  # pragma: no cover - tkcalendar is required by requirements.txt
	_BaseDateEntry = object  # type: ignore


class FixedDateEntry(_BaseDateEntry):  # type: ignore[misc]
	"""DateEntry with robust popup refresh for reliable header arrow navigation.

	On some platforms (Windows with tkcalendar 1.5.x), the calendar header arrow
	binding can become stale after a date selection and focus transitions can
	prematurely withdraw the popup. This subclass refreshes the calendar display
	after every popup open and softens focus-out handling to restore reliable
	navigation.
	"""

	def __init__(self, *args, **kwargs):
		# Initialize base DateEntry
		super().__init__(*args, **kwargs)  # type: ignore[misc]
		# Replace Calendar <FocusOut> with a guard that keeps the popup open when
		# focus moves within the popup (e.g., header arrows), only withdrawing when
		# it actually leaves the popup entirely.
		try:
			cal = getattr(self, "_calendar", None)
			if cal is not None:
				try:
					cal.unbind('<FocusOut>')
				except Exception:
					pass
				cal.bind('<FocusOut>', self._focus_out_guard, add='+')
		except Exception:
			# Non-fatal if binding fails
			pass

	def drop_down(self, *args: Any, **kwargs: Any) -> None:
		"""Show/hide the popup calendar and run a post-open refresh."""
		# Call the base implementation (which either shows or hides the popup)
		try:
			super().drop_down(*args, **kwargs)  # type: ignore[attr-defined]
		except Exception:
			# Defensive: if base doesn't have drop_down, do nothing (user can still type)
			pass
		# If the popup is now visible, schedule a defensive refresh to ensure
		# header navigation controls are bound and functional.
		self.after(0, self._post_open_refresh)

	def _post_open_refresh(self) -> None:
		"""Force a harmless refresh of the header/navigation state.

		We do a best-effort sequence:
		- Check if the popup is actually visible
		- Call the calendar's _display_calendar() method which rebuilds header
		  widgets and re-binds header buttons, ensuring arrows work even after
		  reopening post-selection on Windows tkcalendar 1.5.x.
		"""
		try:
			cal = getattr(self, "_calendar", None)
			top = getattr(self, "_top_cal", None)
			# Only refresh if the popup is currently open (mapped)
			if cal is None or top is None:
				return
			if not cal.winfo_ismapped():
				return
			# Focus the calendar (helps ensure events are routed correctly)
			try:
				cal.focus_set()
			except Exception:
				pass
			# Refresh the calendar display which re-creates header widgets
			# with fresh bindings, fixing the arrow navigation issue.
			try:
				cal._display_calendar()  # type: ignore[attr-defined]
			except Exception:
				# Never fail UI due to private method differences
				pass
		except Exception:
			pass

	def _focus_out_guard(self, event=None) -> None:
		"""Safer FocusOut handler: keep popup open if focus is still within it.

		This prevents premature withdrawal when clicking header arrows or other
		controls inside the calendar popup. If focus truly leaves the popup and
		the entry, we withdraw to match base behavior.
		"""
		try:
			top = getattr(self, "_top_cal", None)
			cal = getattr(self, "_calendar", None)
			if top is None or cal is None:
				return
			focus = self.focus_get()
			# If focus is still on the entry itself or within the popup toplevel,
			# do not withdraw.
			if focus is not None:
				try:
					if focus == self or focus.winfo_toplevel() == top:
						return
				except Exception:
					pass
			# Otherwise, withdraw like the base implementation
			try:
				top.withdraw()
				self.state(['!pressed'])
			except Exception:
				pass
		except Exception:
			pass

