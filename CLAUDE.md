# CLAUDE.md — alumni

> Read on every Claude Code session. Update only via PR.

## What this app is

A standalone Frappe v16 app to run an alumni network for any school / college / institution. Two install modes:
- **School-Connected** — links to `frappe/education` + `erpnext` on the same bench.
- **Standalone** — runs on any Frappe site without those apps.

Same DocTypes, same UI in both modes. Mode-switching happens through an **Adapter Layer** (see `INTEGRATIONS.md`).

Events ride on top of [Buzz](https://github.com/BuildWithHussain/buzz). We don't reinvent ticket types, add-ons, or sponsorship — we extend Buzz Events with alumni-specific filters, member pricing, and links to Alumni Profiles.

**Spec v3 (Apr 2026)** added: private 1:1 messaging via Frappe socketio (ADR-031), document-based registration verification (ADR-032), full election system as first-class feature (ADR-033), donation categories + comments + guest donations (ADR-034), multi-site SaaS deployment pattern (ADR-035), 2FA / TOTP gating for admin/board (ADR-036), social login via Frappe OAuth (ADR-037), multilingual + RTL by default (ADR-038), email/phone verification (ADR-039), pluggable SMS/WhatsApp channels + segmented broadcast (ADR-040), custom domain + subdomain auto-provisioning with Let's Encrypt (ADR-041), PWA + offline + Web Push (ADR-042), Aurora dark theme + design system (ADR-043), profile completeness scoring + onboarding (ADR-044), Memorial Wall + Distinguished Alumni Awards (ADR-045), Perks marketplace + digital member card (ADR-046), Job Referrals + Speaker Bureau (ADR-047), networking match suggestions (ADR-048), SEO + Open Graph + QR codes (ADR-049), per-alumni vCard builder (ADR-050), per-alumni custom domain (ADR-051), WhatsApp Business integration (ADR-052), admin-managed template registry (ADR-053), and consolidated lessons from InfyVCardsSaas's 14-version history applied up-front (ADR-054).

**Required reading before frontend work:** `DESIGN_SYSTEM.md` (component vocabulary, motion, accessibility, RTL, performance budgets, white-labeling). The token system in `THEMES.md` is the *visual* contract; `DESIGN_SYSTEM.md` is the *interaction* contract. Both bind frontend tickets.

Read `DECISIONS.md` ADRs 031–049 before touching any of these areas.

## Stack

- **Frappe v16+ ONLY**. We use v16 features: UUID autoname, data masking, virtual DocTypes, type annotations, scheduler improvements. Code that targets v14/v15 is rejected in review.
- Python 3.11+
- Node 20 LTS, Yarn
- Vue 3 + Vite + Frappe UI for the logged-in portal
- Jinja for the public site
- Chart.js for analytics (no Insights dependency)
- Frappe Builder for public landing/pricing/about pages
- Buzz for event engine
- Frappe `payments` app for gateway abstraction
- License: AGPL-3.0

## The single most important rule

**Never `import` from another app outside the Adapter Layer.** Every cross-app call goes through `alumni/integrations/<adapter>.py`. The adapter has two implementations: `_real.py` (when the app is present) and `_fallback.py` (always). The selector in `__init__.py` decides which to use at runtime based on `frappe.get_installed_apps()` plus the user's choice in Alumni Settings.

CI rejects any PR that does `from erpnext.X` or `from education.X` or `from buzz.X` outside `integrations/`. Yes — even Buzz goes through the adapter, because we want to swap event engines later without rewriting the app.

```
alumni/integrations/
├── __init__.py            # adapter selector
├── education.py / education_real.py / education_fallback.py
├── receivables.py / receivables_real.py / receivables_fallback.py
├── events.py / events_real.py / events_fallback.py     # Buzz adapter (real-only)
├── storage.py / storage_real.py / storage_fallback.py
├── mail.py / mail_real.py / mail_fallback.py
├── analytics.py / analytics_real.py / analytics_fallback.py
├── live_class.py / live_class_real.py / live_class_fallback.py
├── certificates.py / certificates_real.py / certificates_fallback.py
├── communication.py / communication_real.py / communication_fallback.py  # EXPANDED v3 per ADR-040 — pluggable SMS/WhatsApp channels + broadcast (12 built-in providers + Custom HTTP)
├── messaging.py / messaging_real.py / messaging_fallback.py    # NEW v3 — fallback uses internal Message/Thread DocTypes; _real reserved for future Raven backend
└── verification.py / verification_fallback.py                  # NEW v3 — internal-only, no _real
```

## Hard rules

1. **No imports from other apps outside `alumni/integrations/`.** Enforced by `tests/test_no_cross_app_imports.py` (CI gate).
2. **Frappe v16 only.** Use type annotations, UUID autoname where suitable, data masking for PII fields per ADR-026.
3. **No required dependencies beyond `frappe`, `payments`, and `buzz`.** App must `bench install-app` cleanly on a vanilla Frappe v16 site with those three.
4. **Every adapter has both implementations.** `_real` and `_fallback`. `_fallback` is always functional.
5. **Standalone mode is the default mental model.** Design for standalone first; school-connected version is "additionally we read X from `tabStudent`".
6. **No Insights dependency.** Analytics live inside the app using Chart.js. If Insights is present, the analytics adapter shows an "Open in Insights" link.
7. **Never expose conduct or sensitive student data.** Even in school-connected mode, only academic snapshot fields are pulled, only with explicit field whitelist.
8. **Privacy filters apply at field level.** Use `permission_query_conditions` for rows, custom serializer for fields, plus v16 `data_masker` for PII.
9. **All money goes through the receivables adapter.** Never hardcode ERPNext doctype names in app code.
10. **No PII in logs.** Use `frappe.logger().info("alumni action", extra={"alumni": name})`.
11. **CSS uses tokens only.** Component CSS references `var(--color-X)`, never literal hex/rgb. Lints enforce.
12. **Every new DocType uses v16 type annotations.** Required: `def validate(self) -> None:`, `def before_save(self) -> None:`, etc.
13. **All user-facing strings wrapped in `_("…")`** for the multilingual + RTL build (per ADR-038). Vue strings via Frappe's translation hook. RTL layout selectors `[dir="rtl"]` only — no per-language CSS forks.
14. **Sensitive operations always log to Audit Log.** Including (v3 additions): `vote_cast`, `nomination_approved`, `nomination_rejected`, `message_reported`, `verification_decided`, `guest_donation_received`. Payload sanitized — never include voter ID, message body, or guest email in plaintext.
15. **Vote integrity is non-negotiable.** `Alumni Vote.voter` is redacted in every serializer except for System Manager. DB-level unique index on (election, position, voter). Never `frappe.get_all` votes — always `frappe.get_list`.
16. **Messaging stays on-server.** Never route messages through Pusher / Pubnub / external broker — Frappe socketio is the only realtime layer (per ADR-031). Attachments go through the storage adapter as **private** files.
17. **Guest data is not alumni data.** A guest donor's email never appears in the directory, alumni-facing exports, or anywhere a non-Admin can read. Guest comment widgets exclude the email field at the serializer level.
18. **All SMS / WhatsApp goes through the communication adapter** (per ADR-040). Never call Twilio (or any provider) directly from app code — register an `Alumni Communication Channel` and use `communication.send_sms` / `communication.send_whatsapp`. Bulk sends go through `Alumni Broadcast`, never ad-hoc loops over a recipient list. SMS / WhatsApp message bodies are NEVER stored in audit log payloads in plaintext — log a hash + the channel + recipient_count, not the body.
19. **Frontend work consults `DESIGN_SYSTEM.md`** before reaching for new patterns. Use documented components / states / motion tokens. New components must be added to Storybook with light + dark + LTR + RTL variants before merge.
20. **Memorial profiles are sacred.** Once `Alumni Profile.status = Deceased`, contact-data masking is permanent (no Admin override). Memorial maintainers can edit bio / photo only. Tribute submissions are always moderated. Audit-log every edit on a memorial page.
21. **Domain operations are System Manager only.** Adding / verifying / deleting an `Alumni Tenant Domain` requires System Manager role. Never expose domain DNS tokens or SSL keys in any API response — display them once on the domain detail page and store hashed for verification only.
22. **vCards never execute custom JavaScript.** Custom CSS allowed (sanitized via `bleach` allow-list); JS forbidden permanently. If a designer wants JS, they write a Frappe app extension instead. Per ADR-054 lesson #4.
23. **vCard templates are uploaded, not coded.** Outside of the 2 built-in vCard templates and 1 built-in WhatsApp Store template, every template is an admin-uploaded `.zip` package validated by `template_registry.install_from_zip`. Per ADR-053. Don't add a 3rd built-in template — make it an admin-uploadable example shipped in `/docs/templates/examples/` instead.
24. **AI adapter has strict PII minimization.** Never pass raw profile / message / vote / donation data to `ai.draft`. Use the per-purpose context allow-lists in `ai/contexts.py`. The `bio_context` allow-list is the canonical example — copy that pattern for new purposes. AI generation logs store only metadata (prompt hash, model, tokens, accepted/discarded flag) — never the prompt text or output text.
25. **vCard storage is quota-bounded.** Every upload checks the alumni's tier-based `vcard_storage_mb` allowance against current usage; over-quota uploads are rejected with a clear "upgrade tier or delete media" message. Per ADR-054 lesson #1.

## Naming

| Thing | Convention | Example |
|---|---|---|
| DocType | `Alumni X` | `Alumni Profile`, `Alumni Event Booking` |
| Module folder | snake_case | `alumni_event_booking/` |
| Python class | PascalCase, no prefix | `class AlumniEventBooking(Document)` |
| autoname | per SPEC.md §04 (UUID for opaque IDs, format strings for human-readable) | `ALU-{passing_year}-{####}` or UUID |
| API method | snake_case in `alumni/api.py` | `book_event(event, ticket_type, qty)` |
| Adapter public function | snake_case in `alumni/integrations/<x>.py` | `events.create_event(meta)` |
| Test file | `test_<feature>.py` in `tests/` | `test_payments.py` |
| Workflow JSON | `<doctype_lower>_workflow.json` in `workflow/` | `alumni_event_workflow.json` |
| Theme folder | snake_case | `alumni/themes/heritage/` |
| CSS token | `--color-X`, `--font-X`, `--space-X`, `--radius-X` | `--color-accent` |

## Forbidden patterns

- ❌ `from erpnext...`, `from education...`, `from insights...`, `from buzz...` outside `integrations/`
- ❌ `frappe.get_doc("Sales Invoice", ...)` outside `integrations/receivables_real.py`
- ❌ `frappe.get_doc("Student", ...)` outside `integrations/education_real.py`
- ❌ `frappe.get_doc("Buzz Event", ...)` outside `integrations/events_real.py`
- ❌ `frappe.get_all` when permissions matter — use `frappe.get_list`
- ❌ `frappe.db.sql("...")` with string interpolation — use parameterized queries
- ❌ `print()` for debugging — use `frappe.logger()`
- ❌ Synchronous gateway calls in request handlers — always enqueue
- ❌ Storing money as Float — use `Currency`
- ❌ Storing dates as strings — use `Date` / `Datetime`
- ❌ Hardcoded currency/locale/country — read from `Alumni Settings`
- ❌ Literal hex/rgb in component CSS — use theme tokens
- ❌ Code targeting Frappe v14 or v15 — v16 only
- ❌ Importing in Server Scripts — Server Scripts block imports; use `frappe.utils.X` directly
- ❌ External realtime brokers (Pusher / Pubnub / Ably) for messaging — `frappe.publish_realtime` only
- ❌ Hardcoded language strings — wrap in `_()` (Python) or `__()` (Vue) so translations work
- ❌ Reading `Alumni Vote.voter` outside System Manager scope — redacted serializer is the only path
- ❌ Storing OTP / 2FA secrets in DB tables — Frappe core handles TOTP; OTPs go in `frappe.cache()`
- ❌ Including guest donor email in any non-Admin response shape
- ❌ Direct provider imports (`from twilio...`, `import vonage`, `from africastalking...`) anywhere outside `communication_real/drivers/<provider>.py` — register an Alumni Communication Channel instead
- ❌ Looping over alumni and calling `send_sms` directly for a campaign — use `Alumni Broadcast` so it's queued, rate-limited, audited, and retried
- ❌ Hardcoded hex / rgb colors in components — use design tokens; even the new dark mode (Aurora) uses the same tokens
- ❌ Custom motion durations or easings — use `--motion-fast/base/slow` from the design system
- ❌ Direct provider SDK imports in app code (e.g., `from twilio.rest import Client`, `from sendgrid...`) — providers live in `communication_real/drivers/<provider>.py`
- ❌ Image `<img>` without `alt` attribute — required even for decorative images (use `alt=""`)
- ❌ Bypassing the QR utility — always use `alumni.utils.qr.generate(url)` so codes are signed and consistent
- ❌ Reading `Alumni Tenant Domain.dns_token` or `ssl_custom_key` outside of System Manager scope
- ❌ JavaScript in any vCard customization field — sanitizer rejects it; don't try to allow-list it for "trusted" alumni
- ❌ Hardcoded vCard / WhatsApp Store templates in app code beyond the 2+1 built-in — make new templates admin-uploadable per ADR-053
- ❌ Passing raw `Alumni Profile` / message / vote / donation data to `ai.draft` — use the per-purpose context allow-list in `ai/contexts.py`
- ❌ Storing AI-generated text in audit logs or in `Alumni AI Generation Log` — only metadata (prompt hash, tokens, etc.) is permitted
- ❌ Skipping the storage-quota check on vCard image uploads — even for "premium" tiers, the check runs (the limit is just higher)

## Adding an integration touchpoint

1. Define the public function signature in `alumni/integrations/<area>.py`.
2. Implement `_real.py` (target app installed) and `_fallback.py` (always).
3. Update the selector in `alumni/integrations/__init__.py`.
4. Add tests in `tests/integrations/test_<area>.py` covering both implementations.
5. Document in `INTEGRATIONS.md`.

## Adding a DocType

1. Scaffold with `bench new-doctype` or by hand.
2. Fields per SPEC.md §04. Use v16 `autoname: "uuid"` if no human-readable ID is needed.
3. Permissions per SPEC.md §06.
4. Controller in `<doctype>.py` with **type-annotated** `validate`, `before_save`, `on_submit`.
5. Test for create / read / update / permission denial.
6. If part of a workflow, add the workflow fixture and reference in `hooks.py`.
7. `bench migrate` and run tests.

## Adding an API endpoint

- Whitelist in `alumni/api.py` with `@frappe.whitelist()`.
- Guest endpoints use `@frappe.whitelist(allow_guest=True)` and explicit no-PII checks.
- Validate inputs with `frappe.utils.validate_email_address` etc.
- Wrap writes in `frappe.db.savepoint`.
- Return dicts, not Document objects.
- Add a test in `tests/test_api.py`.

## Adding a theme

See `THEMES.md`. In short: drop a folder under `alumni/themes/<id>/` with `theme.json`, `tokens.css`, `preview.png`. Validator runs at install. No code changes elsewhere.

## Cross-mode testing

Every payment / membership / event / donation feature has tests for **both** modes:

```python
# tests/test_payments.py
import pytest

@pytest.mark.parametrize("mode", ["school_connected", "standalone"])
def test_membership_purchase_flow(mode: str) -> None:
    set_mode(mode)
    ...
```

CI runs the suite twice — once with school-connected dependencies present, once on a vanilla site. Both must pass.

## OpenAEC Frappe Skill Package

The team has the **OpenAEC Frappe Claude Skill Package** installed at `~/.claude/skills/`. 61 deterministic skills covering ~95% of Frappe v14-v16. Claude reads them automatically when generating Frappe code.

If you don't have it: see `CLAUDE_CODE_SETUP.md`.

When in doubt about a Frappe pattern, the skill package is the source of truth. Defer to it.

## Definition of done

- [ ] Lints pass (`ruff`, `eslint`)
- [ ] Tests pass on **both** modes
- [ ] Coverage ≥ 80% on changed files
- [ ] Type annotations on every new function
- [ ] No new cross-app imports outside `integrations/`
- [ ] No literal hex in component CSS
- [ ] Adapter contract (`INTEGRATIONS.md`) updated if needed
- [ ] CHANGELOG.md updated
- [ ] If a DocType changed, migration is idempotent (run twice on staging)
