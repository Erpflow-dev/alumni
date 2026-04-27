# Changelog

All notable changes to the Alumni app are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Added — Spec v3 (Apr 2026, feature-parity review against ZaiAlumni)

**Identity & Security**
- ADR-032 — Document-based registration verification (transcripts, IDs, degree certs uploaded; admin queue review).
- ADR-039 — Email verification mandatory on self-registration; phone OTP optional via the communication adapter.
- ADR-036 — Two-factor authentication (TOTP) mandatory for Admin / Alumni Board Member / System Manager; soft-prompted for Alumni.
- ADR-037 — Social login through Frappe core OAuth: Google, Facebook, LinkedIn, Apple, Microsoft.
- New role: **Alumni Board Member** (election oversight; reviews nominations, audits votes, publishes results).
- New child DocType: **Alumni Verification Document**.

**Communication**
- ADR-031 — Built-in private 1:1 messaging powered by Frappe socketio (no external broker).
- New DocTypes: **Alumni Message Thread**, **Alumni Message**, **Alumni Message Read Receipt** (child).
- New adapter `alumni.integrations.messaging` with fallback (built-in storage) and a `_real` slot reserved for a future Raven backend.
- Recipient-controlled inbound preferences (All / Same Batch / Mentees Only / Off), block list, report-and-moderate flow.

**Governance & Engagement**
- ADR-033 — Full election system as a first-class feature.
- 12 new DocTypes: **Alumni Committee Category**, **Alumni Committee Designation**, **Alumni Election**, **Alumni Election Position** (child), **Alumni Election Symbol**, **Alumni Nomination**, **Alumni Candidate**, **Alumni Candidate Comment**, **Alumni Vote** (UUID autoname, audited), **Alumni Election Result** (child) — plus the existing Committee + Committee Member upgraded with v3 fields.
- Election state machine: Draft → Nomination Open → Nomination Closed → Voting Open → Voting Closed → Results Published.
- Optional Board-Member vote audit before counting (configurable per election).
- Auto-create elected Committee on results publication.

**Donations**
- ADR-034 — Donation Categories taxonomy, public moderated comments on campaigns, and **guest donations** (non-registered visitors with tax receipts emailed).
- New DocTypes: **Alumni Donation Category**, **Alumni Campaign Comment**.
- New whitelisted public endpoint `donate_as_guest`.

**Public site & Localization**
- ADR-038 — Multilingual + RTL by default. Ships translations for English, Arabic (RTL), Hindi, Bengali, Spanish, Portuguese, French, Indonesian.
- New theme metadata field `supports_rtl` validated by the theme validator.
- New site-CMS DocTypes: **Alumni FAQ**, **Alumni Testimonial**, **Alumni Image Gallery Item**, **Alumni Hero Banner** — for non-developer maintenance of the public site.
- News and Notices gain Categories + Tags; Stories gain Categories.

**Operations**
- ADR-035 — Multi-tenancy via Frappe native multi-site (one bench, many institutions, true data isolation). SaaS billing / super-admin / domain provisioning deferred to v2 companion app `alumni_saas`.
- ADR-040 — Pluggable SMS / WhatsApp channels with segmented broadcast. Twelve built-in provider drivers (Twilio, Twilio WhatsApp, MessageBird, Vonage, Plivo, Africa's Talking, Wati, Gupshup, 360Dialog, Unifonic, MSG91, SSL Wireless) plus Custom HTTP for any JSON-API gateway.
- ADR-041 — Custom domain + subdomain auto-provisioning. New DocType `Alumni Tenant Domain` handles DNS verification, Let's Encrypt SSL, auto-renewal. Single-tenant and SaaS deployments share the same flow.
- New DocTypes: **Alumni Communication Channel**, **Alumni Broadcast**, **Alumni Broadcast Log Entry** (child), **Alumni Tenant Domain**.
- Broadcast targeting: All Active / Chapter / Reunion Group / Committee / Class / Department / Membership Tier / Custom List / Election Eligible Voters — with min/max passing year + country filter overlays.
- Multi-site SaaS deployment runbook in `docs/ops/multi-site-saas.md`.
- Three new dashboards: **Messaging Health**, **Election Participation**, **Verification Pipeline** (total dashboards now 10) plus a Broadcast/cost dashboard via T-090.
- Audit log expanded with new event types: `vote_cast`, `nomination_approved`, `nomination_rejected`, `message_reported`, `verification_decided`, `guest_donation_received`, `broadcast_sent`, `sms_sent`, `whatsapp_sent`, `domain_verified`, `ssl_renewed`, `award_published`, `memorial_status_set`.
- ZaiAlumni → Alumni migration script (`alumni/migration/from_zaialumni.py`) with idempotent re-runs and dry-run mode.

**Frontend & Mobile**
- ADR-042 — Progressive Web App (PWA) with service worker, offline shell, Web Push notifications, installable on mobile + desktop. Native iOS/Android wrappers deferred.
- ADR-043 — Fourth default theme **Aurora** (dark mode) bringing total to 4 themes (Heritage, Modern, Bold, Aurora). New `DESIGN_SYSTEM.md` documents the full component vocabulary, motion guidelines, accessibility floor, performance budgets, and white-labeling rules. Storybook seeded for all components × 4 themes × LTR/RTL.
- ADR-044 — Profile completeness scoring with admin-configurable weighted rules + guided 6-step onboarding wizard. Optional gates for directory listing and messaging.
- ADR-049 — SEO + Open Graph + JSON-LD on every public surface; Lighthouse SEO ≥95 in CI; QR codes throughout (member cards, event tickets, candidate ballots, profile share, perk redemption); auto-generated sitemap + robots.txt.

**Recognition & Member Value**
- ADR-045 — **Memorial Wall** for deceased alumni with moderated tributes, family-designated maintainers, permanent privacy lock; **Distinguished Alumni Awards** with peer nominations and Hall of Fame; permanent profile badges for award recipients.
- ADR-046 — **Alumni Perks marketplace** (partner discounts, alumni-owned business listings) + **digital member card** with QR code, downloadable as PDF/PNG or to Apple Wallet / Google Wallet; minimal-PII partner verification endpoint.
- New DocTypes: **Alumni Memorial Tribute**, **Alumni Memorial Maintainer** (children of Profile), **Alumni Award**, **Alumni Award Recipient**, **Alumni Perk Category**, **Alumni Perk**, **Alumni Perk Redemption**.

**Career & Discovery**
- ADR-047 — **Job Referral system** layered on Job Posts (alumni offer to refer applicants; reputation points on hires) + **Speaker Bureau** (alumni opt in with topics, students/admin request talks, auto-creates Event on accept).
- ADR-048 — **Networking match suggestions** on dashboard; deterministic scoring (chapter + batch + city + country + industry + interests overlap + activity); "Not interested" mute; admin-explainable scoring for transparency.
- New DocTypes: **Alumni Job Referral**, **Alumni Speaker Topic** (child of Profile), **Alumni Speaker Request**, **Alumni Match Mute**.

**Digital Business Cards + WhatsApp Business + AI**
- ADR-050 — **Per-Alumni vCard / Digital Business Card builder** at `/v/<slug>` with 14 supporting DocTypes (sections, gallery, testimonials, business hours, custom links, FAQ, iframes, inquiries, appointments, products, product orders, visit analytics, plus the catalog sync log). Pre-fills from Profile so alumni don't re-enter data. Custom CSS sanitized; custom JS forbidden.
- ADR-051 — **Per-alumni custom domain** (e.g., `dr-sara-cardiology.com`) gated to active Members; same DNS verification + Let's Encrypt SSL flow as institution domains; configurable grace period when membership lapses.
- ADR-052 — **WhatsApp Business integration**: tier-a click-to-chat (one-tap pre-filled messages with click analytics) + tier-b WhatsApp Business catalog sync (vCard products + services pushed to Meta's catalog API via the existing communication channels).
- ADR-053 — **Admin-managed template registry** (template marketplace pattern). v1 ships **2** built-in vCard templates (Classic Professional, Modern Minimal) + **1** built-in WhatsApp Store template (Standard Storefront). All other templates uploaded by admin as portable `.zip` packages with full validation (manifest, Jinja sandbox compile, CSS allow-list, no JS, file caps). No code release needed for new templates.
- ADR-054 — **Lessons applied from InfyVCardsSaas's 14-version history** consolidated into v1 design choices: storage quotas from day 1, image cropper at upload, RTL forever-tax avoided, custom JS permanently out of scope, custom domain DNS state machine explicit, 2FA + recovery codes, visitor view limits as tier feature, blocked-email-domain antispam, bulk admin operations, AI bio drafting, public Alumni Business Directory, WhatsApp Store as a vCard section (not separate), tax fields on every monetizable surface, PWA tested on iOS Safari, locale + RTL number direction tested in CI.
- New adapter: `alumni.integrations.ai` with drivers for OpenAI, Anthropic, Bedrock, Custom HTTP. Strict PII minimization (allow-list contexts per purpose), per-alumni token quotas, prompt hashing, output not stored, auto-purge.
- New DocTypes (15): **Alumni VCard**, **Alumni VCard Template**, **Alumni WhatsApp Store Template**, **Alumni VCard Social Link**, **Alumni VCard Service**, **Alumni VCard Gallery Item**, **Alumni VCard Gallery Category**, **Alumni VCard Testimonial**, **Alumni VCard Iframe**, **Alumni VCard Business Hour**, **Alumni VCard Custom Link**, **Alumni VCard FAQ**, **Alumni VCard Inquiry**, **Alumni VCard Appointment**, **Alumni VCard Product**, **Alumni VCard Product Order**, **Alumni VCard Visit**, **Alumni VCard WhatsApp Catalog Sync Log**, **Alumni AI Generation Log**.

### Changed
- DocType count: 33 → ~103 first-class DocTypes.
- ADR count: 30 → 54.
- Build ticket count: 61 → 116 (interleaved across 19 phases; new Phases: 14 Committees & Elections, 17 SaaS Infrastructure, 18 vCards + WhatsApp + AI).
- Theme count: 3 → 4 (added Aurora dark mode per ADR-043). Plus a separate **vCard template registry** with 2 built-in vCard templates and 1 built-in WhatsApp Store template; admin uploads any number more.
- New top-level doc `DESIGN_SYSTEM.md` published as authoritative for frontend tickets.
- New adapter: `alumni.integrations.ai` (12 adapters total now).
- Email template fixture expanded from 15 to 28 templates (verification × 4, elections × 5, donations × 2, messaging × 2).
- `Alumni Profile` schema gains: `verification_documents` table, `verification_status`, `email_verified` / `email_verified_on`, `phone_verified`, `messaging_preference`, `2fa_enabled` (mirror), `social_login_provider`, `preferred_language`.
- `Alumni Settings` gains four new sections: Verification & Security, Messaging, Election, plus multilingual fields (`default_language`, `enabled_languages`).
- `Alumni Donation` gains `is_guest`, `guest_name`, `guest_email`. `Alumni Donation Campaign` gains `category`, `allow_guest_donations`, `allow_comments`.
- Alumni lifecycle gets two pending substates: `Pending Email` and `Pending Docs`, between `Draft` and `Active`.
- Profile permission/serializer rules: PII redaction extends to vote.voter, message thread access, and guest donor email.

### Deprecated
- (none)

### Removed
- (none)

### Fixed
- (none)

### Security
- v3 spec adds DB-level vote uniqueness (election, position, voter), rate-limited public endpoints (`donate_as_guest`, `request_email_verification`, `request_phone_otp`, `submit_nomination`, `cast_vote`), and messaging spam controls (≤30 msgs/min/sender, attachment MIME-sniff, body XSS sanitization).
- 2FA gating middleware blocks Admin / Board write operations until TOTP is enrolled when `mandatory_2fa_for_admin = 1`.

---

## [Unreleased — initial scaffold]

### Added
- (project initialized — no changes yet)
