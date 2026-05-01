# Project context — alumni

> Auto-loaded by Claude Code on session start. Companion to `CLAUDE.md` (root rules).
> Last refreshed: 2026-04-29, after the pre-T-001 spec hygiene sweep.

## What this is, in one paragraph

`alumni` is a standalone Frappe v16 app that runs an alumni network for any school / college / institution. AGPL-3.0. Two install modes selected at first-run wizard, switchable later in `Alumni Settings`: **school_connected** (links to `frappe/education` + `erpnext` on the same bench) and **standalone** (vanilla Frappe site, internal stubs for everything). Required external apps in both modes: `frappe>=16`, `payments`, `buzz`. Same DocTypes and same UI in both modes — mode behaviour swaps via the Adapter Layer.

## Versions (pin everything)

- **Frappe v16+ ONLY.** Never generate code targeting v14 or v15. Use type annotations on every controller method, `autoname: "uuid"` for opaque IDs (audit, polymorphic, votes), `frappe.utils.data_masker` for PII, virtual DocTypes for read-only views over external data, the improved scheduler with proper `cron` events.
- Python 3.11+
- Node 20 LTS, Yarn
- Vue 3 + Vite + Frappe UI (logged-in SPA)
- Jinja (public site)
- Chart.js (analytics — no Insights dependency)
- Frappe Builder (marketing pages: home / pricing / about / FAQ landing)

## Skill package

The OpenAEC Frappe Skill Package is installed at `~/.claude/skills/`. 61 deterministic skills covering doctype creation, controllers, hooks, permissions, REST API, migrations, fixtures, scheduler, jinja, print formats, testing, deployment. **Defer to the skill if it exists** — the skills are read automatically when generating Frappe code.

---

## Architectural rules — NEVER violate

These are the inviolables. CI gates exist for most. Each cites where the rule is canonically documented.

### 1. Adapter Layer rule (ADR-001 / ADR-002, CLAUDE.md hard rule #1)

**Never `import` from another Frappe app outside `alumni/integrations/`.** Every cross-app touch goes through `alumni.integrations.<area>` (the public surface), which dispatches to `<area>_real.py` or `<area>_fallback.py` via the selector in `alumni/integrations/__init__.py`. **Even Buzz** goes through the adapter — we want to swap event engines later without rewriting app code.

- **Forbidden imports anywhere outside `integrations/`:** `erpnext`, `education`, `buzz`, `raven`, `insights`, `drive`, `mail`, `school_*`, `lms`, `hrms`, `crm`, `helpdesk`.
- **Forbidden DocType reads anywhere outside the matching `_real.py`:** `frappe.get_doc("Sales Invoice", …)` (receivables_real), `frappe.get_doc("Student", …)` (education_real), `frappe.get_doc("Buzz Event", …)` (events_real).
- **Enforcement:** `alumni/tests/test_no_cross_app_imports.py` (T-003) — AST walks every `.py` file, fails CI on a forbidden prefix outside `integrations/`. The `FORBIDDEN_PREFIXES` list lives in `INTEGRATIONS.md` § CI guard and includes `raven` (per spec hygiene).
- **12 adapters total:** education, receivables, events (real-only), storage, mail, analytics, live_class, certificates, communication, messaging, verification (fallback-only — no `_real`), ai. AI is special — see selector contract below.

### 2. No direct provider SDK imports (CLAUDE.md hard rule #18, ADR-040)

**Never import a provider SDK from app code.** `from twilio…`, `import vonage`, `from africastalking…`, `from sendgrid…`, etc. — all forbidden anywhere outside `communication_real/drivers/<provider>.py`. Register an `Alumni Communication Channel` and use `communication.send_sms` / `communication.send_whatsapp` instead. Bulk sends go through `Alumni Broadcast`, never ad-hoc loops over a recipient list.

- 12 built-in providers: Twilio, Twilio WhatsApp, MessageBird, Vonage, Plivo, Africa's Talking, Wati, Gupshup, 360Dialog, Unifonic, MSG91, SSL Wireless. Plus a Custom HTTP driver for any JSON-API gateway.
- **SMS / WhatsApp message bodies are NEVER stored in audit log payloads in plaintext** — log a hash + channel + recipient_count.

### 3. Vote integrity — `Alumni Vote.voter` redaction (CLAUDE.md hard rule #15, ADR-033)

**The `voter` field is redacted in every serializer except for System Manager.** DB-level unique index on `(election, position, voter)`. **Never `frappe.get_all` votes — always `frappe.get_list`** so permission filters apply. Every read of vote data writes to `Alumni Audit Log` with `event_type = vote_record_read`.

- Vote name is UUID autoname (opaque) so the voter cannot be reverse-engineered from the record name.
- One-vote-per-position-per-voter enforced at the DB level, not just in the controller — the unique index is the last line of defence.
- The seven canonical attack scenarios are covered by T-085's election integrity test suite.

### 4. Custom JavaScript forbidden in vCards, permanently (CLAUDE.md hard rule #22, ADR-054 lesson #4)

**No JS in any vCard customization field, ever.** Custom CSS allowed (sanitized via `bleach` allow-list — no `@import`, no `url(http…)` external, no `expression()`, no JavaScript URLs). The sanitizer rejects JS. Don't try to allow-list it for "trusted" alumni. If a designer needs JS, they write a Frappe app extension instead.

- Same rule for vCard templates: `template_registry.install_from_zip` (T-105) rejects any `.js` file in the upload pipeline.
- This is the lesson InfyVCardsSaas re-learned across multiple releases — we ship the rule on day 1.

### 5. Guest donor email is not alumni data (CLAUDE.md hard rule #17, ADR-034)

**A guest donor's email never appears in the directory, alumni-facing exports, or anywhere a non-Admin can read.** Guest comment widgets exclude the email field at the serializer level. The tax receipt goes to that email; the address never re-enters the alumni network.

- Public endpoint: `donate_as_guest(campaign, name, email, amount, …)` is `@frappe.whitelist(allow_guest=True)`. Per-IP rate limit + email format validation + honeypot before record creation.
- `Alumni Donation.is_guest=1` flips the receipt template branch and the privacy filters.
- Audit log entry uses `guest_donation_received` event type with sanitized payload (no plaintext email).

### Other inviolables — also CI- or reviewer-enforced

- **Memorial profiles are sacred** (rule #20 / ADR-045) — once `Alumni Profile.status = Deceased`, contact-data masking is permanent. No Admin override. Memorial maintainers can edit bio / photo only.
- **Domain operations are System Manager only** (rule #21 / ADR-041) — `Alumni Tenant Domain.dns_token` and `ssl_custom_key` never appear in any API response.
- **AI adapter PII minimization** (rule #24 / ADR-054 lesson #10) — never pass raw profile / message / vote / donation data to `ai.draft`. Use the per-purpose allow-lists in `alumni/integrations/ai/contexts.py`. AI generation logs store only metadata (prompt hash, model, tokens, accepted flag) — never the prompt text or output text.
- **Messaging stays on-server** (rule #16 / ADR-031) — Frappe socketio only via `frappe.publish_realtime`. Never Pusher / Pubnub / Ably / external broker.
- **CSS uses tokens only** (rule #11 / ADR-027) — never literal hex/rgb in component CSS. CI lint enforces.
- **All money is `Currency`** — never `Float`.
- **No `print()` for debugging** — `frappe.logger().info("…", extra={"alumni": name})` with structured fields. **No PII in logs** (rule #10).
- **No string interpolation in `frappe.db.sql`** — parameterized queries only.
- **All user-facing strings wrapped in `_("…")`** (rule #13 / ADR-038) — Vue strings via Frappe's translation hook. The CI lint added in T-074 enforces this going forward.

---

## Adapter selector contract (INTEGRATIONS.md §0)

Three behaviours non-negotiable in `alumni/integrations/__init__.py`:

1. **App-presence is the default discriminator.** Most adapters pick `_real` when their target Frappe app is in `frappe.get_installed_apps()`.
2. **AI is special.** `_real` is selected via `Alumni Settings.ai_provider` + `ai_enabled`, **NOT** via installed apps. Special-case lives BEFORE the app-presence check.
3. **Defensive default.** If `Alumni Settings` doesn't yet exist (during install / migrate / pre-wizard), the selector swallows `frappe.DoesNotExistError` and returns `"fallback"`. Every `_fallback` is callable on an empty site (storage especially gets called during fixture import).

---

## Spec count totals — sanity check (last verified 2026-04-29)

If a count drifts during a doc edit, there's an inconsistency to chase.

| Thing | Count |
|---|---|
| First-class DocTypes | ~105 |
| ADRs | 54 (031–054) |
| Build tickets | 116 |
| Adapters | 12 |
| Default themes | 4 (Heritage / Modern / Bold / Aurora) |
| SMS / WhatsApp providers | 12 + Custom HTTP |
| Email templates | 29 |
| Election DocTypes | 13 |
| vCard DocTypes | 17 |
| Built-in vCard templates | 2 (Classic Professional, Modern Minimal) |
| Built-in WhatsApp Store templates | 1 (Standard Storefront) |

---

## Lifecycle labels — canonical, don't paraphrase

`Alumni Profile.status` Select values:

```
Draft → Pending Email → Pending Docs → Active → Suspended | Deceased
```

Substates are named for what is **still pending**. `Pending Email` = waiting for email verification. `Pending Docs` = email verified, waiting for verification document review. The opposite framing ("Email Verified" / "Docs Submitted") was a pre-hygiene typo that got corrected in `spec-hygiene-pre-t001`. Don't regress the prose.

---

## Where authoritative knowledge lives

| Question | Doc |
|---|---|
| What's the rule? | `CLAUDE.md` (25 hard rules + forbidden patterns) |
| What's the schema? | `SPEC.md` §03 (inventory) + §04 (fields) |
| Why was the choice made? | `DECISIONS.md` (54 ADRs, append-only) |
| What does the adapter expose? | `INTEGRATIONS.md` §1–§12 (§0 = selector contract) |
| What does the next ticket need? | `BUILD_TICKETS.md` (sized for one Claude Code session each) |
| Visual tokens | `THEMES.md` |
| Component patterns / motion / a11y / RTL / perf | `DESIGN_SYSTEM.md` |
| Project state + blockers + next 3 tickets | `PROJECT_STATE.md` |
| Onboarding new Claude sessions | `CLAUDE_CODE_SETUP.md` |

---

## v2 deferrals (won't bite v1, but don't forget)

See `DECISIONS.md` § "v2 cleanup notes" (appended after ADR-054).

- **Polymorphic comment consolidation.** v3 ships three comment-shaped DocTypes: the generic `Alumni Comment` (polymorphic), the specialized `Alumni Campaign Comment` (donation-campaign, supports guest commenters), and `Alumni Candidate Comment` (election, has its own moderation workflow). v2 cleanup: extend the generic `Alumni Comment` and migrate the two specialized tables into it.

---

## Current branch state (as of 2026-05-01)

- `main` — baseline import of v3 spec docs + spec hygiene + .claude bootstrap (`c3ef797`)
- `phase-0/t-001-repo-scaffold` — **T-001 scaffold landed locally**. Adds `pyproject.toml`
  (ruff + pytest + coverage 80% gate), `.pre-commit-config.yaml`, `MANIFEST.in`,
  `license.txt` (canonical AGPL-3.0), `.github/workflows/ci.yml` (matrix on
  `alumni_mode` per ADR-021 — standalone + school_connected legs, both run
  `bench migrate` twice for idempotency, pytest is collect-only until tests land),
  and the `alumni/` Frappe-app skeleton (`hooks.py`, `modules.txt`, `patches.txt`,
  `config/`, `public/`, `templates/`, `www/`, `alumni/doctype/`). README Install
  section now distinguishes peer Frappe apps from Python packages and shows the
  extra `bench get-app erpnext|education` step for school_connected mode. Pending
  push + PR.

---

## Next up

After T-001 PR merges: **T-002 — Adapter Layer skeleton** (Phase 0). Per
`BUILD_TICKETS.md` lines 24–36: scaffold all 12 adapters with public surface +
`_real` + `_fallback` stubs (events real-only; verification fallback-only; ai
scaffolded with `ai_fallback.py` raising `NotImplementedError("AI not enabled")`,
real driver work deferred to T-104). Implement the selector in
`alumni/integrations/__init__.py` with the AI special-case branch and the
`frappe.DoesNotExistError` defensive default for the pre-Settings install path.
Test that the selector returns `"fallback"` when `Alumni Settings` doesn't yet
exist.

---

## Daily workflow reminders

- **One ticket = one session.** Resist the urge to do two at once — accuracy drops.
- After every commit, run `git diff --stat` and `git diff` and check the changes match the ticket's stated scope.
- For PR review, paste the diff into a fresh Claude.ai web session and ask for a ruthless second-opinion review.
- End of session: update `PROJECT_STATE.md` with shipped commit hashes, blockers, next 3 tickets.
- For UI / frontend changes, **start the dev server and use the feature in a browser** before reporting complete. Type checks are not feature checks.
- For DocType changes, run `bench migrate` twice on staging to confirm idempotency.
- Cross-mode tests are non-negotiable for any payment / membership / event / donation feature — `@pytest.mark.parametrize("mode", ["school_connected", "standalone"])` and CI runs both legs.
