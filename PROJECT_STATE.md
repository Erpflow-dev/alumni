# PROJECT_STATE.md

> Update weekly. Paste into Claude Code at the start of every session along with `CLAUDE.md`.

## This week (auto-update)
- **Week of:** 2026-04-27
- **Current phase:** Phase 0 — Foundation (planning complete; scaffold not yet started)
- **Active ticket(s):** T-001 Repo scaffold (queued, not started)

## Last week's progress
_Bullet what shipped. Use commit hashes._
- **Spec bumped to v3** (final revision Apr 2026) after a feature-parity review against ZaiAlumni, several incumbent alumni products, and InfyVCardsSaas's 14-version history. Added 24 new ADRs (031–054), ~72 new DocTypes (33 → ~105), 55 new build tickets (T-062 → T-116) across 3 new phases (14 Elections, 17 SaaS Infra, 18 vCards/WhatsApp/AI), 3 new adapters (messaging, verification, ai — bringing total to 12), 1 new role (Alumni Board Member), 14 new email templates (29 total), 3 new dashboards, 12 built-in SMS / WhatsApp provider drivers + Custom HTTP, 4th theme (Aurora dark mode), full PWA support, custom domain + per-alumni custom domain auto-provisioning with Let's Encrypt SSL, Memorial Wall, Distinguished Alumni Awards, Perks marketplace + digital member card, Job Referrals, Speaker Bureau, Networking match suggestions, profile completeness scoring, SEO + Open Graph + JSON-LD + QR codes, **per-alumni vCards (2 built-in templates + admin-uploadable registry), WhatsApp click-to-chat + Business catalog sync, AI bio drafting opt-in, Alumni Business Directory, antispam settings, bulk admin ops, recovery codes**, and a new top-level `DESIGN_SYSTEM.md` doc.
- All 11 root docs updated to v3: SPEC.md, DECISIONS.md, INTEGRATIONS.md, BUILD_TICKETS.md, README.md, CLAUDE.md, CHANGELOG.md, PROJECT_STATE.md, THEMES.md. CLAUDE_CODE_SETUP.md unchanged (still applies).

## Blockers
_What's stuck and who is unstuck-ing it._
- (none)

## Decisions made this week
_New ADRs filed in DECISIONS.md._
- ADR-031 — Private 1:1 messaging built-in via Frappe socketio
- ADR-032 — Document-based registration verification
- ADR-033 — Election system as first-class feature, not optional add-on
- ADR-034 — Donation system: categories + comments + guest donations
- ADR-035 — Multi-tenancy via Frappe multi-site; SaaS billing → v2 companion app
- ADR-036 — 2FA mandatory for Admin/Board roles, optional for Alumni
- ADR-037 — Social login via Frappe OAuth Provider
- ADR-038 — Multilingual + RTL support enabled by default
- ADR-039 — Email verification mandatory; phone OTP optional
- ADR-040 — Pluggable SMS / WhatsApp channels with segmented broadcast (12 built-in providers + Custom HTTP)
- ADR-041 — Custom domain + subdomain auto-provisioning with Let's Encrypt SSL automation
- ADR-042 — Progressive Web App (PWA) first; service worker + offline + Web Push; native wrappers deferred
- ADR-043 — Dark mode shipped as fourth theme (Aurora) + DESIGN_SYSTEM.md published
- ADR-044 — Profile completeness scoring + guided onboarding (admin-configurable rules)
- ADR-045 — Memorial Wall + Distinguished Alumni Awards + Hall of Fame as first-class features
- ADR-046 — Alumni Perks marketplace + digital member card with QR (Apple Wallet / Google Wallet optional)
- ADR-047 — Job Referral system + Speaker Bureau as opt-in alumni capabilities
- ADR-048 — Networking match suggestions: deterministic scoring, no ML in v1
- ADR-049 — SEO + Open Graph + JSON-LD + QR codes for shareable surfaces
- ADR-050 — Per-Alumni vCard / Digital Business Card builder (Frappe-native, alumni-tuned, institution-signed)
- ADR-051 — Per-alumni custom domain support (extension of ADR-041 — Members can attach `their-name.com` to their vCard)
- ADR-052 — WhatsApp Business integration: click-to-chat (tier a, v1) + Business API catalog sync (tier b, behind feature flag)
- ADR-053 — Admin-managed vCard / WhatsApp template registry (template marketplace pattern; ships 2 vCard + 1 WhatsApp templates; admin uploads more)
- ADR-054 — Lessons applied from InfyVCardsSaas's 14-version history (storage quotas, image cropper, RTL day-1, no JS, custom-domain state machine, recovery codes, view limits, antispam, bulk ops, AI bio drafting, business directory, WhatsApp Store as vCard section, tax fields day-1, iOS PWA tested day-1, locale CI tests)

## Risks tracked
_From SPEC and DECISIONS, plus emergent._
- **Vote integrity** is the highest-risk surface area in v3. Plan: T-085 election integrity test suite covers the seven canonical attack scenarios; DB unique index on `(election, position, voter)` defends against double-voting at storage layer.
- **Messaging at scale**: realtime socketio fine for institutions ≤5K alumni; over that, watch for Frappe socketio worker contention. Plan: T-057 load test verifies p95 < 300ms with 100 concurrent users; if larger institutions adopt, the messaging adapter `_real` can swap in Raven later.
- **Translation maintenance**: shipping 8 languages means 8 .csv files to keep current. Plan: only top-200 priority strings translated initially; non-translated strings fall back to English. Community-contribution workflow documented in T-074 wrap-up.
- **Standalone-mode receivables**: needs to handle multi-currency cleanly. Watching.
- **Frappe Meet still alpha** — staying on Jitsi via fallback for v1.
- **bKash / HyperPay / Moyasar** may not be in `frappe/payments` yet — may need to contribute upstream.

## Next 3 tickets
1. T-001 — Repo scaffold
2. T-002 — Adapter Layer skeleton (now includes messaging + verification adapters)
3. T-003 — CI guard for cross-app imports

## Outstanding questions
_Stuff to ask the team or research._
- Confirm payment provider priorities for first release. (Suggested order: Manual → Stripe → Razorpay → bKash → HyperPay → Moyasar.)
- Confirm whether v1 ships election system **enabled** or **disabled** by default. Current default: `enable_elections = 0` — institutions opt in when ready.
- Confirm phone OTP provider: Twilio? Or rely on whatever the institution already wires through `communication_real`?
- For the v2 companion `alumni_saas`: does pricing need to model per-alumni, per-feature, or hybrid? Defer until v2 work begins.
