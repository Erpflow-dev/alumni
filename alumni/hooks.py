"""Frappe app hooks for the alumni app.

Most hooks are empty placeholders at T-001 (Phase 0 / Foundation). They get
populated as feature tickets land — see BUILD_TICKETS.md for the schedule.
The keys are kept here, even when empty, so future contributors see the
contract surface in one place rather than discovering them ad-hoc.

Versions: targets Frappe v16+ ONLY (per ADR-026). v14/v15 not supported.
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# App metadata
# ---------------------------------------------------------------------------

app_name = "alumni"
app_title = "Alumni"
app_publisher = "Erpflow"
app_description = (
    "Standalone Frappe v16 app for alumni networks. "
    "Supports school-connected (frappe/education + erpnext) and "
    "standalone install modes through the Adapter Layer."
)
app_email = "info@erpflow.dev"
app_license = "agpl-3.0"
app_logo_url = "/assets/alumni/images/logo.svg"

# Required Frappe apps (peer apps installed via `bench get-app`, not pip).
# Both modes require these. Optional apps (education, erpnext, drive,
# insights, etc.) are detected at runtime by the adapter selector — see
# INTEGRATIONS.md §0.
required_apps = ["payments", "buzz"]

# ---------------------------------------------------------------------------
# Static asset includes (populated in T-005, T-068, T-091, T-095)
# ---------------------------------------------------------------------------

app_include_css: list[str] = []
app_include_js: list[str] = []
web_include_css: list[str] = []
web_include_js: list[str] = []

# ---------------------------------------------------------------------------
# Fixtures (populated as DocTypes / Roles / Workflows / Email Templates land)
# ---------------------------------------------------------------------------

fixtures: list = []

# ---------------------------------------------------------------------------
# Permissions (T-006 onwards — see SPEC.md §06)
# ---------------------------------------------------------------------------

# Row-level filters per DocType. Keys are DocType names, values are the
# importable path to a callable taking (user) -> SQL fragment.
permission_query_conditions: dict[str, str] = {}

# DocType-level extra checks. Keys are DocType names, values are
# importable path to a callable taking (doc, user) -> bool.
has_permission: dict[str, str] = {}

# ---------------------------------------------------------------------------
# Doc events (T-006 onwards)
# ---------------------------------------------------------------------------
# Hooks fired on Document CRUD lifecycle. Per CLAUDE.md hard rule #1,
# any cross-app document references inside these handlers MUST go through
# alumni.integrations.<area>.

doc_events: dict[str, dict[str, str]] = {}

# ---------------------------------------------------------------------------
# Scheduler (T-009 onwards — see SPEC.md §08)
# ---------------------------------------------------------------------------

scheduler_events: dict[str, list[str] | dict[str, str]] = {
    "cron": {},
    "hourly": [],
    "daily": [],
    "weekly": [],
}

# ---------------------------------------------------------------------------
# Boot session (T-066 — 2FA gate, T-038 — preferred language)
# ---------------------------------------------------------------------------

boot_session: str | None = None

# ---------------------------------------------------------------------------
# Setup wizard (T-004)
# ---------------------------------------------------------------------------
# The first-run wizard is exposed as Frappe Onboarding; the entry point
# lands in T-004. Until then the default Frappe onboarding applies.

# ---------------------------------------------------------------------------
# Whitelisted methods (populated in alumni/api.py — T-006 onwards)
# ---------------------------------------------------------------------------
# We use @frappe.whitelist() decorators directly; this list stays empty
# unless we need to whitelist methods on classes (uncommon in this app).

override_whitelisted_methods: dict[str, str] = {}

# ---------------------------------------------------------------------------
# Translations (T-074)
# ---------------------------------------------------------------------------
# Frappe v16 reads alumni/translations/<lang>.csv automatically once any
# file is present in that folder. Per ADR-038 we ship 8 base languages.

# ---------------------------------------------------------------------------
# Website / public site (T-044, T-045)
# ---------------------------------------------------------------------------

website_route_rules: list[dict] = []
website_redirects: list[dict] = []
