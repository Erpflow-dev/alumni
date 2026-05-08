# Upstream issue draft — buzz: toggle_test_mode at import time breaks bench commands when CI=true

> Draft to file against [BuildWithHussain/buzz](https://github.com/BuildWithHussain/buzz) **after** PR #4 (alumni `fix/ci-yarn-cache`) merges. Maintainer feedback during our active fix cycle creates churn — better to file with full context, a working pin, and a link to the merged workaround.

---

**Title:** `buzz/__init__.py:toggle_test_mode(True) at import time breaks bench commands when CI=true`

**Body:**

Since `16ef2563` (refactor: use frappe's toogle_test_mode for enabling testing, 2026-02-02), `buzz/__init__.py` calls `toggle_test_mode(True)` at module import time when the `CI` env var is set:

```python
__version__ = "0.0.1"

import os

if os.environ.get("CI"):
    import frappe
    from frappe.tests.utils import toggle_test_mode

    toggle_test_mode(True)
```

GitHub Actions sets `CI=true` on every job by default, so this fires during bench's CLI command discovery (`get_app_commands` walks installed apps and imports each `<app>.commands` before any frappe context is initialized).

`toggle_test_mode` reads `frappe.local.flags`, which doesn't exist at that point, so importing buzz raises `AttributeError: flags`. Any bench CLI command run with `CI=true` crashes — including `bench install-app`, `bench migrate`, `bench build`.

**Repro** (Frappe v16.16.0 + buzz HEAD):

```bash
CI=true bench --site test install-app some-other-app
```

Traceback:

```
File ".../frappe-bench/apps/buzz/buzz/__init__.py", line 9, in <module>
    toggle_test_mode(True)
File ".../frappe/tests/utils/__init__.py", line 62, in toggle_test_mode
    frappe.local.flags.in_test = enable
File ".../frappe/utils/local.py", line 28, in __getattribute__
    raise AttributeError(name)
AttributeError: flags
```

**Possible fixes** (any of):

- Defer the toggle — let frappe's test runner set `in_test` itself, not at module import time.
- Gate on a more specific env var than `CI` (e.g., `FRAPPE_IN_TEST` as `5118a99d` did before the refactor).
- Wrap in `try/except AttributeError` so import succeeds outside frappe context.

**Workaround for downstream consumers:** pin to `5118a99d` (the commit immediately before the refactor) until fixed. That version uses `FRAPPE_IN_TEST` instead of `CI` and a simpler `frappe.in_test = True` attribute set, with no fragile `frappe.local` access at import time.

**Reference:**

| SHA | Date | Note |
|---|---|---|
| `16ef2563` | 2026-02-02 | Introduces the bug (`refactor: use frappe's toogle_test_mode for enabling testing`) |
| `5118a99d` | 2026-02-01 | Last known-good — recommended downstream pin |
| `3c8b5ef8` | 2025-09-26 | Pre-test-mode-machinery (`refactor: rename to Buzz (#53)`) |

Workaround applied in [Erpflow-dev/alumni#4](https://github.com/Erpflow-dev/alumni/pull/4) — pin moved from `3d77434b` (2026-04-20, affected) to `5118a99d` (2026-02-01, last known-good).
