"""Frappe Docs config for the alumni app (legacy compatibility shim)."""

source_link = "https://github.com/Erpflow-dev/alumni"
docs_base_url = "https://github.com/Erpflow-dev/alumni"
headline = "Alumni — a standalone Frappe v16 app for alumni networks"
sub_heading = "Two install modes (school-connected, standalone) via the Adapter Layer"


def get_context(context):  # noqa: ARG001 — Frappe contract requires this name
    context.brand_html = "Alumni"
