# Fix Revenue Analytics Access Control

## Why
Currently, users with the 'Staff' role can see and access the "Revenue by Room Type" Analytics feature in the Reports tab. Staff users can successfully click the "Revenue by Room Type" button and export revenue analytics reports, which bypasses role-based access control. This is a security vulnerability because revenue analytics should be restricted to administrators only. The feature was implemented without proper authorization checks, allowing unauthorized access to sensitive business data.

## What Changes
- Add explicit role-based access control requirements to a new `auth` capability specification
- Modify UI rendering logic to conditionally hide the Analytics section UI controls for non-admin users
- Add fail-safe authorization guard in the revenue analytics callback method
- Update tests to verify access control enforcement at both UI and backend levels

Specific code changes:
- In `app/ui/main.py`, `_build_reports()` method: Wrap the creation of `analytics_section` frame and its children (label and button) in a conditional check: `if self.current_user['role'] == 'admin':`
- In `app/ui/main.py`, `_show_revenue_analytics()` method: Add security guard clause at the beginning: `if not self._require_admin("Access Revenue Analytics"): return`
- Add unit tests to verify UI section is not created for staff users
- Add functional tests to verify callback guard prevents staff access even if UI controls were somehow exposed

## Impact
- Affected specs: `auth` (NEW), `ui`
- Affected code:
  - Modified: `app/ui/main.py` (UI conditional rendering and callback guard)
  - Modified: `tests/test_ui.py` (add access control tests)
- Security: Closes unauthorized access to revenue analytics for staff users
- UX: Staff users will no longer see the Analytics section in the Reports tab (cleaner interface)
