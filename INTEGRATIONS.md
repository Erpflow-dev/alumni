# INTEGRATIONS.md — adapter contracts

The Adapter Layer is what makes this app work in both **School-Connected** and **Standalone** mode. Every cross-app touchpoint is a single function with two implementations.

> **Rule:** App code imports from `alumni.integrations.<area>`. Never from `alumni.integrations.<area>_real` or `_fallback` directly. Never from any other Frappe app outside `integrations/`. Even Buzz goes through the adapter so we can swap event engines later.

---

## §0 Selector contract

The selector decides `_real` vs `_fallback` for each adapter at call time. Three behaviours are non-negotiable:

1. **App-presence is the default discriminator.** For most adapters, `_real` is selected when its target Frappe app is installed (`frappe.get_installed_apps()`); otherwise `_fallback` is used.
2. **The AI adapter is special.** AI provider selection is **not** driven by app presence — it's driven by `Alumni Settings.ai_provider` (None / OpenAI / Anthropic / Bedrock / Custom HTTP) plus the `ai_enabled` master toggle. The selector special-cases `area == "ai"` *before* the app-presence check.
3. **Defensive default during install / migrate.** Adapters get called during `bench install-app` and `bench migrate` (storage especially, for fixture import). At that moment `Alumni Settings` does not yet exist. The selector MUST swallow `frappe.DoesNotExistError` and return `"fallback"` — it must never raise. Every `_fallback` is therefore also expected to be safe to call against an empty / pre-Settings site.

```python
# alumni/integrations/__init__.py
from __future__ import annotations
import frappe

def _mode_for(area: str) -> str:
    """Return 'real' or 'fallback' for a given integration area.

    Defensive default: if Alumni Settings does not yet exist (during
    install / migrate / pre-wizard), every adapter falls back to '_fallback'
    rather than raising — adapters used during install (notably storage)
    must remain callable.
    """
    # Defensive: Settings may not exist during install / migrate
    try:
        settings = frappe.get_cached_doc("Alumni Settings")
    except frappe.DoesNotExistError:
        return "fallback"

    # AI adapter is special: provider is chosen via Alumni Settings.ai_provider,
    # NOT via frappe.get_installed_apps(). Returns 'real' iff a provider is
    # configured AND ai_enabled = 1.
    if area == "ai":
        if (
            getattr(settings, "ai_enabled", 0)
            and getattr(settings, "ai_provider", None) not in (None, "", "None")
        ):
            return "real"
        return "fallback"

    if settings.mode == "standalone":
        # Standalone mode: only events use real (Buzz is always required), rest fallback
        if area == "events":
            return "real"
        return "fallback"

    installed = frappe.get_installed_apps()
    requirements = {
        "education":   "education",
        "receivables": "erpnext",
        "events":      "buzz",        # always required, both modes
        "storage":     "drive",
        "mail":        "mail",
        "analytics":   "insights",
        "live_class":  "school_live_class",
        "certificates": "school_certificates",
        "communication": "school_communication",
        "messaging":   "raven",       # NEW v3 — optional Raven chat backend; falls back to in-app
        "verification": None,         # NEW v3 — always uses fallback (Frappe core); no real impl
        # 'ai' handled above — not app-presence-driven
    }
    real = requirements.get(area)
    if real is None:
        return "fallback"
    return "real" if real in installed else "fallback"


def _impl(area: str):
    mode = _mode_for(area)
    module = f"alumni.integrations.{area}_{mode}"
    return frappe.get_module(module)
```

Each public surface module (`education.py`, `events.py`, etc.) exposes a stable function set, dispatching to `_impl(area)`.

---

## 1. Education adapter — `alumni.integrations.education`

```python
def list_graduating_students(passing_year: int) -> list[dict]: ...
def get_student(student_id: str) -> dict | None: ...
def list_past_students(filters: dict | None = None) -> list[dict]: ...
def get_department(name: str) -> dict | None: ...
def is_school_connected() -> bool: ...
```

**Real:** reads `tabStudent`, `tabGuardian`, `tabEducation Department`. Read-only.
**Fallback:** uses internal `Past Student` and `Alumni Department` stubs.

---

## 2. Receivables adapter — `alumni.integrations.receivables`

```python
def ensure_customer(alumni: str) -> str: ...
def ensure_item(item_code: str, item_name: str, group: str) -> str: ...
def create_invoice(
    customer: str,
    items: list[dict],
    currency: str,
    due_date: str,
    metadata: dict,
) -> dict: ...
def record_payment(
    invoice_id: str,
    amount: float,
    currency: str,
    gateway: str,
    gateway_txn_id: str,
    paid_at: str,
) -> dict: ...
def refund_payment(payment_id: str, amount: float, reason: str) -> dict: ...
def get_invoice(invoice_id: str) -> dict: ...
def list_invoices_for_alumni(alumni: str) -> list[dict]: ...
```

**Real:** ERPNext Customer / Item / Sales Invoice / Payment Entry flow.
**Fallback:** `Alumni Invoice` + `Alumni Payment` DocTypes (lightweight).

### Alumni Invoice (fallback only)
| Field | Type |
|---|---|
| name | autoname `INV-{YYYY}-{######}` |
| alumni | Link → Alumni Profile |
| items | Table → Alumni Invoice Item (item_code, item_name, qty, rate, amount) |
| total_amount | Currency |
| currency | Link → Currency |
| due_date | Date |
| source_doctype | Data |
| source_name | Data |
| status | Select: Draft / Sent / Paid / Cancelled / Refunded |
| payment_url | Data |

### Alumni Payment (fallback only)
| Field | Type |
|---|---|
| name | autoname `PMT-{YYYY}-{######}` |
| invoice | Link → Alumni Invoice |
| alumni | Link → Alumni Profile |
| amount | Currency |
| currency | Link → Currency |
| gateway | Data |
| gateway_txn_id | Data unique |
| paid_at | Datetime |
| status | Select: Completed / Refunded / Failed |

---

## 3. Events adapter — `alumni.integrations.events` (Buzz wrapper)

This is the new star adapter. We ride on Buzz for everything ticketing, but expose only the surface our app needs.

```python
def create_event(meta: dict) -> str:
    """meta = {title, description, start_at, end_at, venue, online_link, ...}
    Returns Buzz Event name. Caller separately creates Alumni Event Wrapper
    pointing to it."""

def update_event(buzz_event: str, meta: dict) -> None: ...

def publish_event(buzz_event: str) -> None: ...

def list_ticket_types(buzz_event: str) -> list[dict]: ...
def add_ticket_type(buzz_event: str, tier: dict) -> str: ...
def update_ticket_type(ticket_type_id: str, tier: dict) -> None: ...

def list_add_ons(buzz_event: str) -> list[dict]: ...
def add_add_on(buzz_event: str, add_on: dict) -> str: ...

def list_sponsorship_tiers(buzz_event: str) -> list[dict]: ...
def add_sponsorship_tier(buzz_event: str, tier: dict) -> str: ...

def book(buzz_event: str, alumni_email: str, ticket_type: str,
         qty: int, add_ons: list[dict] | None = None,
         coupon: str | None = None) -> dict:
    """Returns {booking_id, payment_url, total_amount}.
    Forwards to Buzz's booking API which uses frappe/payments."""

def get_booking(booking_id: str) -> dict: ...
def list_bookings_for_alumni(alumni_email: str) -> list[dict]: ...

def cancel_booking(booking_id: str, reason: str) -> dict: ...
def transfer_ticket(booking_id: str, new_attendee_email: str) -> dict: ...

def scan_ticket(qr_token: str) -> dict:
    """Mark ticket as Used. Returns booking detail for check-in display."""
```

**Real implementation** (the only one — Buzz is required in both modes):
```python
# events_real.py
import frappe

def create_event(meta: dict) -> str:
    doc = frappe.get_doc({
        "doctype": "Buzz Event",
        "title": meta["title"],
        "description": meta.get("description"),
        "start_at": meta["start_at"],
        "end_at": meta["end_at"],
        "venue": meta.get("venue"),
        "online_link": meta.get("online_link"),
        "payment_gateway": frappe.db.get_single_value(
            "Alumni Settings", "payment_gateway"
        ),
    })
    doc.insert()
    return doc.name
```

(There is no `events_fallback.py` for now — Buzz is a required dep. We could write one later if a deployment really wanted to skip Buzz, but it's a deliberate non-goal.)

### Alumni Event Wrapper (our DocType, 1:1 with Buzz Event)

| Field | Type | Notes |
|---|---|---|
| `name` autoname | `EVT-{YYYY}-{####}` | |
| `buzz_event` | Link → Buzz Event | unique, required, 1:1 mapping |
| `visibility` | Select | Public / Alumni-only / Members-only |
| `chapter` | Link → Alumni Chapter | optional |
| `member_pricing_enabled` | Check | enables alumni-only ticket prices |
| `passing_year_filter_min` / `_max` | Int | restrict who can book |
| `organizer_alumni` | Link → Alumni Profile | |
| `moderator_approved` | Check | workflow gate |
| `featured` | Check | shows on landing |

When a user creates an Alumni Event in our UI:
1. Our controller calls `events.create_event(...)` → Buzz Event created.
2. Our wrapper saves with `buzz_event` linked.
3. Booking buttons on our event page point to Buzz's booking page, with our wrapper enforcing visibility filters via `permission_query_conditions`.

---

## 4. Storage adapter — `alumni.integrations.storage`

```python
def upload(content: bytes, filename: str, folder: str, public: bool = False) -> str: ...
def get_url(file_id: str) -> str: ...
def delete(file_id: str) -> None: ...
def list_folder(folder: str) -> list[dict]: ...
```

**Real:** Frappe Drive folders.
**Fallback:** `tabFile` with virtual prefix paths.

Folders used: `/alumni/profile-photos`, `/alumni/event-covers`, `/alumni/cvs`, `/alumni/receipts`, `/alumni/membership-cards`, `/alumni/story-images`.

---

## 5. Mail adapter — `alumni.integrations.mail`

```python
def send_transactional(
    template: str,
    recipients: list[str],
    context: dict,
    attachments: list[dict] | None = None,
    delayed: bool = True,
) -> str: ...

def send_bulk(newsletter_name: str) -> dict: ...
def list_bounces(since: "datetime") -> list[dict]: ...
```

**Real:** Frappe Mail with bounce/click tracking.
**Fallback:** `frappe.sendmail` with rate-limit + Email Queue.

---

## 6. Analytics adapter — `alumni.integrations.analytics`

```python
def render_chart(chart_id: str, filters: dict) -> dict:
    """Returns {labels: [...], datasets: [...]} for Chart.js."""
def list_dashboards() -> list[dict]: ...
def export_dataset(dataset: str, filters: dict, format: str) -> bytes: ...
```

**Real:** in-app SQL queries + an `open_in_insights_url` link if Insights present.
**Fallback:** in-app SQL only. Charts always render with Chart.js client-side.

---

## 7. Live Class adapter — `alumni.integrations.live_class`

```python
def create_room(
    title: str,
    starts_at: "datetime",
    duration_minutes: int,
    host_email: str,
    metadata: dict,
) -> dict:
    """Returns {room_id, join_url, host_url, recordable: bool}."""

def get_room(room_id: str) -> dict | None: ...
def end_room(room_id: str) -> None: ...
```

**Real:** `school_live_class.api.create_room`.
**Fallback:** public `https://meet.jit.si/<random>` (recordable=false).

---

## 8. Certificates adapter — `alumni.integrations.certificates`

```python
def render(template: str, context: dict, output_format: str = "pdf") -> bytes: ...
```

**Real:** `school_certificates.api.render`.
**Fallback:** WeasyPrint with built-in templates (membership_card, event_ticket, donation_receipt, committee_certificate).

---

## 9. Communication adapter — `alumni.integrations.communication` *(EXPANDED v3, per ADR-040)*

The communication adapter handles all outbound non-email messaging: push notifications, transactional SMS (OTPs, payment receipts), WhatsApp, and bulk broadcasts. v3 makes the SMS / WhatsApp providers pluggable via `Alumni Communication Channel` records — admins register any number of provider configurations, each with its own credentials, country routing, and quota.

### Public surface

```python
# Push (mobile / web push notification)
def push(user: str, title: str, body: str, deeplink: str | None = None) -> None: ...

# Transactional SMS — single recipient, fast path
def send_sms(to: str, body: str,
             channel: str | None = None) -> dict:
    """Sends an SMS. If channel is None, picks per ADR-040 routing precedence:
       (1) explicit channel → (2) recipient country → (3) is_default → (4) first active.
       Returns {provider_message_id, channel_used, status}."""

# Transactional WhatsApp — single recipient
def send_whatsapp(to: str, body: str,
                  template_name: str | None = None,
                  template_variables: dict | None = None,
                  channel: str | None = None) -> dict:
    """If recipient has not messaged within 24h, template_name is required (WhatsApp
       Business policy). Returns {provider_message_id, channel_used, status}."""

# Bulk broadcast — async, queued
def queue_broadcast(broadcast_name: str) -> None:
    """Reads Alumni Broadcast doc, resolves the segment, enqueues per-recipient sends
       respecting messaging_preference, phone_verified, country filter, and the
       broadcast_max_recipients_per_minute rate limit. Writes one Alumni Broadcast Log
       Entry row per recipient."""

# Webhook entry point (provider delivery receipts)
def handle_delivery_receipt(channel: str, payload: dict) -> None:
    """Updates the matching Alumni Broadcast Log Entry by provider_message_id."""

# Segment resolver — used by queue_broadcast and broadcast preview
def resolve_segment(segment_type: str, segment_filter: dict,
                    extra: dict | None = None) -> list[str]:
    """Returns list of Alumni Profile names for the given segment.
       segment_type ∈ {'all_active', 'chapter', 'reunion_group', 'committee',
                       'class', 'department', 'membership_tier', 'custom_list',
                       'election_eligible'}."""
```

### Channel routing

The adapter selects a channel for any send according to this precedence:

1. **Explicit `channel` argument** — caller passed a specific Alumni Communication Channel name
2. **Country match** — if recipient's phone country code maps to an active channel's `default_for_country`, use that
3. **Default for medium** — `Alumni Settings.default_sms_channel` or `default_whatsapp_channel`
4. **First active** — first active channel of the right `channel_type`
5. **Error** — no eligible channel; transactional sends raise; broadcast log entries marked Failed with skip_reason

For OTPs and other one-shots where reliability matters more than cost, callers can pass `channel=Alumni Settings.transactional_sms_channel` explicitly.

### Built-in providers (in `_real`)

The `communication_real.py` module ships with drivers for: **Twilio**, **Twilio WhatsApp**, **MessageBird**, **Vonage**, **Plivo**, **Africa's Talking**, **Wati**, **Gupshup**, **360Dialog**, **Unifonic**, **MSG91**, and **SSL Wireless**. Each driver is ~80 lines and handles auth + send + delivery-receipt parsing.

The **Custom HTTP** driver lets institutions wire any provider exposing a JSON HTTP API by configuring the channel record with `http_url`, `http_method`, `http_auth_header`, `http_payload_template` (Jinja, with `{{to}}`, `{{body}}`, `{{from_address}}` available), and `http_response_id_path` (JSON path to extract the provider message ID). No Python required — pasting the provider's curl example into the four fields is enough.

### Fallback behavior

When no Alumni Communication Channel record is configured, `_fallback`:
- `push` writes a Frappe Notification Log entry only
- `send_sms` and `send_whatsapp` raise `CommunicationChannelNotConfigured` for transactional sends; for broadcast sends, the recipient log entry is marked Skipped with reason "no channel configured"
- `queue_broadcast` still runs, reports recipients_count, but every entry is Skipped — admin sees the failure clearly in the Broadcast detail view and can configure a channel and click Resend

### Real (school_communication) override

When the institution has its own central communication app (`school_communication`), the events `push` and `send_sms` can be aliased to its `notify` API via `Alumni Settings.communication_app = "school_communication"`. The channel system still applies for everything else.

### Security & audit

Every `send_sms` / `send_whatsapp` (transactional) writes to `Alumni Audit Log` with `event_type="sms_sent"` / `"whatsapp_sent"` and a hashed body — never the plaintext message — plus the channel used. Every Broadcast submit writes one summary audit entry; per-recipient details live in the Broadcast Log Entry table. Channel `auth_credentials` is stored as Frappe `Password` (encrypted at rest, decrypted only inside the driver).

### Rate limiting

- Transactional sends: 5/min per recipient (per Frappe cache, sliding window)
- Broadcast sends: `broadcast_max_recipients_per_minute` (Settings default 60), enforced by the queue worker
- Per-channel: respect `daily_quota` — when reached, channel is auto-deactivated for the day with a warning email to Admin

---

## 10. Messaging adapter — `alumni.integrations.messaging` *(NEW v3)*

Wraps how messages are persisted and delivered. The default fallback uses our own DocTypes (`Alumni Message Thread` / `Alumni Message`) plus Frappe's socketio for realtime; an optional real adapter can route through a dedicated chat app (e.g. [Raven](https://github.com/The-Commit-Company/raven)) when present.

```python
def open_thread(participant_a: str, participant_b: str) -> str:
    """Returns thread id. Idempotent — same pair always yields same thread."""

def send_message(thread_id: str, sender: str,
                 body: str, attachments: list[str] | None = None) -> str:
    """Returns message id. Publishes realtime to recipient's user channel."""

def list_threads_for(alumni: str, page: int = 0, page_size: int = 20) -> list[dict]: ...

def list_messages_in(thread_id: str, before: str | None = None,
                     limit: int = 50) -> list[dict]: ...

def mark_read(thread_id: str, reader: str) -> None: ...

def block(blocker: str, blocked: str) -> None: ...

def unblock(blocker: str, blocked: str) -> None: ...

def report(thread_id: str, reporter: str, reason: str) -> None:
    """Logs to Alumni Audit Log; flags thread for Moderator review."""

def delete_message(message_id: str, requester: str) -> None:
    """Soft-delete; keeps audit trail."""
```

**Real (Raven):** delegates persistence to Raven's channel/message DocTypes; we keep a thin `Alumni Message Thread` linker for permission filtering.
**Fallback (default):** uses our `Alumni Message Thread` + `Alumni Message` DocTypes and `frappe.publish_realtime`. Attachments stored via the storage adapter as **private** files. Per ADR-031, this is the only one most deployments will use.

---

## 11. Verification adapter — `alumni.integrations.verification` *(NEW v3)*

Wraps email verification (always-on by default) and phone OTP verification (opt-in). There is no `_real` — Frappe core provides the building blocks (signed tokens, email queue, optional SMS gateway), so the fallback is always used.

```python
def issue_email_verification_token(email: str, ttl_seconds: int = 86400) -> str:
    """Returns the token; sends the verification email via mail adapter."""

def consume_email_verification_token(token: str) -> dict:
    """Returns {email: str, valid: bool, reason: str | None}.
    Single-use; expired/replayed tokens return valid=False."""

def issue_phone_otp(phone: str, ttl_seconds: int = 600) -> str:
    """Returns the otp; sends via communication.sms()."""

def verify_phone_otp(phone: str, otp: str) -> bool:
    """Single-use; rate-limited to 5 attempts per hour per phone."""

def review_documents(profile: str) -> dict:
    """Returns aggregate verification state for a profile —
    {accepted_count, pending_count, rejected_count, status: str}."""

def is_profile_verified(profile: str) -> bool:
    """True iff email_verified AND verification_status == 'Verified'
    AND (phone_verified OR not require_phone_verification)."""
```

**Why an adapter?** It centralizes the "is this person verified" question so DocType controllers, permission rules, and the API layer all ask the same way. Future move to a third-party identity provider (Auth0, Clerk) becomes a one-file swap.

---

## 12. AI adapter — `alumni.integrations.ai` *(NEW v3, per ADR-054 lesson #10)*

Optional adapter that drafts text content (bios, descriptions, citations) for human review. Disabled by default; institutions opt in via `Alumni Settings.ai_enabled = 1` and configure a provider.

### Public surface

```python
# Draft a piece of content
def draft(purpose: str, context: dict, max_tokens: int = 600) -> dict:
    """purpose ∈ {'bio_draft', 'section_description', 'story_draft',
                   'campaign_description', 'news_article', 'citation'}.
       context: minimized data (no email/phone/other-alumni PII).
       Returns {text, model_used, input_tokens, output_tokens, latency_ms,
                generation_log_id} so the caller can stream to UI and
                later mark accepted/discarded."""

# Mark an AI generation accepted (the user kept the result)
def mark_accepted(generation_log_id: str) -> None: ...

# Mark a generation discarded (regenerate or close composer)
def mark_discarded(generation_log_id: str) -> None: ...

# Quota check before an expensive call — caller can pre-check
def remaining_tokens_for(alumni: str) -> int: ...
```

### Real implementations

`ai_real.py` ships with drivers for **OpenAI**, **Anthropic** (Claude), **Bedrock** (Anthropic, Llama, Mistral), and **Custom HTTP** (any JSON-API LLM).

Selection: `Alumni Settings.ai_provider` chooses the driver. `ai_credentials` is encrypted (Frappe Password). `ai_model_default` is provider-specific.

### Fallback

`ai_fallback.py` returns `NotImplementedError("AI not enabled")` for `draft`. Composer UI hides the "Help me write" button when `ai_enabled=0` so callers should never reach the fallback in practice.

### Privacy & abuse controls

- **PII minimization:** the `context` dict passed to `draft` is rendered through a strict allow-list per `purpose`. For `bio_draft`, only `{name, passing_year, current_role, current_city, interests, skills}` go to the model. Email, phone, address, vote history, message contents, donation history NEVER cross the boundary.
- **Prompt hashing:** the rendered prompt is hashed (SHA-256) and stored in `Alumni AI Generation Log.prompt_hash`. The prompt text itself is not stored.
- **Output not stored:** `draft` returns the text to the caller; the caller streams it to the UI; if the user discards, nothing about the output is retained beyond the metadata log entry.
- **Per-alumni token quota:** `Alumni Settings.ai_max_monthly_tokens_per_alumni` caps monthly usage per alumni. Checked before the call; remaining tokens shown in the UI.
- **Auto-purge:** generation logs older than `Alumni Settings.ai_data_retention_days` (default 90) are deleted by `tasks.purge_ai_generation_logs()` daily.
- **Audit:** every call writes one Alumni AI Generation Log row with `requested_by`, `target_doctype`, `target_name`, `purpose`, `model_provider`, `model_id`, token counts, latency, and `accepted_by_user` (filled later by `mark_accepted` / `mark_discarded`).

### When NOT to use AI

The communication adapter does not call `ai.draft` for SMS / WhatsApp message bodies (admin writes those manually for a reason — accountability). Voting, election, and verification flows never invoke AI. Donation receipts, tax receipts, and audit log entries are template-rendered, never AI-generated.

---

## CI guard

`tests/test_no_cross_app_imports.py` walks the source tree and fails any PR that imports from another Frappe app outside `alumni/integrations/`:

```python
import ast
import os

FORBIDDEN_PREFIXES = [
    "erpnext", "education", "insights", "lms", "hrms",
    "drive", "mail", "crm", "helpdesk", "buzz", "school_",
    "raven",  # reserved for future messaging_real backend (per INTEGRATIONS.md §10)
]

def _python_files(root: str):
    for dirpath, _, filenames in os.walk(root):
        for fn in filenames:
            if fn.endswith(".py"):
                yield os.path.join(dirpath, fn)

def test_no_cross_app_imports():
    for path in _python_files("alumni/"):
        if "/integrations/" in path:
            continue
        if "/tests/" in path:
            continue
        with open(path) as f:
            source = f.read()
        tree = ast.parse(source, filename=path)
        for node in ast.walk(tree):
            modules: list[str] = []
            if isinstance(node, ast.Import):
                modules = [n.name for n in node.names]
            elif isinstance(node, ast.ImportFrom) and node.module:
                modules = [node.module]
            for module in modules:
                for prefix in FORBIDDEN_PREFIXES:
                    assert not module.startswith(prefix + ".") and module != prefix, (
                        f"{path}: forbidden import '{module}' outside integrations/"
                    )
```

This is what makes the standalone promise real.

---

## Changing an adapter

1. Update the public function signature in `alumni/integrations/<area>.py`.
2. Update both `<area>_real.py` and `<area>_fallback.py` (or just real if no fallback).
3. Add tests in `tests/integrations/test_<area>.py` covering both.
4. Update this document.
5. Bump the adapter version comment at the top of `<area>.py`.
