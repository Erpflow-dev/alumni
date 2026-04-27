# BUILD_TICKETS.md — implementation backlog

Tickets in dependency order. Each is sized for one Claude Code session (1–6 hours).

> **Workflow:** copy a ticket into Claude Code, paste relevant SPEC.md section if needed, complete it, open a PR. Mark `[x]` when merged. Update `PROJECT_STATE.md` weekly.

> **Spec v3 update — Apr 2026.** Tickets T-001 through T-061 are the original v1/v2 backlog. Tickets T-062 through T-087 were added after the v3 feature-parity review (private messaging, document verification, full election system, donation upgrades, site CMS, identity uplifts). They are interleaved logically into the existing phases via the **Phase index** at the bottom.

---

## Phase 0 — Foundation

### `[ ] T-001 — Repo scaffold`
**Outcome:** A Frappe v16 app installable with `bench install-app alumni` on a vanilla site.
**Steps:**
- `bench new-app alumni` with AGPL-3.0 license
- Add `pyproject.toml` deps: `frappe>=16.0.0`, `payments`, `buzz` (peer-dep noted in README)
- Drop the 11 root docs: `README.md`, `CLAUDE.md`, `DECISIONS.md`, `SPEC.md`, `INTEGRATIONS.md`, `THEMES.md`, `BUILD_TICKETS.md`, `PROJECT_STATE.md`, `CLAUDE_CODE_SETUP.md`, `CHANGELOG.md`, `license.txt`
- CI: GitHub Actions running `ruff`, `pytest`, `bench migrate` on a vanilla Frappe v16 site with `payments` and `buzz` installed
- pre-commit: ruff + eslint + prettier + pyupgrade
- Add `.claude/project.md` pinning Frappe v16 + skill package context
**Done:** CI green on empty app on Frappe v16.

### `[ ] T-002 — Adapter Layer skeleton`
**Outcome:** All 12 adapters exist with public surface + `_real` + `_fallback` stubs (events has only `_real` per ADR-025; verification has only `_fallback` since it is internal-only; AI ships with both but `_real` is a thin shim that T-104 fleshes out with provider drivers).
**Steps:**
- Create `alumni/integrations/__init__.py` with selector per INTEGRATIONS.md §0 — including the AI special-case branch and the `frappe.DoesNotExistError` defensive default for the pre-Settings install / migrate path
- Create `<area>.py` and implementations for: education, receivables, events, storage, mail, analytics, live_class, certificates, communication, **messaging** (new in v3 per ADR-031), **verification** (new in v3 per ADR-032), **ai** (new in v3 per ADR-054 lesson #10 — scaffold only; T-104 lands the real driver implementations)
- All `_real` methods raise `NotImplementedError("requires <app>")`
- All `_fallback` methods return safe defaults
- `events_real.py` is the only events impl — required dep; **no `events_fallback.py`**
- `messaging_fallback.py` uses internal Message Thread / Message DocTypes; `messaging_real.py` is reserved for future Raven backend
- `verification_fallback.py` uses internal Alumni Verification Document table; **no `verification_real.py`**
- `ai_fallback.py` raises `NotImplementedError("AI not enabled")` for `draft`; `ai_real.py` is a stub module with the public function signatures from INTEGRATIONS.md §12 — driver implementations and `ai/contexts.py` allow-lists land in T-104
- Test that selector survives a missing Alumni Settings (delete the Single, call `_mode_for("storage")`, expect `"fallback"` — not `DoesNotExistError`)
**Done:** `pytest tests/integrations/` runs (most tests skipped/xfailed); the missing-Settings selector test passes.

### `[ ] T-003 — CI guard for cross-app imports`
**Outcome:** PRs that import from outside `integrations/` fail CI. Buzz, ERPNext, Education, Insights, Raven all blocked.
**File:** `tests/test_no_cross_app_imports.py` per `INTEGRATIONS.md` § CI guard.
**Done:** Test passes; planted-violation test demonstrates failure.

### `[ ] T-004 — Alumni Settings + Theme + first-run wizard`
**Outcome:** First user lands on `/setup-wizard`, picks mode, fills institution name + currency + theme + payment gateway + email + default language.
**Steps:**
- DocType `Alumni Settings` (Single) per SPEC §04 — including v3 sections: Verification & Security, Messaging, Election
- DocType `Alumni Theme` (read-only, populated from `themes/` folders on install) — includes `supports_rtl` field
- `setup/wizard.py` exposing 7-step wizard via Frappe Onboarding (extra step in v3: language + RTL + 2FA gate confirmation)
- Lock `mode` after first save (System Manager only resets)
- Theme picker shows the 3 default themes
**Done:** Fresh site → wizard → mode + theme + language chosen → settings persisted → site reloads with theme.

### `[ ] T-005 — Theme system + 3 default themes (LTR + RTL ready)`
**Outcome:** Heritage / Modern / Bold themes shipped. Switch in Settings = instant change. Validator enforces required tokens. RTL stylesheet hooks present per ADR-038.
**Steps:**
- Folder structure `alumni/themes/<id>/` with `theme.json`, `tokens.css`, `tokens.rtl.css` (optional), `preview.png`
- Create the 3 themes per `THEMES.md`. All 3 declare `supports_rtl: true` in `theme.json`.
- `setup/install.py` discovers themes on install and creates `Alumni Theme` records
- API: `list_themes()`, `activate_theme(theme)`
- On activation: write `alumni/public/css/active-theme.css` with content hash
- Validator: required tokens, contrast check (≥4.5:1), no `<script>` / external `@import`, valid `supports_rtl`
- Inheritance: `parent_theme` field merges tokens
- Tests: validator catches missing tokens, contrast failures, malicious CSS, missing RTL when claimed
**Done:** All 3 themes installable; switching in Settings updates the live site instantly; switching `default_language` to Arabic flips the body to `dir="rtl"` with no broken layouts.

---

## Phase 1 — Identity

### `[ ] T-006 — Alumni Profile DocType`
**Outcome:** Full Alumni Profile per SPEC.md §04 with v16 type annotations and data masking on PII. Includes v3 fields: `messaging_preference`, `2fa_enabled`, `social_login_provider`, `preferred_language`, `verification_documents`, `verification_status`.
**Steps:**
- DocType + child tables (Career Entry, Education Entry, Verification Document)
- Controller with type-annotated `validate`, `before_save`
- v16 data masking decorator on phone, whatsapp, email when displayed to non-owner
- Permission rules per SPEC §06
- Field-level redaction in `permissions.py`
- Tests: create / read / permission denial / privacy redaction / data masking
**Done:** Profile works in both modes.

### `[ ] T-007 — Past Student stub + Alumni Department stub (standalone)`
**Outcome:** Standalone-mode admins can pre-seed historical alumni.
**Done:** CSV import works; standalone mode usable.

### `[ ] T-008 — Self-registration public form`
**Outcome:** `/alumni/register` works in both modes. Includes file-upload control for verification documents (per ADR-032).
**Steps:**
- Public Jinja form, anti-bot honeypot + Frappe rate limiter
- Multi-step: account → identity → verification documents (≥1 required if `require_verification_documents`)
- On submit: creates Alumni Profile in `Pending Email` status, dispatches email verification token
- Tests: happy path, missing email verification, missing docs, rate-limit hit, malicious file type rejected
**Done:** Anonymous user submits form → Pending Email profile created → email sent.

### `[ ] T-062 — Email verification API + flow` *(NEW v3, per ADR-039)*
**Outcome:** `request_email_verification(email)` and `confirm_email_verification(token)` whitelisted endpoints work.
**Steps:**
- Implement in `alumni/integrations/verification.py` — `issue_email_verification_token`, `verify_email_token`
- Token: signed JWT (HS256 with site secret), payload `{email, exp, nonce}`, 24h expiry
- Confirm endpoint: marks `email_verified=1`, advances profile status `Pending Email → Pending Docs` (or → Active if docs not required)
- Email template `alumni_email_verification` (loaded as fixture)
- Tests: token valid, expired token, replayed token, malformed token, status transitions
**Done:** Self-registered alumni clicks email → status advances correctly.

### `[ ] T-063 — Phone verification (OTP) API + flow` *(NEW v3, per ADR-039)*
**Outcome:** Optional phone OTP via communication adapter, gated on `Alumni Settings.require_phone_verification`.
**Steps:**
- `request_phone_otp(phone)` and `verify_phone_otp(phone, code)` whitelisted endpoints
- 6-digit numeric, 10-min expiry, 3-attempt lockout per phone per hour
- OTP stored in cache (`frappe.cache().set_value`) — never DB
- Communication adapter SMS path (no-op in fallback if no SMS gateway configured)
- Email fallback ("we couldn't text you, here's the code") if SMS fails 3x
- Tests: happy path, expired code, wrong code, lockout, SMS unavailable
**Done:** When enabled in Settings, phone verification works end-to-end; when disabled, endpoints return 404.

### `[ ] T-064 — Verification document review queue` *(NEW v3, per ADR-032)*
**Outcome:** Admin sees a "Pending Verifications" Frappe List View with one-click Accept/Reject. Reject opens a textarea for the rejection reason that goes into the templated email.
**Steps:**
- Frappe List View on Alumni Profile filtered by `verification_status = Pending Review`
- Custom buttons in profile detail: "Approve verification" (advances to `Active`), "Reject" (status back to `Pending Docs`, sends rejection email with reason)
- Email templates: `alumni_verification_approved`, `alumni_verification_rejected`
- Audit log entry on each decision (who, when, decision, reason)
- Tests: approve flow, reject flow, audit entries created, email queued
**Done:** Admin can clear the queue in under 30 seconds per profile.

### `[ ] T-009 — School-Connected auto-promote job`
**Outcome:** Nightly job creates Drafts from graduating Students.
**Done:** Job runs on staging; profiles appear; emails queued.

### `[ ] T-010 — Profile approval + onboarding`
**Outcome:** Admin approves Pending → Active; alumni completes onboarding (incl. messaging preference + 2FA prompt for staff roles).
**Done:** End-to-end flow works.

### `[ ] T-065 — Social login wiring` *(NEW v3, per ADR-037)*
**Outcome:** When `Alumni Settings.social_login_enabled = 1`, login page shows enabled providers from `social_login_providers`. First-time social-login users land in `Pending Docs` (skip email gate since OAuth provider already verified the email).
**Steps:**
- No new code in alumni for OAuth itself — this is 100% Frappe core OAuth Provider Settings configuration
- `setup/social_login.py` helper that flips the right Social Login Key flags from the alumni admin UI
- Login page Jinja override that renders the provider buttons
- Profile creation hook on `User` `after_insert`: if user came in via Social Login Key, create Alumni Profile in Pending Docs and email them
- Field `Alumni Profile.social_login_provider` populated from the User record
- Tests: provider configured → button shows; user signs in via Google → profile created in correct status
**Done:** Demo deployment with Google + LinkedIn enabled; both buttons work.

### `[ ] T-066 — 2FA enforcement middleware for Admin/Board roles` *(NEW v3, per ADR-036)*
**Outcome:** When `mandatory_2fa_for_admin = 1`, an Admin / Board Member / System Manager attempting any write operation without TOTP enrollment is redirected to `/setup-2fa` and writes are blocked.
**Steps:**
- Hook `before_request` (whitelisted endpoints) and override `Document.save` for the gated roles
- Frontend: settings page section "Two-Factor Authentication" surfacing Frappe's TOTP enrollment with a friendly wrapper
- Soft prompt for Alumni role on first login (banner with "Enable 2FA" CTA, dismissible)
- Tests: gated role without 2FA can't write; same role with 2FA can; alumni without 2FA can write
**Done:** Cannot bypass; Frappe's User Permissions still apply normally.

### `[ ] T-011 — Alumni Audit Log`
**Outcome:** Sensitive operations logged to UUID-named audit table.
**Done:** Log entries appear for: visibility changes, mentorship flags, donation refunds, profile reads of others' contact data, **vote_cast, nomination_approved, message_reported, verification_decided** (v3 additions).

---

## Phase 2 — Directory & Social

### `[ ] T-012 — Directory search API + page`
**Outcome:** `/alumni/directory` searchable and respectful of privacy.
**Done:** Search returns redacted results; map shows pins per country.

### `[ ] T-013 — Posts, Comments, Reactions (polymorphic, UUID autoname)`
**Outcome:** Alumni can post short updates; comment/react on Posts/Stories/News/Notices/**Campaigns** (v3 — see T-072) / **Candidates** (v3 — see T-080).
**Done:** Feed works with comments and reactions.

### `[ ] T-014 — Alumni Stories with workflow + categories`
**Outcome:** Stories submitted by alumni go through Pending → Approved → Published. **Story Category** taxonomy added.
**Done:** Workflow end-to-end with notifications; filterable by category.

### `[ ] T-015 — News & Notices with categories + tags`
**Outcome:** Admin posts News / Notices. Alumni see in feed. **News Category, News Tag, Notice Category** taxonomies added per v3 spec.
**Done:** New News appears in feed and pushes notifications; filterable by category and tag.

### `[ ] T-067 — Private 1:1 messaging — DocTypes + send/receive API` *(NEW v3, per ADR-031)*
**Outcome:** Alumni Message Thread / Alumni Message / Alumni Message Read Receipt DocTypes plus the messaging adapter's full surface working with the fallback backend.
**Steps:**
- DocTypes per SPEC §04 messaging schemas
- Thread normalization: controller sorts (`participant_a` < `participant_b`) on save → guarantees one thread per pair
- Messaging adapter functions: `open_thread(alumni_a, alumni_b)`, `send_message(thread, sender, body, attachments)`, `list_threads_for(alumni)`, `list_messages(thread, before, limit)`, `mark_read(thread, reader, up_to_message)`, `block_thread(thread, by)`, `report_thread(thread, by, reason)`
- Recipient gate: enforce `messaging_preference` (All / Same Batch / Mentees Only / Off)
- Spam: rate limit ≤30 msgs/min per sender via Frappe cache
- Audit log entry on `report_thread`
- Tests: 12 cases covering happy path, blocked, rate-limit, preference filter, attachment too large, unverified sender blocked
**Done:** Two-test-user conversation flows work.

### `[ ] T-068 — Messaging realtime + UI` *(NEW v3, per ADR-031)*
**Outcome:** Messages appear instantly in the recipient's inbox. Vue inbox page with thread list + message pane + composer + emoji + attachment uploader + block / report buttons.
**Steps:**
- Backend: `frappe.publish_realtime("alumni_new_message", payload, user=recipient_user)` after each insert
- Frontend: Vue 3 + Frappe UI — `Inbox.vue`, `Thread.vue`, `Composer.vue`
- Frappe socketio subscription on mount; reconnect logic; typing indicator (optional, debounced realtime event)
- Unread count badge in nav (driven by `participant_X_unread_count` on Thread)
- Tests (Playwright): two browser contexts → user A sends, user B sees within 2s
**Done:** Realtime works; reconnect after network blip recovers; mobile layout passes responsive checks.

### `[ ] T-069 — Messaging admin moderation queue` *(NEW v3, per ADR-031)*
**Outcome:** Reported threads appear in a Moderator queue; can read full thread (audited), warn user, or suspend account.
**Steps:**
- Moderator role gets read access to Reported Threads only (not all threads — privacy)
- Reading a reported thread writes one Audit Log entry per session per thread
- Warn action: dispatches templated email to offender; sets `Alumni Profile.warnings += 1`
- 3 warnings → automatic Suspended status (configurable threshold in Settings)
**Done:** End-to-end moderation flow works; non-reported threads remain invisible to Moderators.

---

## Phase 3 — Money (memberships + donations)

> Events go through Buzz's existing payment flow — Phase 5. This phase is for memberships + donations only.

### `[ ] T-016 — Receivables fallback DocTypes`
**Outcome:** `Alumni Invoice` + `Alumni Invoice Item` + `Alumni Payment` for standalone.
**Done:** Standalone test creates invoice + payment; CSV export works.

### `[ ] T-017 — Receivables real (ERPNext) implementation`
**Outcome:** `receivables_real.py` creates Customer + Item + Sales Invoice + Payment Entry.
**Done:** Both modes parametrized tests pass.

### `[ ] T-018 — frappe/payments integration in Settings`
**Outcome:** Admin links a Payment Gateway record in `Alumni Settings`.
**Done:** Settings stores the link; receivables uses it; Buzz reads the same.

### `[ ] T-019 — Manual / offline payment flow`
**Outcome:** "Mark as Paid" admin button on invoices for offline transactions.
**Done:** End-to-end without external gateway.

### `[ ] T-020 — Webhook handler for memberships and donations`
**Outcome:** `payment_webhook` updates Membership / Donation status, generates artifacts.
**Done:** Test triggers webhook → invoice paid → certificate emailed.

---

## Phase 4 — Membership

### `[ ] T-021 — Membership Plans + Memberships`
**Outcome:** Admin defines plans; alumni buy.
**Done:** End-to-end purchase + card emailed.

### `[ ] T-022 — Membership renewal reminders + expiry sweep`
**Outcome:** Scheduled reminders 30/7/1 day; daily expiry sweep.
**Done:** Tests pass at correct intervals.

---

## Phase 5 — Events (via Buzz)

### `[ ] T-023 — Events adapter (Buzz wrapper) — real implementation`
**Outcome:** `events.create_event`, `update_event`, `publish_event`, ticket type / add-on / sponsorship management, `book`, `get_booking`, `list_bookings_for_alumni`, `cancel_booking`, `transfer_ticket`, `scan_ticket` all wired to Buzz.
**Done:** Integration tests demonstrate Buzz Event created via adapter; bookings flow through Buzz.

### `[ ] T-024 — Alumni Event Wrapper DocType`
**Outcome:** 1:1 wrapper over Buzz Event with our visibility / chapter / passing-year filters / featured flag.
**Done:** End-to-end creation through our UI; ticket types editable via embedded Buzz form.

### `[ ] T-025 — Public event listing + detail page`
**Outcome:** `/alumni/events` lists Public-visibility events. `/alumni/events/{name}` shows detail with "Book on Buzz" CTA.
**Done:** Public page renders; ticket purchase routes to Buzz checkout.

### `[ ] T-026 — Member pricing logic`
**Outcome:** When `member_pricing_enabled` and the booker is an active paid Member, member price applies.
**Done:** Member sees discounted price; non-member sees standard.

### `[ ] T-027 — Buzz status sync job`
**Outcome:** `tasks.sync_buzz_event_statuses` polls Buzz Bookings, emits our notifications.
**Done:** Booking confirmation triggers our `event_booking_confirmed` email.

### `[ ] T-028 — Event reminder 24h job`
**Done:** All confirmed attendees of upcoming events receive reminder.

### `[ ] T-029 — Online event integration with live_class adapter`
**Outcome:** When the Wrapper has no venue, live_class adapter generates a join link, written back to Buzz Event's `online_link`.
**Done:** Standalone mode generates Jitsi link; school-connected calls school_live_class.

---

## Phase 6 — Donations

### `[ ] T-030 — Donation Campaigns + Donations (one-time, v1)`
**Outcome:** Admin creates campaigns; alumni donate. Includes v3 fields per ADR-034: `category`, `allow_guest_donations`, `allow_comments`.
**Done:** Donation flow end-to-end with tax receipt PDF.

### `[ ] T-070 — Donation Categories taxonomy + browse page` *(NEW v3, per ADR-034)*
**Outcome:** Admin defines categories (Scholarships, Library, Sports, Emergency Fund, etc.) with icons + cover images. Public `/alumni/give` page groups campaigns by category.
**Steps:**
- DocType `Alumni Donation Category` per SPEC §04
- Public page: tile per category with running raised total + active campaign count
- Drill-in: `/alumni/give/<category>` shows category-filtered campaigns
- Cache the category aggregates (`tasks.refresh_donation_category_totals`, hourly)
**Done:** Categories appear; clicking a category filters campaigns; counts accurate.

### `[ ] T-071 — Guest donation public flow + tax receipt` *(NEW v3, per ADR-034)*
**Outcome:** Guest visitor on `/alumni/give/<campaign>` can donate without an account when `allow_guest_donations = 1`.
**Steps:**
- Whitelisted public endpoint `donate_as_guest(campaign, name, email, amount, currency, payment_method, message)`
- Honeypot + per-IP rate limit + email format validation
- Creates Alumni Donation with `is_guest=1, donor=null, guest_name, guest_email`
- After payment: tax receipt PDF (template branched on `is_guest`) emailed to `guest_email`
- Privacy: guest emails NEVER appear in directory, alumni-facing lists, or any export visible to non-Admins
- Test: guest donates → receives receipt → does not appear in directory under any role
**Done:** Stripe-test happy path passes; donor list view in admin shows guest with badge.

### `[ ] T-072 — Campaign comments (moderated)` *(NEW v3, per ADR-034)*
**Outcome:** Logged-in alumni can leave a comment on any campaign with `allow_comments = 1`. Comments are pending → admin approves → appear publicly.
**Steps:**
- DocType `Alumni Campaign Comment` per SPEC §04, with 1-level threading
- Mod queue list view filtered by `is_published=0`
- Notification to admins on new comment (batched: max 1 email/hour)
- Public widget: rendered under campaign with paginated approved comments
- Audit log on publish/reject decisions
**Done:** End-to-end comment → moderation → public display works.

### `[ ] T-031 — Matching gift support`
**Done:** Matching multiplier applied up to cap.

### `[ ] T-032 — Public landing campaign progress widget`
**Done:** `public_stats` returns campaign progress; landing renders bar.

---

## Phase 7 — Jobs & Volunteering

### `[ ] T-033 — Job Posts + Applications`
**Done:** End-to-end with three apply methods (in-app / external URL / email).

### `[ ] T-034 — Volunteer Opportunities + Signups`
**Done:** Same shape.

---

## Phase 8 — Network features

### `[ ] T-035 — Ask the Network Q&A`
**Outcome:** Public flag works for SEO surface.
**Done:** Q&A in both modes; public page renders public Qs.

### `[ ] T-036 — Geographic Chapters`
**Outcome:** Admin creates; alumni join; chapter-only events filterable.
**Done:** Chapter list + join + filtering work.

### `[ ] T-037 — Reunion Groups (auto-managed)`
**Outcome:** Auto-created per passing year that has alumni.
**Done:** Test seeds 3 alumni from 2018 → group exists with count=3.

---

## Phase 9 — Mentorship

### `[ ] T-038 — Mentorship Request flow`
**Outcome:** Mentee requests; mentor accepts/declines; masked initials + CoC gate.
**Done:** Both modes work.

### `[ ] T-039 — Mentorship Sessions`
**Outcome:** Scheduled sessions with online_link from live_class adapter; reminder 1h before; flag/report flow.
**Done:** End-to-end with audit log entries on flag.

---

## Phase 10 — Outcomes

### `[ ] T-040 — Outcome Survey templates + dispatch`
**Outcome:** Surveys at 1/3/5/10 years; anonymized aggregation.
**Done:** Test seeds 2018 grad → 5-year survey dispatched in 2023.

---

## Phase 11 — Comms

### `[ ] T-041 — Newsletter with segments`
**Done:** Send to 2018 batch only → only those addresses targeted.

### `[ ] T-042 — Transactional email templates fixture (29 templates)`
**Outcome:** v3 expands the template set: original 15 + new for verification (5), elections (6), donations (2), messaging (1). All 29 templates load on `bench migrate`. Canonical list lives in SPEC.md §09.
**Done:** Fixture loads cleanly; render-test asserts each template produces non-empty output with mock context.

### `[ ] T-043 — Push notification via communication adapter`
**Done:** Test asserts adapter called.

### `[ ] T-088 — Alumni Communication Channel + 12 built-in provider drivers` *(NEW v3, per ADR-040)*
**Outcome:** Admins register any number of SMS / WhatsApp channels via the `Alumni Communication Channel` DocType. Twelve provider drivers ship in `communication_real.py`: Twilio, Twilio WhatsApp, MessageBird, Vonage, Plivo, Africa's Talking, Wati, Gupshup, 360Dialog, Unifonic, MSG91, SSL Wireless. Plus a Custom HTTP driver for any API the user can describe with URL + auth + Jinja payload.
**Steps:**
- DocType `Alumni Communication Channel` per SPEC §04 with encrypted `auth_credentials` (Password field)
- Driver registry: `communication_real.drivers.<provider>.send(channel, to, body, **kwargs)` — one module per provider
- Custom HTTP driver: reads `http_url`, `http_method`, `http_auth_header`, `http_payload_template` (Jinja), `http_response_id_path` from the channel
- Channel routing precedence per ADR-040: explicit → country → default → first active → error
- `Alumni Settings` fields wired: `default_sms_channel`, `default_whatsapp_channel`, `transactional_sms_channel`
- "Test send" button on each channel record: prompts for a phone number, sends a fixed test message, displays the provider response
- Daily job: reset `sends_today`; recompute `sends_this_month`; auto-deactivate channels at quota with Admin warning email
- Webhook endpoint `alumni.api.communication_webhook` for delivery receipts; signature/secret per provider documented
- Tests: each driver mocked end-to-end happy path + auth fail; Custom HTTP driver with fixture provider config; routing precedence covered with 6 cases
**Done:** Admin can register a Twilio channel + a Wati WhatsApp channel + a Custom HTTP fallback in 3 minutes; test sends arrive; OTPs work via the configured transactional channel.

### `[ ] T-089 — Alumni Broadcast: compose, segment, preview, queue, send` *(NEW v3, per ADR-040)*
**Outcome:** Admin composes a broadcast in one form: pick medium → pick channel (or auto) → pick segment → preview recipient count → schedule or send. Submission queues per-recipient sends through the communication adapter. Live counters update; per-recipient delivery tracked in `Alumni Broadcast Log Entry`.
**Steps:**
- DocType `Alumni Broadcast` + child `Alumni Broadcast Log Entry` per SPEC §04
- Composer UI (Vue): segment picker with live recipient-count preview, channel picker, body editor with character counter (160 SMS / 1600 concat), WhatsApp template picker with variable form when applicable
- Segment resolver `communication.resolve_segment(segment_type, filter, extra)` — pure function returning a list of Alumni Profile names
- Background job `alumni.tasks.dispatch_broadcast(broadcast)` — chunked through Frappe's job queue, respects `broadcast_max_recipients_per_minute`
- Per-recipient skip rules: messaging_preference=Off, phone unverified (when `respect_phone_verified=1`), country mismatch, no phone on file, daily quota exceeded
- Retry: failed entries retried at 1m + 5m + 30m, capped at 3 attempts
- Cancellation: Admin can cancel a Queued/Sending broadcast; in-flight sends complete but no new ones start
- Double-confirm gate: when recipient count ≥ `broadcast_require_admin_double_confirm_above`, force "type the title to confirm" before submit
- Audit log: one summary entry on submit (`event_type=broadcast_sent`, payload includes hashed body, segment, channel, recipient count) — never plaintext body
- Tests: 8 cases — segment resolution for each segment_type, skip-rule honoring, cancellation race, retry sequence, double-confirm gate, plain SMS happy path, WhatsApp template happy path, partial failure (50% success → retry → final result)
**Done:** Admin sends a broadcast to "Class of 2018, KSA-only, via Unifonic SMS" — receives report 60 seconds later showing per-recipient delivery status.

### `[ ] T-090 — Broadcast dashboard + cost tracking` *(NEW v3, per ADR-040)*
**Outcome:** Operations dashboard shows: sends today / this month per channel, cost estimate (using each channel's `cost_per_send`), broadcast history with success rates, top failed-recipient phone numbers (for cleanup), and quota usage bars per channel.
**Done:** Render in standalone via Chart.js; "Open in Insights" link when Insights installed.

### `[ ] T-091 — Aurora dark theme + design system documentation` *(NEW v3, per ADR-043)*
**Outcome:** Fourth default theme `Aurora` (dark mode) ships alongside Heritage / Modern / Bold. New `DESIGN_SYSTEM.md` documents the full component vocabulary. Storybook (or equivalent) seeded with all documented components in both light and dark variants.
**Steps:**
- Folder `alumni/themes/aurora/` with `theme.json` (`color_scheme: "Dark"`), `tokens.css`, `tokens.rtl.css`, `preview.png`, `components.css`
- Token contract for Aurora maintains contrast ≥4.5:1 (validated)
- `Alumni Profile.preferred_theme` field wired — overrides institution default
- Theme loader checks `prefers-color-scheme` when `enable_dark_mode_auto = 1` and user has not set a preference
- Storybook stories for: Button (primary / secondary / ghost / danger / sizes), Card, Input + variants, Modal, Toast, Empty state, Loading skeleton, Avatar, Badge, Tabs, Pagination, Date picker, Select / multi-select, Tag, Tooltip, Progress, Stepper, Sidebar nav, Header, Footer
- All stories render in 4 themes × 2 directions = 8 variants
- Visual regression: chromatic-style snapshots gate PRs that change tokens or component CSS
**Done:** All 4 themes pickable; OS-level dark preference auto-engages Aurora when no user preference set; Storybook deployed to a public URL; visual regression CI green.

---

## Phase 12 — Public site & Subdomain

### `[ ] T-044 — Public landing built with Frappe Builder`
**Outcome:** `/alumni` (or root in standalone) — landing rendered from Builder fixture.
**Done:** Builder pages installable as fixtures; tokens applied.

### `[ ] T-045 — About / Contact / FAQ public pages`
**Done:** Builder pages or Jinja, depending on what's friendlier.

### `[ ] T-073 — Site CMS DocTypes (FAQ, Testimonial, Image Gallery, Hero Banner)` *(NEW v3)*
**Outcome:** Four content DocTypes that the Builder pages reference, so non-developers maintain the public site without touching Builder.
**Steps:**
- DocType `Alumni FAQ` (question, answer rich text, category, sort_order, is_published)
- DocType `Alumni Testimonial` (alumni_link, quote, photo, role_snapshot, is_published, sort_order)
- DocType `Alumni Image Gallery Item` (image, caption, gallery_section, sort_order, is_published)
- DocType `Alumni Hero Banner` (heading, subheading, cta_label, cta_url, background_image, sort_order, is_active, valid_from, valid_to)
- Builder helper components: `<AlumniFaqList />`, `<AlumniTestimonials />`, `<AlumniGallery section="campus" />`, `<AlumniHeroBanner />`
- Tests: scheduled visibility windows respected; sort order honored
**Done:** Admin can add/edit FAQ entries → instantly visible on `/alumni/faq` without dev help.

### `[ ] T-074 — Multilingual translations + RTL pass + unwrapped-string CI lint` *(NEW v3, per ADR-038)*
**Outcome:** All user-facing strings wrapped in `_("…")`. Translation .csv files for English (source), Arabic, Hindi, Bengali, Spanish, Portuguese, French, Indonesian. RTL layout verified for Arabic. **CI lint enforces wrapping going forward** so future PRs can't reintroduce raw strings.
**Steps:**
- `bench --site test.local generate-pot-file --app alumni`
- Seed `alumni/translations/ar.csv` etc. with priority strings (top 200) using `_()` keys
- Add `[dir="rtl"]` selectors in component CSS for layout swaps (margins, icon flips)
- Vue: hook through `frappe.client.get_translation`
- E2E test: switch site language to Arabic → public landing renders RTL with no overflow
- **CI lint** `tests/test_user_facing_strings_wrapped.py` — walks `.py` files in user-facing modules (`alumni/api.py`, `alumni/alumni/doctype/`, `alumni/templates/`, `alumni/www/`), parses each via `ast`, and **flags any string literal** passed as a positional arg to: `frappe.msgprint`, `frappe.throw`, `print`, a `return` of a bare string, or `raise <Exception>(...)` — that isn't wrapped in `_(...)`. Allow-list (don't flag): `frappe.logger().*` calls, exception classes from `frappe.exceptions`, fixture / enum / dict-key string literals, strings inside `# noqa: i18n` comments, docstrings.
- The lint targets the same surface set the translator scans (`generate-pot-file`), so anything the lint passes is guaranteed translatable.
- Vue equivalent: ESLint rule `eslint-plugin-vue-i18n` configured with `no-raw-text` to enforce the same on `.vue` templates.
**Done:** Arabic visitor sees Arabic UI in RTL layout; other 6 languages have ≥80% coverage; planted-violation test (a `frappe.throw("Direct string")` call) makes the lint fail.

### `[ ] T-046 — Subdomain hostname routing`
**Outcome:** `alumni.<school>` serves alumni site; main domain serves school site (school-connected mode).
**Done:** Two hostnames serve different sites from one site; documented.

### `[ ] T-047 — Custom branding pulls from Settings + active theme`
**Done:** Logo / colors / social URLs render across the site without code changes.

### `[ ] T-075 — Multi-site deployment runbook + sample bench layout` *(NEW v3, per ADR-035)*
**Outcome:** `docs/ops/multi-site-saas.md` documents the multi-tenant pattern: one bench, many sites, one alumni install on each. Includes shell scripts for `new-tenant.sh` (creates site + installs alumni + seeds Settings + sets domain) and `nginx-vhost.j2` template.
**Done:** Runbook tested by spinning up 3 sample tenants on a staging bench; tenants are fully isolated (DB, files, settings).

---

## Phase 13 — Analytics

### `[ ] T-048 — Analytics adapter + 3 base dashboards`
**Outcome:** Network / Membership / Event dashboards in Vue + Chart.js.
**Done:** Render in standalone with no Insights.

### `[ ] T-049 — Remaining 4 dashboards`
**Done:** Donations / Jobs / Mentorship / Newsletter dashboards live.

### `[ ] T-076 — v3 dashboards: Messaging Health, Election Participation, Verification Pipeline` *(NEW v3)*
**Outcome:** Three new dashboards rounding out the v3 spec.
- **Messaging Health:** active threads/day, messages/day, % alumni who DM'd ≥1 peer, top 10 reported threads (admin-only), median response time
- **Election Participation:** turnout per election (eligible / voted / %), nomination volume by position, votes cast by chapter, vote audit lag (queue depth)
- **Verification Pipeline:** docs awaiting review, median review time (24h target), approval/rejection ratio, rejected-then-resubmitted funnel
**Done:** All three render in standalone via Chart.js; "Open in Insights" deep link present when Insights installed.

### `[ ] T-050 — Open-in-Insights deep links`
**Done:** Each dashboard shows Insights link when installed.

---

## Phase 14 — Committees & Elections (NEW v3 phase)

> Per ADR-033, the election system is first-class. Twelve interlocking DocTypes plus a heavy state machine. Sized as 8 tickets so each fits one Claude Code session.

### `[ ] T-077 — Committee Category + Designation + Committee + Member + Meeting DocTypes` *(NEW v3)*
**Outcome:** All 5 committee-side DocTypes per SPEC §04, including the v3 expansions (Category, Designation child of Committee Member).
**Steps:**
- DocTypes per spec
- Controllers with type annotations
- Permission rules: Admin full; Board Member read all + write Committee Meeting; Alumni read public list only
- Print format for Committee Member appointment letter (uses certificates adapter)
- Tests: create / read / permission denial; no committee can have two `is_current=1` members in the same designation
**Done:** Admin can hand-appoint a committee end-to-end without ever touching elections.

### `[ ] T-078 — Election + Election Position + Election Symbol DocTypes + state machine` *(NEW v3, per ADR-033)*
**Outcome:** Core election DocTypes + workflow: `Draft → Nomination Open → Nomination Closed → Voting Open → Voting Closed → Results Published`.
**Steps:**
- DocTypes per SPEC §04
- Workflow JSON `alumni_election_workflow.json`
- Scheduled job `tasks.advance_election_states()` runs hourly: checks `nomination_open_at / close_at / voting_open_at / close_at / result_publish_at` against now() and advances state, publishing realtime events
- Symbol uniqueness within an election: validator rejects duplicate `assigned_symbol` for the same election
- Test: time-travel test with `freeze_time` advancing through every state transition
**Done:** State machine correct; election self-progresses without manual intervention.

### `[ ] T-079 — Nomination submission + payment + review` *(NEW v3, per ADR-033)*
**Outcome:** Eligible alumni submit nomination during nomination window; pay nomination fee (if any) via receivables adapter; Board Member reviews and approves/rejects.
**Steps:**
- Whitelisted endpoint `submit_nomination(election, position, manifesto, photo, proposed_symbol)`
- Eligibility check on submit: profile Active + status not Suspended + within passing-year window + member tier matches if elections require Members
- If `nomination_fee > 0`: create invoice via receivables adapter; store payment URL on the Nomination; nomination cannot be reviewed until payment status is Paid (or if fee is 0)
- Board Member queue: List View on Nomination filtered by `application_status = Submitted`
- On Approve: controller creates Alumni Candidate, assigns symbol, dispatches `alumni_nomination_approved` email
- On Reject: dispatches `alumni_nomination_rejected` email with reason
- Audit log on every approve/reject (`event_type = "nomination_approved"` etc.)
- Tests: ineligible alumni blocked; payment-required nomination cannot be reviewed unpaid; approve creates Candidate with assigned symbol
**Done:** Nomination → payment → review → Candidate flow complete.

### `[ ] T-080 — Candidate profile public page + comments` *(NEW v3, per ADR-033)*
**Outcome:** Public `/alumni/elections/<election>/candidates/<candidate>` page shows candidate photo, manifesto, assigned symbol. Logged-in alumni can leave moderated comments per Alumni Candidate Comment DocType.
**Steps:**
- Public Jinja page (theme-tokenized)
- Reuse comment moderation pattern from T-072 (campaigns)
- Candidate-comment-specific moderation queue
- Sharing: OpenGraph tags so a candidate's link previews nicely on WhatsApp / X / LinkedIn
- Tests: public page works for Guest; comment requires login; rejected comment never appears
**Done:** A candidate's URL can be shared and works for non-logged-in viewers; comments behave.

### `[ ] T-081 — Vote casting + integrity gates` *(NEW v3, per ADR-033)*
**Outcome:** Logged-in eligible alumni vote during voting window. UUID-named Vote records, DB-unique on (election, position, voter), `voter` field redacted in non-System-Manager queries.
**Steps:**
- DocType `Alumni Vote` (`name=uuid`, fields: `election`, `position`, `voter` (Link Alumni Profile, restricted in serializer), `candidate`, `cast_at`, `audit_status` Select: Pending / Validated / Rejected, `audited_by`, `audited_on`, `audit_note`)
- DB unique index `(election, position, voter)` via `Index` in DocType JSON
- Whitelisted endpoint `cast_vote(election, position, candidate)` with eligibility checks (election state = Voting Open, voter eligible per election rules, voter not already voted on this position)
- Vote serializer redacts `voter` for everyone except System Manager (and the voter themself)
- Confirmation page with one-time review screen "you are about to vote for [candidate], symbol [X] — confirm?"
- Audit log entry per vote (`event_type = "vote_cast"`, payload includes hashed voter ID, never plain)
- Tests: ineligible voter blocked; double-vote blocked at DB level; vote redacted in admin list view; System Manager can read voter
**Done:** Vote cast works; integrity holds under concurrency (parallel double-submits → exactly one succeeds).

### `[ ] T-082 — Vote audit queue (Board Members)` *(NEW v3, per ADR-033)*
**Outcome:** When `vote_audit_required = 1`, Board Members see a queue of `audit_status = Pending` votes; click to approve / reject (with reason). Only Validated votes count toward results.
**Steps:**
- Custom Frappe List View on Alumni Vote, restricted to Board Member + Admin roles
- Bulk-approve action (Frappe ListView Action) with double-confirm
- Reject sets `audit_status = Rejected`, removes from candidate's `votes_count`, audit log entry with reason
- `tasks.recount_validated_votes()` recalculates `Alumni Candidate.votes_count` every 5 min during voting + hourly for the next 24h after close
- Tests: rejected vote does not count; recount idempotent; concurrent audit + recount safe
**Done:** Board Member can clear audit queue; counts update.

### `[ ] T-083 — Election Results: tally, publication, Committee creation` *(NEW v3, per ADR-033)*
**Outcome:** When state advances to `Results Published`, system finalizes counts, marks winners, and (optionally) creates an `Alumni Committee` populated with the winners.
**Steps:**
- `publish_results(election)` action (auto on `result_publish_at`, also manual button for Admin)
- Per position: rank candidates by validated votes_count; top N (where N = `position.seats`) flagged `is_winner = 1`
- Tie-breaker policy: configurable (`tie_breaker = Earlier Nomination | Higher Passing Year Match | Random`)
- Populate `Alumni Election Result` rows (one per position with winners + runner-ups + counts)
- If `auto_create_committee = 1` on Election: create Alumni Committee with `is_elected=1`, `parent_election=election`, members table populated from winners with appropriate Designations
- Public results page `/alumni/elections/<election>/results` with charts (turnout, votes per candidate per position)
- Templated `alumni_election_results_published` email to all eligible voters + special variant to winners
- Tests: tie-breaker triggers; committee created with correct membership; no Vote rows leak voter identity in the public page
**Done:** Election runs end-to-end from Draft to Committee handover.

### `[ ] T-084 — Election public landing + countdown widgets` *(NEW v3, per ADR-033)*
**Outcome:** `/alumni/elections` lists current + recent elections with countdown ("Voting closes in 2d 14h"). Detail page shows positions, candidates per position, and a vote button (logged-in eligible alumni only) during the voting window.
**Done:** Public page renders even when no election is active (shows "Past Elections"); during voting window the vote button is the only thing in view.

---

## Phase 15 — Hardening

### `[ ] T-051 — Privacy gate verification suite`
**Done:** Coverage on permissions.py ≥ 95%, including: vote.voter redaction, message thread access, verification document visibility, guest donor email never exposed.

### `[ ] T-052 — Cross-mode CI matrix`
**Done:** Two green CI jobs per PR.

### `[ ] T-053 — Rate limiting on public endpoints`
**Done:** 6th request in a minute returns 429. Includes `donate_as_guest`, `request_email_verification`, `request_phone_otp`, `submit_nomination`, `cast_vote`.

### `[ ] T-054 — Accessibility pass (WCAG AA)`
**Done:** axe-core report with 0 critical. RTL layouts pass too.

### `[ ] T-055 — Theme contrast lint in CI`
**Done:** PRs that ship a theme failing contrast fail CI.

### `[ ] T-056 — Component CSS hex/rgb lint`
**Done:** Stylelint catches literal colors outside `tokens.css`.

### `[ ] T-057 — Load test: directory + feed + messaging`
**Done:** k6 report — p95 < 500ms with 100 concurrent users; messaging realtime latency p95 < 300ms.

### `[ ] T-058 — Backup + restore drill`
**Done:** Runbook in `docs/ops/backup-restore.md`. Verifies vote integrity preserved across restore.

### `[ ] T-085 — Election integrity test suite` *(NEW v3, per ADR-033)*
**Outcome:** Dedicated test module covering attack scenarios:
- Double voting via concurrent submits
- Vote casting outside the voting window
- Ineligible voter (wrong chapter, wrong passing year, suspended account, non-member when members-only)
- Vote read by non-System-Manager (must return redacted voter)
- Audit log tampering attempt
- Symbol reassignment after voting starts (must be blocked)
- Election state regression attempt (must be blocked)
**Done:** All 7 attack scenarios produce the expected error/safe behavior; coverage on election controllers ≥ 90%.

### `[ ] T-086 — Messaging spam + harassment hardening` *(NEW v3, per ADR-031)*
**Outcome:** Tests + protections covering: rate limit per sender per minute, block list precedence, attachment MIME sniff (not just extension), oversized attachment, message-body XSS sanitization, link-spam pattern detection (≥3 URLs in one message → flagged for review).
**Done:** All cases produce the expected behavior; sanitizer bypass attempts fail.

---

## Phase 16 — Release

### `[ ] T-059 — Documentation site`
**Done:** mkdocs site live; covers install (both modes + multi-site SaaS), themes, integrations, migration, **elections runbook, messaging admin guide, verification queue guide, multilingual setup**.

### `[ ] T-060 — v1.0.0 release`
**Done:** Tagged; CHANGELOG complete; release notes mention Buzz, themes, v16 requirement, and the v3 feature set.

### `[ ] T-061 — Demo data fixture`
**Outcome:** `alumni.demo.seed()` creates 50 alumni, 5 events (via Buzz), 2 campaigns (1 with comments + guests), 1 chapter, 1 active election with 4 candidates across 2 positions, 8 message threads, 5 verification docs in queue.
**Done:** Demo site renders with realistic data in either theme; election demo site shows mid-voting state.

### `[ ] T-087 — ZaiAlumni → Alumni migration script` *(NEW v3)*
**Outcome:** `alumni/migration/from_zaialumni.py` reads ZaiAlumni MySQL export and produces Frappe-importable CSVs for: Alumni Profile, Alumni Membership Plan, Alumni Membership, Alumni Donation Campaign, Alumni Donation, Alumni Committee, Alumni Committee Member, Alumni Job Post, Alumni Story, Alumni Notice.
**Steps:**
- Field mapping doc in `docs/migration/zaialumni-mapping.md`
- Idempotent: re-running the script does not create duplicates (uses `external_legacy_id` field on each migrated DocType)
- Dry-run mode: prints intended writes without executing
- Tests with a fixture export of 100 records
**Done:** ZaiAlumni customer can migrate with one shell command + 30 min of manual review.

---

---

## Phase 17 — SaaS Infrastructure (NEW v3)

> Per ADR-041, ADR-042, ADR-049 — domain provisioning, PWA, sharing/SEO. These are infrastructure-level features that can ship after the core app is functional but are needed before any production deployment goes live.

### `[ ] T-092 — Alumni Tenant Domain DocType + DNS verification flow` *(NEW v3, per ADR-041)*
**Outcome:** Admin adds a custom domain through the UI; system generates a `dns_token`, displays clear CNAME + TXT record instructions; hourly job verifies DNS; flips status to `DNS Verified` on success.
**Steps:**
- DocType `Alumni Tenant Domain` per SPEC §04
- Admin page `/alumni/admin/domains` with add-domain form
- DNS verification: `dnspython` queries the TXT record at `_alumni-verify.<domain>` and checks for `dns_token`; CNAME at `<domain>` points to `cname_target` (Settings.primary_domain)
- Scheduled job `tasks.verify_pending_domains()` (hourly) walks all domains with status=`Pending DNS` and verifies; marks `Failed` after 7 days of failed checks
- Email templates `alumni_domain_verification_pending`, `alumni_domain_verified`, `alumni_domain_verification_failed`
- Tests: happy path verification, missing TXT, wrong CNAME, expired pending state, multiple domains per site
**Done:** Admin completes DNS setup → within 1 hour their domain shows "DNS Verified".

### `[ ] T-093 — Let's Encrypt SSL provisioning + auto-renewal` *(NEW v3, per ADR-041)*
**Outcome:** When a domain reaches `DNS Verified`, the system requests a Let's Encrypt certificate via Frappe's `bench setup lets-encrypt` integration. On success, status flips to `Live`. Daily renewal job catches certs expiring within 30 days.
**Steps:**
- `tasks.provision_ssl_for(domain)` shells out to `bench setup lets-encrypt --domain <domain>` (via Frappe's existing helper)
- Status transitions: `DNS Verified → SSL Pending → Live` (or → `Failed` with reason)
- Custom certificate upload path: when `ssl_provider = Custom Upload`, admin uploads PEM + key; system validates the chain matches the domain
- Nginx vhost regenerated: `bench setup nginx` after each provision
- `tasks.renew_expiring_certs()` daily; pages SaaS operator on renewal failure
- `tasks.cleanup_expired_domains()` daily marks expired certs and 503s the vhost (better than serving stale certs)
- Tests: Let's Encrypt sandbox staging happy path; rate-limit handling; renewal trigger; custom cert validation
**Done:** Custom domain reaches `Live` status; HTTPS works; renewal exercised against Let's Encrypt staging.

### `[ ] T-094 — Wildcard subdomain auto-provisioning for SaaS signup` *(NEW v3, per ADR-041)*
**Outcome:** SaaS signup flow (or admin "create tenant" action) auto-creates a Frappe site at `<slug>.alumni-saas.com`, installs the alumni app, seeds Settings, and creates the corresponding `Alumni Tenant Domain` record.
**Steps:**
- Helper script `alumni/saas/provision_tenant.sh` (called from the v2 alumni_saas app or by ops directly): creates site, installs app, applies tenant config from a JSON file, sets first admin password
- Wildcard cert `*.alumni-saas.com` provisioned at infra layer (separate runbook in `docs/ops/wildcard-cert.md`)
- Tenant slug validation: lowercase, alphanumeric + hyphens, 3–32 chars, against a reserved-word list (admin, www, api, mail, alumni, saas, etc.)
- Tests with a fixture tenant JSON: provisions in <60s, alumni site reachable at `<slug>.alumni-saas.com`
**Done:** Ops runs `provision_tenant.sh new-tenant.json` and a working alumni site exists 60 seconds later.

### `[ ] T-095 — PWA: manifest, service worker, offline shell` *(NEW v3, per ADR-042)*
**Outcome:** Alumni portal is installable as a PWA. Manifest auto-generated per tenant (icons, theme color, background color from active theme + Settings). Service worker caches the app shell + last-viewed directory pages + own profile + recent messages for offline read access. Offline state shows a clear banner; write attempts queue and retry on reconnect.
**Steps:**
- `alumni/public/pwa/manifest.webmanifest` template — rendered server-side per tenant
- `alumni/public/pwa/service-worker.js` — Workbox-style caching strategies: networkFirst for API calls, cacheFirst for static assets, staleWhileRevalidate for own profile and directory
- Icons generated from `Alumni Settings.institution_logo` at 192×192, 512×512, maskable variants
- `tasks.regenerate_pwa_manifest_for(site)` — hooked to Settings + Theme save
- Offline banner component + write-queue (IndexedDB) for outgoing messages
- Lighthouse PWA score gate ≥90 in CI
**Done:** Mobile Chrome / Safari shows "Add to Home Screen" prompt after 3rd visit; installed app launches into the alumni shell; airplane-mode test still shows directory and profile.

### `[ ] T-096 — PWA: Web Push subscription + notification flow` *(NEW v3, per ADR-042)*
**Outcome:** After a user permits notifications, they receive Web Push notifications for new messages and event reminders. Subscription stored in `Alumni Profile.push_subscription` (encrypted). Unsubscribe respected.
**Steps:**
- VAPID keys generated per site at install (one-shot)
- Frontend: `Notification.requestPermission()` flow, register subscription via `pushManager.subscribe`, POST to `register_push_subscription`
- Backend: `register_push_subscription`, `unregister_push_subscription` whitelisted; storage encrypted via Frappe Password field
- Push send: `alumni.push.send(profile, payload)` using `pywebpush`; called from messaging adapter on new message + from event reminder job
- Notification body never contains message content — just "New message from [redacted name]" — content fetched on click
- Tests: subscription happy path, unsubscribe, send-after-unsubscribe (404 handling), TTL expiry, payload size limits
**Done:** A user with the PWA installed and notifications granted receives a push within 5 seconds of a peer messaging them.

### `[ ] T-097 — Profile completeness scoring + onboarding wizard` *(NEW v3, per ADR-044)*
**Outcome:** Every Alumni Profile has a live `profile_completeness_percent` (0–100). New `/alumni/welcome` flow walks new users through 6 high-leverage fields. Dashboard card nudges toward next missing field. Admin can edit completeness rules in Settings.
**Steps:**
- Compute function `alumni.utils.completeness.compute(profile)` — pure, takes profile + rules JSON, returns int + breakdown
- `before_save` hook recalculates on Profile save
- Dashboard widget "Complete your profile" with the ring + next 3 missing fields
- `/alumni/welcome` Vue flow: 6-step (photo / employer / city / bio / interests / mentor flag) with skip-per-step
- Admin Settings UI for editing weights — preview pane shows what % a sample profile scores under the new rules
- Optional gates: directory hides profiles below `directory_min_completeness`; messaging blocked for senders below `messaging_min_completeness` (soft warning)
- Tests: rule changes recompute scores via a job (not migration); breakdown explainable; edge cases (profile with all fields = 100%)
**Done:** New user lands on welcome flow after first login; completeness ring updates live as they fill fields; admin can adjust weights and see impact.

### `[ ] T-098 — Memorial Wall + bereavement workflow` *(NEW v3, per ADR-045)*
**Outcome:** Profiles with `status=Deceased` render a memorial page at `/alumni/memorial/<n>` with photo, dates, bio, photo gallery, and moderated tributes. Family members designated as `memorial_maintainers` can edit. Profile contact-data masking is permanently locked when status changes to Deceased.
**Steps:**
- Workflow: Active → Deceased (Admin-only, requires confirmation, audited)
- On transition: notify `family_contact_email` if set; freeze contact masking; switch profile to memorial template
- Public memorial page (Jinja, theme-tokenized)
- Tribute submission: alumni-only or guest with name (configurable); always moderated by Admin
- Maintainer permissions: can edit `bio`, `photo`, add gallery images, approve tributes
- Tests: status transition, masking lock, maintainer permission scope, tribute moderation flow
**Done:** Deceased profile renders correctly; tributes flow through moderation; maintainers can update; contact data permanently inaccessible to non-Admin viewers.

### `[ ] T-099 — Distinguished Alumni Awards + Hall of Fame` *(NEW v3, per ADR-045)*
**Outcome:** Admin defines award catalog; runs nomination cycles; selects recipients. Public Hall of Fame at `/alumni/hall-of-fame` filterable by award and year. Recipient profiles show permanent badges if award is configured for them.
**Steps:**
- DocTypes `Alumni Award` + `Alumni Award Recipient` per SPEC §04
- Nomination flow reuses Election Nomination pattern (peer-nominated, board-reviewed) when `selection_method = Peer Nomination + Board Review`
- Public Hall of Fame page with filters
- Profile badge: `recipient.award.confers_permanent_badge=1` → display tag in directory + profile detail
- Email templates: `alumni_award_announced`, `alumni_award_recipient_congratulations`
- Tests: award catalog management; recipient publication; badge display; nomination → review → publish flow
**Done:** Hall of Fame page live; awards searchable; badges render across directory and profile.

### `[ ] T-100 — Alumni Perks marketplace + digital member card` *(NEW v3, per ADR-046)*
**Outcome:** Alumni see curated perk feed at `/alumni/perks`. Can claim codes, click through URLs, or generate a member-card QR that partners scan to verify. Digital member card downloadable as PNG / PDF; optional Apple Wallet / Google Wallet pass.
**Steps:**
- DocTypes `Alumni Perk Category`, `Alumni Perk`, `Alumni Perk Redemption` per SPEC §04
- Public perk feed (alumni-only / member-only filter respected)
- Redemption flow per type: Code reveal page; URL click logs; QR scan endpoint `verify_member_card(token)`
- Member card generator: HTML → PDF via wkhtmltopdf; QR via `qrcode` (signed JWT with profile_id + expiry)
- PassKit + Google Wallet integration: opt-in; if not configured, downloadable PDF/PNG only
- Partner verification endpoint: returns `{name, passing_year, member_tier, expires_on}` — no PII
- Tests: each redemption type happy path; QR signature verify; expired card rejected; eligibility filters work
**Done:** Alumni can browse perks, redeem one of each type, generate and use a member card; partners can scan and verify.

### `[ ] T-101 — Job Referral system + Speaker Bureau` *(NEW v3, per ADR-047)*
**Outcome:** Job posters can offer referrals (`referral_offered=1`); applicants request referrals; referrers manage from their dashboard. Alumni can opt into `speaker_topics`; current students browse `/alumni/speakers` and submit requests.
**Steps:**
- DocTypes `Alumni Job Referral`, `Alumni Speaker Topic` (child), `Alumni Speaker Request` per SPEC §04
- Job Post UI: toggle for `referral_offered`; applicant flow gains "Request referral" button
- Referrer dashboard: queue of referral requests with Accept / Decline / Mark Submitted / Mark Hired actions
- Reputation: increment `referral_reputation_points` on Hired status
- Speaker Bureau page `/alumni/speakers` with topic / format / honorarium filters
- Speaker request form (logged-in alumni or via short-form for current students in school_connected mode)
- Auto-decline after `speaker_request_default_response_days`
- On Accept: auto-create Alumni Event Wrapper draft with the speaker as featured
- Tests: end-to-end referral state machine; reputation increment; speaker request → accept → event creation
**Done:** Both flows work end-to-end; reputation visible on profiles; speaker bureau searchable.

### `[ ] T-102 — Networking match suggestions` *(NEW v3, per ADR-048)*
**Outcome:** Dashboard widget shows 5 suggested alumni weekly. Users can mute matches.
**Steps:**
- Scoring function `alumni.utils.matching.score(viewer, candidate)` per ADR-048 weights
- DocType `Alumni Match Mute`
- Scheduled job `tasks.refresh_match_suggestions()` weekly per active alumni — caches top 20 in `Alumni Match Cache` (transient)
- API `get_match_suggestions_for(alumni)` returns top 5, excluding muted
- Dashboard widget (Vue) with "Connect" / "Not interested" actions
- `_explain_score(viewer, candidate)` exposed for admin debugging
- Tests: scoring deterministic; mute respected; cold-start (new alumni with no chapter, no city) gets cross-batch suggestions
**Done:** Widget populates within 24h of new profile; "Not interested" sticks across sessions; admin can explain any suggestion.

### `[ ] T-103 — SEO + Open Graph + JSON-LD + QR codes` *(NEW v3, per ADR-049)*
**Outcome:** Every public surface emits OG / Twitter Card / JSON-LD. WhatsApp / X / LinkedIn previews work. Lighthouse SEO ≥95. QR codes generated for events, member cards, candidates, profiles.
**Steps:**
- Template partial `seo_meta.html` consuming `seo_meta()` controller helper (returns dict: title, description, image, type, jsonld)
- Per-DocType controllers implement `seo_meta()`: Donation Campaign, Candidate, Event Wrapper, Alumni Story, News, Job Post, Award Recipient, public Profile
- JSON-LD types: Organization (institution), Person (alumni), Event (events), JobPosting (jobs), Article (stories/news)
- `robots.txt` template + `tasks.refresh_sitemap()` daily generates `sitemap.xml` from public DocTypes
- QR utility `alumni.utils.qr.generate(url, branding_color=None)` returns PNG bytes
- Privacy: alumni profile public URL is opt-in via `public_profile_slug`; `noindex` on private pages
- Tests: OG tags present and valid; JSON-LD parses with structured-data validator; sitemap excludes private DocTypes; Lighthouse SEO ≥95 on landing + public surfaces
**Done:** Sharing a candidate URL on WhatsApp shows photo + manifesto; donation campaign on LinkedIn shows progress + cover; events appear in Google for Jobs / events.

---

---

## Phase 18 — Digital Business Cards + WhatsApp Business + AI assistance (NEW v3)

> Per ADR-050 (vCards), ADR-051 (per-alumni custom domains), ADR-052 (WhatsApp click-to-chat + Business API), ADR-053 (admin-managed template registry), and ADR-054 (lessons applied from InfyVCardsSaas's 14-version history). This phase is a self-contained subsystem; can ship after Phase 17 once SaaS infrastructure is solid.

### `[ ] T-104 — AI adapter providers + PII allow-lists (scaffold lives in T-002)` *(NEW v3, per ADR-054 lesson #10)*
**Outcome:** `alumni.integrations.ai` already exists from T-002 (public surface stub + no-op `_fallback`). This ticket lands the **real driver implementations** (OpenAI, Anthropic, Bedrock, Custom HTTP) and the per-purpose **PII context allow-lists** in `alumni/integrations/ai/contexts.py`. AI is institution-opt-in; per-alumni token quotas enforced; generation logs written; PII-minimization filters in place.
**Steps:**
- Driver implementations under `alumni/integrations/ai_real/drivers/{openai,anthropic,bedrock,custom_http}.py` (scaffold module from T-002 stays; this fills it in)
- DocType `Alumni AI Generation Log` per SPEC §04
- Settings fields per SPEC §04 AI section
- Per-purpose `context` allow-lists in `ai/contexts.py` (one function per purpose returning the safe subset)
- Token quota checked via `frappe.cache().incr` against `Alumni Settings.ai_max_monthly_tokens_per_alumni`; reset by daily job on the 1st of each month
- Auto-purge job `tasks.purge_ai_generation_logs()` daily
- Tests: each driver mocked happy path; PII never crosses to the model (asserted by inspecting captured request payloads); quota enforcement; auto-purge correctness
**Done:** Institution flips `ai_enabled=1` + adds OpenAI credentials; alumni clicks "Help me write" on bio; gets a draft within 3s; generation log row exists; PII not in payload.

### `[ ] T-105 — VCard registry: 2 built-in templates + admin upload pipeline` *(NEW v3, per ADR-050 + ADR-053)*
**Outcome:** Two built-in templates ship (`classic-professional`, `modern-minimal`) and the admin upload pipeline accepts new templates via `.zip` upload with full validation.
**Steps:**
- Folder structure `alumni/vcard_templates/<id>/` with `template.json`, `card.html`, `card.css`, `preview.png`, `sample_data.json`
- DocType `Alumni VCard Template` per SPEC §04 (read-only, populated from disk)
- Two built-in templates designed: Classic Professional (formal, light + dark variants, alumni-association-branding-forward) and Modern Minimal (clean, image-led, mobile-first)
- Both built-ins fully RTL + dark-mode tested (per ADR-054 lessons #2 + #3)
- Install pipeline: `alumni.vcard.template_registry.install_from_zip(zip_bytes, uploader)` — quarantines unzip, runs validator, moves to live dir, creates record
- Validator covers (per ADR-053): manifest JSON Schema, Jinja sandbox compile, CSS allow-list scan (no `@import`, no `url(http)` external, no `expression()`), no JS files, file count ≤30, total size ≤10MB, no path traversal in zip
- Admin UI at `/alumni/admin/vcard-templates`: list installed (with version, author, preview, install/uninstall, "Times used" count), Upload Template button, drag-and-drop zone, preview-before-publish flow that renders `sample_data.json` against the template
- Documentation: `docs/templates/authoring-vcard-templates.md` + `docs/templates/template-anatomy.md` (variable reference, CSS allow-list, sanitization rules, RTL checklist, dark-mode checklist)
- Tests: built-in templates render correctly; valid zip installs; bad zips rejected with clear error messages (path traversal, JS file present, missing manifest, invalid Jinja, oversized, too many files); re-upload with higher version updates files; lower version refused
**Done:** Admin uploads a "Doctor" template zip → preview rendered → installs in 5s → alumni in the institution can pick it.

### `[ ] T-106 — Alumni VCard core schema + public render route` *(NEW v3, per ADR-050)*
**Outcome:** `Alumni VCard` DocType + 13 child / linked DocTypes + public route `/v/<slug>` rendering with the chosen template. Pre-fill on first save copies profile data so alumni only edit deltas. Custom CSS sanitizer in place.
**Steps:**
- All vCard DocTypes per SPEC §04 (Alumni VCard, Social Link, Service, Gallery Item, Gallery Category, Testimonial, Iframe, Business Hour, Custom Link, FAQ)
- Public Jinja route `/v/<slug>` → controller resolves `Alumni VCard` by `slug` + institution scope → loads template → renders with full context
- Slug validator: 3–48 chars, URL-safe, against `Alumni Settings.vcard_blocked_slugs` reserved list, unique per site
- Pre-fill on insert: `before_insert` hook copies `Alumni Profile.name → display_name`, `profile_photo → profile_photo`, `current_employer + designation → current_role`, `current_city → address`, `linkedin_url → social_links[platform=LinkedIn]`
- Custom CSS sanitizer: `bleach`-based allow-list (only `display`, `position`, `top/right/bottom/left`, `padding/margin`, `border`, `background-color`, `color`, `font-*`, `text-*`, etc.); rejected properties produce inline error feedback
- Section visibility toggles render only enabled sections; no DOM for disabled ones (smaller HTML payload)
- Theme tokens: vCard CSS uses the same `--color-*` variables as institution themes; `dynamic_accent_color` overrides `--color-accent` only for the vCard surface
- Tests: 18 cases covering slug uniqueness, reserved-slug rejection, pre-fill behavior, custom-CSS sanitization, section visibility, dark-mode rendering, RTL rendering
**Done:** Alumni creates a vCard, picks Classic Professional, edits bio, publishes; visiting `/v/ahmed-2018` renders the page in <500ms.

### `[ ] T-107 — VCard sections: Services, Gallery, Testimonials, Custom Links, FAQ, Iframes, Business Hours` *(NEW v3)*
**Outcome:** All non-monetized sections fully functional with admin-managed via the alumni's vCard editor. Image-cropper enforced on every image upload. Iframe URL allow-list enforced.
**Steps:**
- Editor UI (Vue) for each section with add/edit/delete/sort-order; Storybook stories per ADR-043
- Image cropper integration (per ADR-054 lesson #2) with declared aspect ratios per section: profile 1:1, cover 16:9, gallery 4:3 default, services-icon 1:1, testimonial-photo 1:1
- Iframe URL allow-list check at save time (against `Alumni Settings.vcard_iframe_allowlist_domains`); rejected URLs show clear error
- Lazy-loading for gallery items below the fold (per ADR-054 lesson #14 — Lighthouse perf budget)
- Lightbox for gallery images
- Tests: each section CRUD; image-crop client + server validation; iframe domain rejection; sort-order persistence
**Done:** Alumni adds 5 services + 12 gallery items + 3 testimonials + 4 custom links to their vCard; published page renders all of them with proper aspect ratios.

### `[ ] T-108 — VCard contact form (Inquiries) + antispam` *(NEW v3, per ADR-054 lesson #8)*
**Outcome:** Contact form on every published vCard. Submissions filtered against blocked email domains, blocked keywords (regex), honeypot, and minimum-time-on-page check. Spam auto-flagged. Alumni get notified per their preferences.
**Steps:**
- DocType `Alumni VCard Inquiry` per SPEC §04
- Public submit endpoint `submit_vcard_inquiry(vcard_slug, payload)` with rate limiter (5/min per IP; 3/min per email)
- Antispam pipeline: blocked domain check → blocked keyword regex check → honeypot field → min-seconds-on-page → captcha if 3 spam flags from same IP in 24h
- Notification: configurable per vCard (email + push); inquiry email template `alumni_vcard_new_inquiry`
- Admin moderation list view filterable by `is_spam`, `vcard_owner`, status
- IP-purge job: drops `submitted_ip` 90 days after submission (per ADR-054 lesson #8)
- Tests: spam vector tests (each blocked domain, each keyword pattern, fast-submit, missing honeypot, captcha trigger); legitimate submission flow; bulk moderation
**Done:** Spam attempt blocked; legitimate inquiry reaches alumni; alumni replies via the in-app composer.

### `[ ] T-109 — VCard appointments (free + paid via receivables adapter)` *(NEW v3)*
**Outcome:** Customers book appointments on a vCard; alumni approve/reject; payment (if required) flows through receivables adapter; calendar event optionally exported via communication adapter. Service-based booking supported (per InfyVCards v14.7.5).
**Steps:**
- DocType `Alumni VCard Appointment` per SPEC §04
- Booking widget: shows alumni's available slots from `business_hours` minus existing approved appointments minus configurable buffer; supports "Book by service" linking to a `Alumni VCard Service`
- Free path: submit → status=Pending → alumni approves → status=Approved → confirmation email sent
- Paid path: submit → invoice via receivables adapter → payment URL emailed → on payment-status=Paid + alumni-approval, status=Approved → confirmation
- ICS export: `Alumni VCard Appointment` controller generates `.ics` content; emailed to both customer and alumni
- Tests: free booking happy path; paid booking happy path; double-booking rejected; refund handling; alumni rejection flow
**Done:** Customer books a paid 30-minute appointment; pays via Stripe; alumni approves; both receive confirmation + ICS.

### `[ ] T-110 — VCard products + product orders + tax + receipts` *(NEW v3, per ADR-054 lesson #13)*
**Outcome:** Alumni list products on their vCard; customers buy; orders flow through receivables; tax breakdown computed; PDF receipt auto-generated.
**Steps:**
- DocTypes `Alumni VCard Product`, `Alumni VCard Product Image` (child of Product), `Alumni VCard Product Order` per SPEC §04
- Product editor with multi-image upload, stock management, tax fields, sort order, category
- Product browse + cart UI on vCard (cart in localStorage; submitted on checkout)
- Checkout: shipping address + payment method selector (limited to what `Alumni Settings` enabled gateways support); receivables adapter creates invoice with tax breakdown
- Order email templates: `alumni_vcard_order_placed_customer`, `alumni_vcard_order_placed_seller`, `alumni_vcard_order_status_update`
- PDF receipt via certificates adapter; includes seller's institution-signed badge ("Verified alumni of [Institution]")
- Order admin: status workflow Placed → Confirmed → Processing → Shipped → Delivered + tracking number
- Refund flow: alumni initiates refund through receivables adapter; order moves to Refunded
- Tests: cart correctness; tax breakdown matches receivables; out-of-stock rejection; refund flow; multi-image product
**Done:** Customer buys a 2-item order with 15% VAT; pays Stripe-test; receipt PDF arrives showing tax breakdown; alumni marks as Shipped with a tracking number.

### `[ ] T-111 — WhatsApp click-to-chat (tier a) + analytics tracking` *(NEW v3, per ADR-052)*
**Outcome:** Every vCard with a `whatsapp_number` set renders a WhatsApp button that opens `wa.me/<number>?text=<encoded_pre_filled_message>`. Clicks tracked; conversion shown in vCard analytics.
**Steps:**
- WhatsApp button component (Vue + theme-tokenized) used by vCard render
- Pre-fill: `Alumni VCard.whatsapp_business_message` rendered through Jinja with `{{ vcard.display_name }}`, `{{ vcard.slug }}`
- Click tracking: `track_vcard_event(slug, event)` — increments `Alumni VCard Visit.whatsapp_click_count` for the day
- Privacy: WhatsApp number masked in directory listings unless explicitly published (per ADR-052)
- Tests: button renders correctly; pre-fill encoding; click increments counter; click does NOT identify the visitor (privacy)
**Done:** Customer taps WhatsApp button → WhatsApp opens with pre-filled message → analytics show 1 click for the day.

### `[ ] T-112 — WhatsApp Business catalog sync (tier b)` *(NEW v3, per ADR-052)*
**Outcome:** Alumni who run a WhatsApp Business account can sync their vCard products + services to a WhatsApp Business catalog. Sync uses the institution's `Alumni Communication Channel` (channel_type=WhatsApp). Behind feature flag `whatsapp_business_integration_enabled`.
**Steps:**
- `whatsapp_catalog_sync_enabled` toggle on Alumni VCard
- Sync function: posts each product + service to Meta WhatsApp Business catalog API via the configured channel's auth credentials
- DocType `Alumni VCard WhatsApp Catalog Sync Log` per SPEC §04
- Frequency: Manual / Hourly / Daily per `Alumni Settings.whatsapp_catalog_sync_frequency`
- Inbound message handling: replies to vCard WhatsApp number reach the alumni's vCard inbox (NOT the internal Alumni Message Thread system per ADR-052 — different audiences)
- Documentation: `docs/integrations/whatsapp-business-setup.md` (Meta verification checklist, phone number provisioning, business profile API, troubleshooting)
- Tests: sync happy path against Meta sandbox; partial failure (1 of 5 products fails) yields status=Partial with the right error_summary; rate-limit handling; concurrent-sync deduplication
**Done:** Alumni syncs 3 products + 2 services → catalog visible in their WhatsApp Business → catalog_sync_log shows Success.

### `[ ] T-113 — WhatsApp Store template registry + 1 built-in template` *(NEW v3, per ADR-053)*
**Outcome:** WhatsApp Store templates are admin-uploadable (same registry pattern as vCard templates). One built-in: "Standard Storefront". `enable_whatsapp_store=1` on the vCard renders the products section using the chosen WhatsApp Store template.
**Steps:**
- Folder structure `alumni/whatsapp_templates/<id>/`
- DocType `Alumni WhatsApp Store Template` per SPEC §04
- Built-in template: Standard Storefront (clean grid, sticky cart, theme-tokenized)
- Same admin upload pipeline as T-105 (validator, preview, install)
- WhatsApp Store rendering integrated into vCard render — when `enable_whatsapp_store=1`, products section uses the WhatsApp Store template instead of the default products section
- Tests: built-in renders; admin upload pipeline reused; conflict detection (a vCard template embedding products vs a WhatsApp Store template covering products — only one rendered)
**Done:** Built-in Standard Storefront ships; admin uploads a Restaurant Store template; alumni picks it; vCard renders with the new look.

### `[ ] T-114 — Per-alumni custom domain support` *(NEW v3, per ADR-051)*
**Outcome:** Alumni at eligible Member tier can attach their own custom domain (e.g., `dr-sara-cardiology.com`) to their vCard. Same DNS verification + Let's Encrypt SSL flow as institution domains (T-092, T-093). Membership lapse triggers configurable grace period before domain breaks.
**Steps:**
- Extend `Alumni Tenant Domain` with `domain_scope` (Institution / Alumni VCard) and `target_vcard` fields
- Eligibility check: `Alumni Settings.alumni_custom_domains_enabled = 1` AND alumni's active Membership tier in `Alumni Settings.alumni_custom_domain_eligible_tiers`
- Public alumni-facing UI at `/alumni/me/vcard/domain`: walk through DNS setup with copy-able CNAME + TXT values
- Reuse `tasks.verify_pending_domains()` and `tasks.provision_ssl_for(domain)` (no new background jobs needed)
- Nginx vhost regeneration adds one server block per registered alumni custom domain; routing by Host header
- Membership lapse: `tasks.handle_lapsed_member_domains()` daily; configurable grace period (default 30 days) before domain returns 404 / branded "membership expired" page; SSL keeps renewing through grace period
- Institution admin panel: "Alumni Custom Domains" list view aggregating all alumni domains (no edit access — read-only)
- Audit log on every alumni-domain registration / deletion / lapse-break
- Tests: alumni adds domain → verifies → SSL → live; membership lapse triggers grace; renew restores; admin panel listing
**Done:** Alumni adds `dr-sara-cardiology.com` → DNS verified within 1 hour → SSL provisioned → vCard live at custom domain. Lapsed membership shows graceful message on day 31.

### `[ ] T-115 — VCard analytics dashboard + view-limit enforcement` *(NEW v3, per ADR-054 lesson #7)*
**Outcome:** Alumni see vCard analytics: views (today / 7d / 30d / all), unique views, WhatsApp clicks, contact-add count, inquiry count, appointment count, top countries, top referrers. Per-tier view limits enforced; over-limit shows branded "limit reached" page.
**Steps:**
- Aggregation worker: `tasks.aggregate_vcard_visits()` rolls up raw events from cache to `Alumni VCard Visit` daily
- Analytics page (Vue) — Chart.js charts; date-range filter; export to CSV
- View limit enforcement: `Alumni VCard.monthly_view_count` checked on every render against `Alumni VCard.monthly_view_limit`; over-limit shows branded "Monthly view limit reached — please come back next month, or alumni can upgrade their plan inline" page
- Monthly reset job `tasks.reset_monthly_vcard_views()` on the 1st of each month
- Storage usage dashboard per alumni: shows breakdown (gallery / products / cover / profile) + total used / quota
- Tests: aggregation correctness; chart accuracy; view-limit enforcement at exact threshold; reset on month boundary
**Done:** Alumni sees their dashboard showing 1247 views this month, 18 WhatsApp clicks, 3 inquiries.

### `[ ] T-116 — Alumni Business Directory + AI bio drafting + bulk operations` *(NEW v3, per ADR-054 lessons #9, #10, #11)*
**Outcome:** Three smaller features bundled. (a) Public `/alumni/businesses` page lists alumni-owned businesses with published vCards, filterable by industry / city / passing year; SEO-indexed (per ADR-049). (b) "Help me write" AI button on bio composer + section description composer + story draft (uses `ai.draft`). (c) Bulk operations on every admin list view: bulk approve, bulk delete (with double-confirm), bulk export CSV, bulk message (creates an Alumni Broadcast pre-populated with the selection).
**Steps:**
- Public Business Directory: filter UI + SEO meta + JSON-LD per ADR-049; only shows vCards where `Alumni Profile.is_alumni_owned_business_owner=1` AND `Alumni VCard.is_published=1` AND `Alumni VCard.disable_indexing=0`
- AI bio composer: button next to bio field calls `ai.draft(purpose='bio_draft', context=bio_context(profile))`; streams result to UI; user accepts / regenerates / discards; `mark_accepted` / `mark_discarded` called accordingly
- Bulk operations: Frappe ListView Action override on every admin list view (Alumni Profile, Alumni Donation, Alumni Story, Alumni VCard, etc.) — admin-configurable which actions per role
- Bulk message creates Alumni Broadcast in Draft status with `segment_type=Custom List` and the selected names pre-populated
- Tests: business directory SEO + filters; AI draft happy + quota-exceeded paths; bulk-delete double-confirm; bulk-broadcast creation
**Done:** Business Directory crawlable; AI button drafts a bio in 3s; admin bulk-deletes 30 spam profiles in one click.

---

## Phase index — what's in each phase after v3

| Phase | Tickets | Theme |
|---|---|---|
| 0 — Foundation | T-001 → T-005 | Scaffold, adapters, Settings, themes (LTR + RTL) |
| 1 — Identity | T-006 → T-011, T-062, T-063, T-064, T-065, T-066, **T-097** | Profile + verification + 2FA + social login + completeness scoring |
| 2 — Directory & Social | T-012 → T-015, T-067, T-068, T-069 | Directory, posts, taxonomies, **messaging** |
| 3 — Money | T-016 → T-020 | Receivables + payments wiring |
| 4 — Membership | T-021, T-022 | Plans + renewals |
| 5 — Events | T-023 → T-029 | Buzz wrapper |
| 6 — Donations | T-030, T-070, T-071, T-072, T-031, T-032 | Campaigns + categories + guest + comments + matching |
| 7 — Jobs & Volunteering | T-033, T-034, **T-101** | Jobs + Volunteering + **Referrals + Speaker Bureau** |
| 8 — Network features | T-035, T-036, T-037, **T-098, T-099, T-102** | Q&A, Chapters, Reunions + **Memorial Wall + Hall of Fame + Match Suggestions** |
| 9 — Mentorship | T-038, T-039 | |
| 10 — Outcomes | T-040 | |
| 11 — Comms | T-041, T-042, T-043, T-088, T-089, T-090, **T-091** | Newsletter + 29 templates + push + multi-channel SMS/WhatsApp + broadcast + **Aurora dark theme + design system** |
| 12 — Public site | T-044, T-045, T-073, T-074, T-046, T-047, T-075, **T-100** | Builder + CMS DocTypes + multilingual + multi-site runbook + **Perks + Member Card** |
| 13 — Analytics | T-048, T-049, T-076, T-050 | 10 dashboards |
| 14 — **Committees & Elections (NEW)** | T-077 → T-084 | Full election subsystem |
| 15 — Hardening | T-051 → T-058, T-085, T-086 | Privacy + rate limit + a11y + integrity |
| 16 — Release | T-059, T-060, T-061, T-087 | Docs + tag + demo + migration |
| 17 — **SaaS Infrastructure (NEW)** | T-092 → T-096, T-103 | Domain provisioning + SSL + subdomain auto + PWA + push + SEO/QR |
| 18 — **vCards + WhatsApp Business + AI (NEW)** | T-104 → T-116 | AI adapter + vCard registry + 2 built-in templates + admin upload pipeline + sections + appointments + products + WhatsApp click-to-chat + WhatsApp Business catalog + per-alumni custom domain + analytics + business directory + bulk ops |

---

## Total

**116 tickets** (was 61 in v2). Roughly 32–38 weeks for one full-time Frappe dev with Claude Code + the OpenAEC skill package + a part-time Vue dev + a part-time designer (for design system + 2 default vCard templates) + a part-time DevOps for the SaaS infrastructure.

The v3 additions (55 new tickets) break down as:
- Identity uplifts (verification, 2FA, social, multilingual): 5 tickets (T-062 → T-066)
- Messaging: 3 tickets (T-067 → T-069)
- Donation upgrades: 3 tickets (T-070 → T-072)
- Site CMS + multilingual + multi-site: 3 tickets (T-073 → T-075)
- v3 dashboards: 1 ticket (T-076)
- Elections: 8 tickets (T-077 → T-084) — the heaviest area
- Hardening + integrity: 2 tickets (T-085, T-086)
- Migration: 1 ticket (T-087)
- Multi-channel SMS / WhatsApp + Broadcast: 3 tickets (T-088 → T-090) — per ADR-040
- Aurora dark theme + design system: 1 ticket (T-091) — per ADR-043
- SaaS infrastructure (custom domain, SSL, subdomain auto, PWA, push, SEO/QR): 6 tickets (T-092 → T-096, T-103) — per ADR-041, ADR-042, ADR-049
- Profile completeness + onboarding: 1 ticket (T-097) — per ADR-044
- Memorial Wall + Hall of Fame: 2 tickets (T-098, T-099) — per ADR-045
- Perks marketplace + member card: 1 ticket (T-100) — per ADR-046
- Job Referrals + Speaker Bureau: 1 ticket (T-101) — per ADR-047
- Networking match suggestions: 1 ticket (T-102) — per ADR-048
- **Digital Business Cards + WhatsApp Business + AI: 13 tickets (T-104 → T-116) — per ADR-050, ADR-051, ADR-052, ADR-053, ADR-054**

Plus expanded scope on existing tickets — no new ticket numbers but updated **Outcome / Done** lines.

**Cost savings vs hand-built:**
- ~6 weeks saved by using Buzz instead of building Event / Ticket Type / Booking ourselves (ADR-025)
- ~3 weeks saved by using Frappe core for OAuth, TOTP, translations, multi-site (ADRs 035–038)
- ~2 weeks saved by using socketio for messaging instead of Pusher / external broker (ADR-031)
- ~2 weeks saved by making SMS/WhatsApp providers configurable instead of bundling one (ADR-040)
- ~3 weeks saved by leaning on Frappe's Let's Encrypt + multi-site infrastructure for custom domains (ADR-041)
- ~4 weeks saved by shipping a PWA instead of native iOS / Android wrappers (ADR-042)
- ~6 weeks saved by deterministic match scoring instead of an ML pipeline (ADR-048)
- **~10 weeks saved by shipping only 2 vCard templates and making the rest admin-uploadable, vs InfyVCardsSaas's 40+ baked-in templates over 14 versions (ADR-053)**
- **~4 weeks saved by applying lessons from InfyVCardsSaas's 14-version history up-front (storage quota, image cropper, RTL, custom-JS-banned, recovery codes, antispam, bulk ops) — features they had to add late (ADR-054)**
