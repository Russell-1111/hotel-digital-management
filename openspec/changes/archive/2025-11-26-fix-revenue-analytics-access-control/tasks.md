## 1. UI Layer Access Control

- [x] 1.1 Modify `app/ui/main.py` `_build_reports()` method to wrap analytics_section creation in role check
- [x] 1.2 Add conditional: `if self.current_user['role'] == 'admin':` before line 1807 (analytics_section creation)
- [x] 1.3 Indent analytics_section frame creation and all children (lines 1807-1822) under the conditional block
- [x] 1.4 Verify proper indentation for: analytics_section LabelFrame, analytics_desc Label, ttk.Button

## 2. Callback Authorization Guard

- [x] 2.1 Modify `app/ui/main.py` `_show_revenue_analytics()` method to add fail-safe guard
- [x] 2.2 Add as first statement (after docstring): `if not self._require_admin("Access Revenue Analytics"): return`
- [x] 2.3 Verify guard prevents dialog opening when authorization fails

## 3. Unit Tests for UI Access Control

- [x] 3.1 Add test in `tests/test_ui.py`: `test_analytics_section_hidden_for_staff`
- [x] 3.2 Test SHALL initialize App with staff user and verify analytics_section not in UI tree
- [x] 3.3 Add test: `test_analytics_section_visible_for_admin`
- [x] 3.4 Test SHALL initialize App with admin user and verify analytics_section exists and is visible
- [x] 3.5 Add test: `test_revenue_analytics_callback_blocked_for_staff`
- [x] 3.6 Test SHALL mock _require_admin to return False and verify dialog not opened
- [x] 3.7 Add test: `test_revenue_analytics_callback_allowed_for_admin`
- [x] 3.8 Test SHALL mock _require_admin to return True and verify dialog opened successfully

## 4. Integration Testing

- [x] 4.1 Manual test: Login as staff user, navigate to Reports tab, verify Analytics section not visible
- [x] 4.2 Manual test: Login as admin user, navigate to Reports tab, verify Analytics section visible
- [x] 4.3 Manual test: As admin, click "Revenue by Room Type" button, verify dialog opens
- [x] 4.4 Verify no console errors or exceptions during role-based rendering

## 5. Security Validation

- [x] 5.1 Code review: Confirm no other paths to access revenue analytics bypass role check
- [x] 5.2 Review app/analytics.py functions to ensure they have no direct UI exposure
- [x] 5.3 Verify _require_admin helper is consistently used for all admin-only features
- [x] 5.4 Update security documentation if needed

## 6. Documentation Updates

- [x] 6.1 Update USER_GUIDE.md to clarify Analytics feature is admin-only
- [x] 6.2 Add note in README.md about role-based access control for sensitive features
- [x] 6.3 Document the defense-in-depth approach (UI hiding + callback guard)
