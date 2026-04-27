# DECISIONS.md — alumni

ADRs in append-only order. Once accepted, never edit — supersede with a new ADR.

---

## ADR-001 — Standalone Frappe app, not a coupled module
**Status:** accepted
**Decision:** Build as a standalone, distributable Frappe app that runs on any Frappe site. Two install modes: School-Connected and Standalone.
**Why:** Maximum reach. Schools, colleges, institutes, training academies all benefit. Coupling would cap the audience to schools that already run Frappe Education + ERPNext.

---

## ADR-002 — Adapter Layer is the only place cross-app imports live
**Status:** accepted
**Decision:** All references to other apps' DocTypes live in `alumni/integrations/<area>_real.py`. App code imports only from `alumni/integrations/<area>.py` (the public surface). Selector in `__init__.py` swaps between `_real` and `_fallback` based on `frappe.get_installed_apps()` and Alumni Settings.
**Why:** Standalone mode breaks the moment a stray import leaks. CI gate enforces.

---

## ADR-003 — Insights is never required
**Status:** accepted
**Decision:** Analytics rendered inside the app with Chart.js. If Insights is installed, an "Open in Insights" link is shown alongside the in-app charts.

---

## ADR-004 — Receivables fallback uses two new lightweight DocTypes
**Status:** accepted
**Decision:** When ERPNext is not installed, the app uses internal DocTypes `Alumni Invoice` and `Alumni Payment`. Same fields semantically, no double-entry accounting, no Items, no Customers — just record-keeping.

---

## ADR-005 — Education fallback uses an internal "Past Student" stub
**Status:** accepted
**Decision:** Standalone mode has a minimal `Past Student` DocType for manual-entry / CSV import. School-Connected mode reads `tabStudent` directly via the adapter.

---

## ADR-006 — Storage adapter: Frappe Drive when present, Frappe File otherwise
**Status:** accepted

---

## ADR-007 — Mail adapter: Frappe Mail when present, frappe.sendmail otherwise
**Status:** accepted

---

## ADR-008 — Live Class fallback uses public Jitsi
**Status:** accepted
**Decision:** Fallback generates `meet.jit.si/<random>` URLs (no auth, no recording). Real adapter calls `school_live_class` if installed.

---

## ADR-009 — Alumni portal runs on a separate subdomain
**Status:** accepted
**Decision:** `alumni.<institution-domain>` rather than the staff site. Hostname routing in Website Settings + per-host Web Page Set.

---

## ADR-010 — Single-tenant per Frappe site
**Status:** accepted
**Decision:** One Frappe site = one alumni network. To run multiple, run multiple sites on the same bench.

---

## ADR-011 — Auto-promotion only in School-Connected mode
**Status:** accepted
**Decision:** Nightly job exists only when `mode == "school_connected"` and reads from `tabStudent`. In Standalone mode the entry paths are: self-registration + admin manual create + CSV import + Past Student bulk seed.

---

## ADR-012 — Current student visibility: hidden by default, masked initials in mentorship
**Status:** accepted
**Decision:** Mentorship UI shows masked initials ("A.K., Grade 11") until mentor accepts and both sign Code of Conduct.

---

## ADR-013 — Anonymous donations: hidden publicly, visible to Admin
**Status:** accepted

---

## ADR-014 — Recurring donations deferred to v2
**Status:** accepted

---

## ADR-015 — Job board open globally with country filter
**Status:** accepted

---

## ADR-016 — Mentorship age cutoff 16+, configurable
**Status:** accepted

---

## ADR-017 — Deceased alumni: status "Deceased" with memorial wall
**Status:** accepted

---

## ADR-018 — Free-tier policy
**Status:** accepted
**Decision:** Free tier (default for all Active alumni) includes directory, feed, jobs, donations, mentorship, volunteer board, network Q&A. Paid tiers unlock event member-rate, priority directory listing, committee eligibility.

---

## ADR-019 — Mentorship sessions on-platform or on-premises only
**Status:** accepted

---

## ADR-020 — Public site Jinja, logged-in app Vue 3
**Status:** accepted

---

## ADR-021 — Tests run on both modes in CI
**Status:** accepted

---

## ADR-022 — Public Network-Question board with privacy controls
**Status:** accepted

---

## ADR-023 — Geographic Chapters and Reunion Groups are auto-managed
**Status:** accepted

---

## ADR-024 — Outcome surveys at 1, 3, 5, 10 years post-graduation
**Status:** accepted

---

## ADR-025 — Adopt Buzz as the event engine, not in-house events
**Status:** accepted
**Decision:** Use [BuildWithHussain/buzz](https://github.com/BuildWithHussain/buzz) as the upstream event app. Wrap it in `alumni.integrations.events`. Don't build Event / Ticket Type / Booking DocTypes ourselves.
**Why:** Buzz already implements: dynamic ticket types, add-ons (T-shirts, meals), sponsorship management with payment-on-approval logo display, public booking pages, attendee self-service dashboard, ticket transfers and cancellations, configurable deadlines, GST collection, payment via Frappe `payments` app. AGPL-3.0, Frappe-native, actively maintained, 631+ commits. Building this ourselves wastes ~6 weeks and will lag forever.
**Consequences:** We add `Alumni Event Wrapper` (1:1 with Buzz Event) holding alumni-specific fields: `visibility` (Public/Alumni/Members), `chapter`, `member_pricing_enabled`, `passing_year_filter`, `organizer_alumni`. Permissions and discovery filters live in our wrapper; ticketing and payment live in Buzz. We contribute back any improvements upstream.

---

## ADR-026 — Frappe v16 only, no backport to v14/v15
**Status:** accepted
**Decision:** This app requires Frappe v16+. We use v16-specific features:
- `autoname: "uuid"` for DocTypes that don't need human-readable IDs (e.g., audit logs, polymorphic comments)
- Type annotations on all controller methods (`def validate(self) -> None:`)
- `frappe.utils.data_masker` for PII fields like `phone`, `email`, `whatsapp` when displayed to non-owners
- Virtual DocTypes for read-only views over external data
- Improved scheduler with proper `cron` event support
**Why:** Backporting drains energy, doubles testing surface, freezes us at v15's limitations. v16 has been stable since 2026; institutions deploying new alumni systems should run current Frappe.
**Consequences:** README, install docs, and CI all enforce v16+. Older deployments must upgrade.

---

## ADR-027 — Three default themes, theme system based on CSS custom properties
**Status:** accepted
**Decision:** Ship three themes (Heritage / Modern / Bold). Theme system uses CSS custom properties (tokens) loaded from `alumni/themes/<id>/tokens.css`. Switching = swap which tokens.css is active. No Vue rebuild, no Jinja change. Custom themes added via folder drop or admin UI ZIP upload. Validator enforces required token list, contrast minimums, no script injection.
**Why:** Institutions vary widely in identity. Three is enough to seed; the token system makes "theme" a non-developer concern.
**Consequences:** Component CSS uses tokens only — never literal hex. CI lints for hex/rgb in component files. Switching themes is instant.

---

## ADR-028 — Use Frappe `payments` app for gateway abstraction
**Status:** accepted
**Decision:** Don't build per-gateway integrations ourselves. Use [frappe/payments](https://github.com/frappe/payments) which Buzz already uses. Add `Alumni Settings.payment_gateway` linking to Payment Gateway records configured by the admin.
**Why:** payments app handles Stripe, Razorpay, PayTabs, GoCardless, etc. with a uniform interface. Adding a new gateway is configuration, not code.
**Consequences:** Manual / offline payments still need a small custom flow in `gateways/manual.py`. Bangladesh's bKash and Saudi HyperPay/Moyasar may need contributing back to `payments` if not present.

---

## ADR-029 — Public landing built with Frappe Builder
**Status:** accepted
**Decision:** The public landing, about, and pricing pages are built with [Frappe Builder](https://github.com/frappe/builder), exported as fixtures. The dynamic public pages (events list, event detail, donate, register) remain Jinja.
**Why:** Builder lets non-developers tweak the marketing pages without code. Theme tokens still apply.
**Consequences:** Builder fixtures are imported on `bench install-app`. Theme changes update the loaded `tokens.css`; Builder pages pick it up automatically since they reference tokens.

---

## ADR-030 — OpenAEC Frappe Skill Package is the team's Claude baseline
**Status:** accepted
**Decision:** Every developer installs the [OpenAEC Frappe Claude Skill Package](https://github.com/OpenAEC-Foundation/Frappe_Claude_Skill_Package) into `~/.claude/skills/`. CLAUDE_CODE_SETUP.md documents the install. Claude reads these skills automatically when generating Frappe code.
**Why:** Without domain skills, Claude generates code that looks correct but fails (e.g. importing inside Server Scripts). 61 deterministic skills covering ~95% of Frappe surface area solve this.
**Consequences:** Onboarding includes the skill install. Skill updates pulled monthly.

---

## ADR-031 — Private 1:1 messaging is built-in, realtime via Frappe socketio
**Status:** accepted
**Decision:** Alumni get an in-app private messenger as a first-class feature, not an add-on. Realtime delivery uses Frappe's built-in socketio (`frappe.publish_realtime`) — no Pusher / Pubnub / external broker. 1:1 only in v1; group chats deferred to v2. Recipients control inbound messaging via `Alumni Profile.messaging_preference` (All Alumni / Same Batch / Mentees Only / Off). Threads can be blocked or reported; reports go through Moderator review and into `Alumni Audit Log`.
**Why:** Every commercial alumni product (ZaiAlumni, Hivebrite, Almabase, Graduway) has a built-in messenger. Alumni networks live or die on peer-to-peer reach-outs. We already have socketio for free; bringing in Pusher would add a paid dependency and a privacy concern (messages routed off-server).
**Consequences:** Three new DocTypes: `Alumni Message Thread`, `Alumni Message`, `Alumni Message Read Receipt`. New adapter `alumni.integrations.messaging` so we can later swap the storage backend (e.g., to a dedicated chat app) without touching app code. Spam-control: rate-limited send (≤30 messages/min per sender), block list per profile. Attachments go through the storage adapter as **private** files only.

---

## ADR-032 — Document-based verification on registration
**Status:** accepted
**Decision:** Self-registered alumni must (a) verify their email and (b) upload at least one verification document (transcript, degree certificate, ID, yearbook page, or other) before an admin can approve them. Both gates are toggleable in `Alumni Settings`. Documents are stored as **private** files via the storage adapter; they are visible only to the owning alumni and to Admins (Moderators don't see PII docs by default).
**Why:** Open self-registration with no proof produces directories full of impostors and ex-students claiming credentials they don't have. The two-gate model (email + doc) is what every serious alumni product implements (ZaiAlumni's flagship "Application Review System"). For school-connected mode this gate is optional — the Student record already proves identity.
**Consequences:** New child DocType `Alumni Verification Document`. Profile lifecycle gains substates `Pending Email` and `Pending Docs`. Admin gets a "Pending Verifications" queue. Verification rejection sends a templated email with the reason and lets the alumni resubmit.

---

## ADR-033 — Election system as first-class feature, not optional add-on
**Status:** accepted
**Decision:** Committee elections (nominations, candidates, election symbols, voting, results) ship in v1 as part of the core app, not a separate paid add-on. Disabled by default in `Alumni Settings.enable_elections` so institutions that don't run elections see no extra menu items. The flow mirrors ZaiAlumni's transparent-vote model: alumni nominate themselves (optionally pay a nomination fee), Board Members approve and assign election symbols, all eligible alumni vote during the voting window, each vote can require Board-Member audit before counting (configurable), results are published and update the Committee membership automatically.
**Why:** Alumni associations universally hold elections — bundling this is what separates a "directory" product from a "real association" product. ZaiAlumni's election addon is one of their three flagship features; we do better by including it. A 12-DocType subsystem isn't trivial, but it's bounded and the data model is well-understood.
**Consequences:** 12 new DocTypes (Committee Category, Committee Designation, Election, Election Position, Election Symbol, Nomination, Candidate, Candidate Comment, Vote, Election Result, plus the existing Committee + Committee Member). New role `Alumni Board Member`. New scheduled job `tasks.advance_election_states()` walks elections through their states. Vote integrity: DB-level unique index on (election, position, voter); `voter` field redacted in all non–System-Manager queries; every read of vote data hits Audit Log.

---

## ADR-034 — Donation system: categories + comments + guest donations
**Status:** accepted
**Decision:** Donations get three upgrades over the v2 baseline: (a) campaigns are grouped under `Alumni Donation Category` (Scholarships, Library, Sports, Emergency Fund, etc.), (b) campaigns support public moderated comments via `Alumni Campaign Comment`, (c) campaigns can opt-in to **guest donations** — non-registered visitors donate via a public form, get a tax receipt by email, and never gain alumni-network access. Per-campaign toggle: `allow_guest_donations`, `allow_comments`.
**Why:** Categories make a 30-campaign list browsable. Comments turn a static fundraising page into a community wall. Guest donations matter most: parents, friends, and corporate matchers who aren't alumni still want to give — turning them away because they can't sign up is fundraising malpractice.
**Consequences:** Two new DocTypes (`Alumni Donation Category`, `Alumni Campaign Comment`). `Alumni Donation` gains `is_guest`, `guest_name`, `guest_email`. New whitelisted public endpoint `donate_as_guest`. Tax receipt template gains a `is_guest` branch. Privacy: guest emails never appear in the directory or any alumni-facing list.

---

## ADR-035 — Multi-tenancy via Frappe multi-site; SaaS billing deferred to v2 companion app
**Status:** accepted
**Decision:** ADR-010 stands: one Frappe site = one alumni network. To run a SaaS — many institutions on one bench — use Frappe's native multi-site (`bench new-site`, per-site config, separate database). The app is multi-site-safe: every query is site-scoped because it goes through Frappe's ORM, settings live in `Alumni Settings` (site-singleton), files go to per-site `private/` and `public/` folders. A v2 companion app `alumni_saas` will add a super-admin dashboard, package/plan management, per-tenant billing, custom domain provisioning, and tenant lifecycle (suspend, expire, delete). Not in v1 — the Frappe-native multi-site already gets you most of the way.
**Why:** Frappe's multi-site model is mature, battle-tested, and gives true data isolation (separate database per tenant). Building shared-database multi-tenancy on top would force `tenant_id` into every query, every DocType, every permission rule — a maintenance nightmare and a constant data-leak risk. The companion-app pattern keeps v1 lean while leaving a clear path to a managed SaaS offering.
**Consequences:** README documents both deployment models (single-tenant + multi-site SaaS). No `tenant_id` field anywhere in v1 schema. The companion app `alumni_saas` is a parking lot for the super-admin features that ZaiAlumni puts in their SaaS Addon: orders, customers, packages, domain requests, frontend CMS for the SaaS marketing site.

---

## ADR-036 — Two-Factor Authentication: mandatory for Admin/Board roles, optional for Alumni
**Status:** accepted
**Decision:** Use Frappe v16's built-in TOTP (Google Authenticator / Authy / 1Password / etc.). Per `Alumni Settings.mandatory_2fa_for_admin` (default true), users with Alumni Admin / Alumni Board Member / System Manager roles must enroll in 2FA before they can perform write operations. Alumni users get a soft prompt on first login but can dismiss it.
**Why:** Election integrity, donation flows, and PII access all sit behind admin/board accounts. A compromised admin can drain campaigns, fake elections, or scrape the directory. Frappe ships TOTP — turning it on is one setting. Forcing it on alumni would tank registration; making it optional with prompts gets the privacy-conscious half.
**Consequences:** Documented in onboarding flow. `Alumni Profile.2fa_enabled` is a virtual mirror of the User flag (display only). The `permissions.py` middleware checks the gate on first write call per session for Admin/Board roles.

---

## ADR-037 — Social login via Frappe OAuth Provider
**Status:** accepted
**Decision:** Use Frappe's built-in OAuth Provider Settings to enable Google, Facebook, LinkedIn, Apple, and Microsoft sign-in. Per `Alumni Settings.social_login_enabled` and `social_login_providers`. First-time social-login users are created as Pending alumni; they still go through the verification doc gate before becoming Active.
**Why:** A "Sign in with Google" button on the registration page lifts conversion 2-3x for typical alumni networks (most alumni already have a Google account). Frappe handles OAuth — we just expose the toggle and tell users which providers their institution allows.
**Consequences:** No new code in `alumni/` for OAuth itself; we configure Frappe core. Login template adds the providers' buttons conditionally. The `social_login_provider` field on `Alumni Profile` records which provider was used (for audit + UX, e.g., "you signed up with Google — manage there").

---

## ADR-038 — Multilingual + RTL support enabled by default
**Status:** accepted
**Decision:** Use Frappe v16's built-in translation system. Ship base translations for English, Arabic (RTL), Hindi, Bengali, Spanish, Portuguese, French, and Indonesian. Per `Alumni Settings.default_language` and `enabled_languages`. Each alumni has `Alumni Profile.preferred_language`. Themes declare `supports_rtl` in `theme.json`; a theme that doesn't is marked LTR-only in the picker.
**Why:** Alumni networks are global by definition. ZaiAlumni gets this right — they ship multilingual + RTL out of the box. Excluding non-English speakers from a school's alumni system is exclusionary in 2026. Frappe's translation infra is mature; the cost is producing the .csv files.
**Consequences:** All user-facing strings in Python wrapped in `_("...")`; all Vue strings go through a translation hook backed by Frappe's `frappe.client.get_translation`. RTL CSS handled by `[dir="rtl"]` selectors in component CSS. Theme validator (per THEMES.md) checks for `supports_rtl` and tests RTL rendering. Translation .csv files live in `alumni/translations/`.

---

## ADR-039 — Email + (optional) phone verification on self-registered alumni
**Status:** accepted
**Decision:** Self-registered alumni MUST verify their email (signed token, 24h expiry, `request_email_verification` + `confirm_email_verification` API). Phone verification (SMS OTP via communication adapter) is OPT-IN per `Alumni Settings.require_phone_verification` (default off — many regions have spotty SMS pricing). Email verification gates the move from `Pending Email → Pending Docs` in the lifecycle.
**Why:** Without email verification, anyone can claim any email. With it, you tie the profile to a real inbox you control. Phone verification adds another factor but isn't free (Twilio etc.) so it stays optional.
**Consequences:** New email template `alumni_email_verification`. New OTP template `alumni_phone_verification_otp` (used only when phone verification is enabled). Token storage: a signed JWT with the alumni's email, expiry, and a nonce — no DB table needed for one-shot tokens. Old tokens purged daily.

---

## ADR-040 — Pluggable SMS / WhatsApp channels with segmented broadcast
**Status:** accepted
**Decision:** The communication adapter exposes a generic two-function surface — `send_sms(to, body, channel=None)` and `send_whatsapp(to, body, template=None, variables=None, channel=None)` — backed by a new `Alumni Communication Channel` DocType. Each channel record stores credentials, provider type (Twilio / MessageBird / Vonage / Plivo / Africa's Talking / Wati / Gupshup / 360Dialog / Twilio WhatsApp / Custom HTTP), and an optional country filter for auto-routing. Multiple channels can be active simultaneously — e.g., one channel for +966 SMS via a local Saudi gateway and a separate WhatsApp Business channel for diaspora alumni. A new `Alumni Broadcast` DocType lets admins compose a message once and dispatch it to a defined segment: All Active Alumni, Chapter, Reunion Group, Committee, Class (passing year + optional section), Department (school-connected mode), Membership tier, or a custom uploaded list. Bulk sends are queued, rate-limited per channel quota, and per-recipient delivery is logged for retries. WhatsApp Business templates and variable substitution are first-class.
**Why:** Alumni offices live and die on SMS/WhatsApp reach — events, fee reminders, election turnout pushes, condolence notices. Hardcoding one provider (Twilio) is exclusionary: a Saudi institution wants a +966-friendly local gateway; an Indian institution wants Gupshup or MSG91; a Bangladeshi institution wants SSL Wireless. ZaiAlumni's own setup hardcodes a single provider per addon, which is exactly the constraint we should not inherit. Making channels first-class DocTypes turns "add a new SMS provider" into a configuration task — admin pastes credentials, picks the provider type, saves. No code deploy. Alumni who happen to be in different countries can be reached via the appropriate gateway automatically based on their phone country code.
**Consequences:** Two new DocTypes (`Alumni Communication Channel`, `Alumni Broadcast`) plus a child (`Alumni Broadcast Log Entry`). Communication adapter `_real.py` ships with built-in drivers for 12 providers (Twilio, Twilio WhatsApp, MessageBird, Vonage, Plivo, Africa's Talking, Wati, Gupshup, 360Dialog, Unifonic, MSG91, SSL Wireless); a Custom HTTP driver lets institutions wire any provider exposing a JSON HTTP API by configuring URL + auth header + payload template — no Python required. Channel selection precedence per send: explicit `channel` argument → recipient country match → channel marked `is_default` → first active. Bulk sends create a parent `Alumni Broadcast` record and one `Alumni Broadcast Log Entry` per recipient; failures get retried twice with exponential backoff before being marked Failed. Costs visible per channel (channel records track total sends today / this month). Encrypted credentials per Frappe's standard `Password` field type.

---

## ADR-041 — Custom domain + subdomain auto-provisioning for SaaS deployments
**Status:** accepted
**Decision:** Build a domain-management layer designed for both single-tenant (one institution, one custom domain) and SaaS (one bench, many tenants, each with a vanity subdomain plus optional custom domain). New DocType `Alumni Tenant Domain` (lives in the v1 app, used by both deployment models) holds: `domain`, `domain_type` (Subdomain / Custom Domain), `verification_status`, `dns_token`, `ssl_status`, `ssl_issued_on`, `ssl_expires_on`, `is_primary`, `redirect_to_primary`. SaaS signup flow auto-provisions `<slug>.alumni-saas.com` (Frappe `domains` table + nginx vhost regenerated by `bench setup nginx` + wildcard SSL). When a tenant adds a custom domain, the flow is: (1) admin enters the domain → (2) we generate a `dns_token`, instruct admin to add a CNAME plus a TXT record for verification → (3) hourly job verifies DNS → (4) on success, request a Let's Encrypt cert via Frappe's existing `bench setup lets-encrypt` → (5) flip `verification_status=Verified, ssl_status=Issued`, regenerate nginx, and the domain goes live. Renewal is automated 30d before expiry. All internal links use `frappe.utils.get_url(force_https=True)` so a domain swap never breaks them.
**Why:** Custom domain is table stakes for any institution that takes itself seriously — `alumni.aramco-school.edu.sa` reads as official; `aramco.alumni-saas.com` reads as a side project. Building this in v1 (rather than punting to the v2 SaaS companion app) means single-tenant deployments get the same flow for free, and the v2 SaaS app just adds a billing/tenant-creation UI on top of an already-working domain system. Frappe already has Let's Encrypt automation (`bench setup lets-encrypt`); we wrap it.
**Consequences:** New DocType `Alumni Tenant Domain`. New scheduled job `tasks.verify_pending_domains()` (hourly) and `tasks.renew_expiring_certs()` (daily). Wildcard cert for the SaaS subdomain (`*.alumni-saas.com`) handled at infra layer (separate runbook). Custom-domain SSL provisioned per-tenant. Domain page has a clear "where to set DNS" walkthrough with copy-able CNAME/TXT values. Admin sees one of four states on every domain: Pending DNS / Pending SSL / Live / Expired. Cert auto-renew failures page the SaaS operator. Tenant-facing email (`alumni_domain_live`) when a custom domain goes live.

---

## ADR-042 — Progressive Web App (PWA) first; native wrappers deferred
**Status:** accepted
**Decision:** Ship the alumni portal as an installable PWA. Includes: web app manifest (with tenant-branded icons + splash + theme color pulled from the active theme), service worker for offline caching of the shell + last-viewed directory pages + own profile + recent messages, push notifications via the Web Push API for new messages and event reminders, and an "Add to Home Screen" prompt after the user's third visit. Native iOS / Android wrappers (Capacitor or Bubblewrap) deferred to a v2 effort if institutions ask — the PWA covers ≥95% of mobile use cases, including push, camera access for profile photos and verification doc uploads, and home-screen install on Android, iOS 16.4+, and desktop. The PWA is bundled per-tenant: when a tenant changes their theme or logo, the manifest regenerates so installed app icons/colors update on next launch.
**Why:** Alumni use phones. Telling them to "open Chrome and bookmark the site" loses 40% of weekly engagement vs an icon on the home screen. Native apps (especially iOS) cost real time + Apple Developer fees + review cycles per tenant; PWAs are zero-marginal-cost per institution and ship the same code as the web. Push notifications for new messages are the single biggest driver of repeat visits in alumni networks; without them the app feels dead.
**Consequences:** New folder `alumni/public/pwa/` with `manifest.webmanifest`, `service-worker.js`, icon set. `alumni.tasks.regenerate_pwa_manifest_for(site)` runs whenever Settings.theme or institution_logo changes. Push subscription flow integrated with `Alumni Profile.push_subscription` (encrypted JSON). Offline list explicit and short — we don't pretend to be an offline-first app. Lighthouse PWA score required ≥ 90 in CI.

---

## ADR-043 — Dark mode shipped as fourth default theme; design system explicitly documented
**Status:** accepted
**Decision:** Ship a fourth default theme `Aurora` (dark mode), bringing the count to 4: Heritage / Modern / Bold / Aurora. Each user picks their preferred theme override in their profile, falling back to the institution default. Dark mode auto-engages when the user's OS preference is dark and they haven't explicitly chosen a theme. New file `DESIGN_SYSTEM.md` documents the full component vocabulary: typography scale, spacing scale, elevation tokens, component patterns (buttons, cards, inputs, modals, toasts, empty states, loading states, error states, skeletons), motion guidelines (durations, easings), responsive breakpoints (mobile 0–639px / tablet 640–1023px / desktop 1024px+), accessibility floor (WCAG AA, focus rings, touch targets ≥44px), and cultural considerations (RTL specifics, regional iconography choices).
**Why:** Three themes wasn't enough — every modern product needs dark mode and "no dark mode" reads as dated. The bigger gap was the missing design system: themes covered visual tokens but not the *patterns* (when do you use a card vs a list? what does a loading state look like? how do error toasts dismiss?). A designer or developer who joins the project needs that vocabulary to ship anything that fits. The `DESIGN_SYSTEM.md` doc fills that gap and is referenced by every frontend ticket.
**Consequences:** New theme folder `alumni/themes/aurora/`. New `Alumni Profile.preferred_theme` field (overrides institution default). `prefers-color-scheme` media query handled in the theme loader. New doc `DESIGN_SYSTEM.md` (treat as authoritative for frontend tickets). Storybook (or equivalent) seeded for all documented components with both light and dark variants — added to the build (T-091).

---

## ADR-044 — Profile completeness scoring and guided onboarding
**Status:** accepted
**Decision:** Compute a `profile_completeness_percent` (0–100) on every Alumni Profile based on a weighted field checklist defined in `Alumni Settings.completeness_rules` (JSON). Default rules: profile photo (15%), current employer + designation (15%), current city + country (10%), bio (10%), career history with ≥1 entry (10%), education history with ≥1 entry (5%), LinkedIn URL (5%), industry tag (5%), willing-to-mentor flag set (5%), preferred language (2%), 2FA enabled (3%), phone verified (5%), at least one chapter joined (5%), interests/skills tags ≥3 (5%). Onboarding wizard runs after first login: shows the completeness ring, walks through 6 high-leverage fields, lets the user skip per-step. After onboarding, a dismissible card on the dashboard nudges toward the next missing field. Optional admin gate: institutions can require ≥X% completeness before a profile appears in the directory or before messaging is enabled.
**Why:** Empty profiles are the #1 reason alumni networks feel dead. A directory of 5,000 alumni where 4,200 have only name + passing year is unhelpful. Gamifying completion with a visible ring + clear next step lifts completion from ~30% to ~70% based on how every other social/professional product works. The completeness rules are JSON-configurable so each institution weights what matters to them — a tech college might weight LinkedIn URL high; a religious institution might weight chapter affiliation high.
**Consequences:** New virtual field `Alumni Profile.profile_completeness_percent` (computed on save). New `Alumni Settings.completeness_rules` JSON field with shipped defaults. New onboarding flow `/alumni/welcome` (Vue). Dashboard card component "Complete your profile". Admin Settings UI for editing completeness rules ships with a preview that shows what % a sample profile would score. Tests: rule changes recompute scores incrementally (job, not migration), respect privacy (never expose individual scores below the directory minimum to non-Admin viewers).

---

## ADR-045 — Memorial Wall, Distinguished Alumni, and Awards as first-class features
**Status:** accepted
**Decision:** Three related but distinct DocTypes formalize how an institution honors alumni. (a) **Alumni Memorial Tribute** — a child table on Profile, only visible when `Profile.status = Deceased`, lets verified peers leave moderated tributes; the profile auto-becomes a memorial page at `/alumni/memorial/<name>` with a candle icon, dates, biography, photo gallery, and tributes; opted-in family members can be designated as page maintainers. (b) **Alumni Award** — a catalog of award types (Distinguished Alumni, Young Achiever, Lifetime Achievement, Hall of Fame, custom), each with a `cycle` (Annual / Biannual / Ad-hoc), `nomination_open` window, criteria, and selection method. (c) **Alumni Award Recipient** — a recognition record linking an Award + an Alumni Profile + a `year` + `citation` + `photo` + `is_published`; renders on a public Hall of Fame page. Distinguished Alumni recipients get a permanent badge on their profile and in the directory.
**Why:** Alumni networks are at their core *recognition* engines. Reunions, awards, and memorials are the moments that convert passive members into active donors and ambassadors. The current spec mentioned "Memorial wall" without a schema for it, which is exactly the gap that turns a feature into a placeholder. Awards programs also drive engagement (nominations) and donations (alumni who win an award are 6× more likely to donate within the next year per industry benchmarks). Tributes need moderation because grief brings out trolls.
**Consequences:** New DocTypes: `Alumni Memorial Tribute` (child of Profile, ≤500 chars body, moderated), `Alumni Award`, `Alumni Award Recipient`. New child on Profile: `memorial_maintainers` (users authorized to update the memorial page). Profile lifecycle gains transition `Active → Deceased` (Admin-only, audited) which triggers a workflow: notify family contact if recorded, switch profile to memorial template, freeze contact-data masking permanently. Public Hall of Fame page at `/alumni/hall-of-fame` filterable by award type and year. Award nomination flow reuses the election Nomination pattern (peer-nominated, board-reviewed). Donation matching: institutions can configure that any donation in honor-of a Distinguished Alumni gets a +25% match for the year of the award.

---

## ADR-046 — Alumni Perks marketplace + digital member card
**Status:** accepted
**Decision:** Active Alumni (or Members, configurable per perk) get a curated `Alumni Perk` feed: discounts and benefits offered by partner businesses, alumni-owned companies, and the institution itself. New DocTypes: `Alumni Perk Category` (Travel, Dining, Education, Tech, Health, Local Business, Alumni-Owned Business…), `Alumni Perk` (title, description, partner, category, discount value, redemption type, eligible audience filter, valid_from/valid_to, redemption code or URL or "show member card" flow, redemption limit per alumni, geographic_filter), `Alumni Perk Redemption` (audit trail: which alumni redeemed which perk when). Alumni get a **digital member card** at `/alumni/card` — a brandable identity card with photo, name, passing year, member tier, QR code (encodes profile URL + signed verification token), expiry date, and the institution's seal. Card can be added to Apple Wallet / Google Wallet via PassKit / Google Wallet API integration. Partners verify a member by scanning the QR (returns a signed JSON of name, status, expiry — no PII beyond what they need to verify).
**Why:** "What do I get for paying $50/year?" is the question every paid-membership institution dies on. Without tangible perks, renewal rates collapse. A perks marketplace gives the answer: ten partner discounts that, used twice a year, return more than the membership fee. Alumni-owned businesses listed in the marketplace also get a marketing boost — turning the network itself into a perk. The digital member card with QR is the credential that makes redemption trivial, and is what alumni actually want to show off (LinkedIn flex).
**Consequences:** Three new DocTypes (Perk Category, Perk, Perk Redemption). Public `/alumni/perks` page (alumni-only or member-only depending on perk eligibility). Verification endpoint `verify_member_card(token)` returns `{name, passing_year, member_tier, expires_on}` with no contact data. PassKit/Google Wallet integration is opt-in per institution; otherwise the card is rendered as a downloadable PNG/PDF. Alumni-owned business listing as a perk requires Moderator approval to prevent abuse. Partners are tracked as Frappe Customer / Supplier records when relevant for accounting (school-connected mode).

---

## ADR-047 — Job Referral system + Speaker Bureau as opt-in alumni capabilities
**Status:** accepted
**Decision:** Two distinct opt-in capabilities layered on top of existing infrastructure. (a) **Job Referral**: for any `Alumni Job Post` where the poster has set `referral_offered=1`, alumni applying can request the poster to refer them internally; this creates an `Alumni Job Referral` record (job + referrer + referee + status: Requested / Accepted / Declined / Submitted / Hired / Not Hired) which the referrer manages from their dashboard, with a referral message and optional company-specific instructions. The referrer earns reputation points on accepted referrals, displayed on their profile. (b) **Speaker Bureau**: alumni opt in via `Alumni Profile.speaker_topics` (child table — topic + level + format: in-person / virtual / both + travel willingness + honorarium expected: free / negotiable / fixed). Current students or admin browse `/alumni/speakers` and submit `Alumni Speaker Request` (event + topic + date + audience size + budget + message); requests route to the alumni's inbox; alumni accept / decline / counter-propose. On acceptance, an Alumni Event Wrapper is auto-created with the speaker as a featured guest.
**Why:** Static job boards underperform — alumni read the post, never apply because they have no warm intro. Adding a referral toggle is what every alumni network with strong placement outcomes does (Stanford GSB, IIT alumni networks, Harvard Business School). It signals to applicants "this isn't a cold posting" and to posters "you'll get pre-vetted candidates." Speaker bureaus are how institutions activate their alumni for current students — the request volume is small but the reputational impact (alumni teaching alumni) is large. Both features cost almost nothing because they layer on existing DocTypes (Job Post, Event Wrapper).
**Consequences:** Two new DocTypes (`Alumni Job Referral`, `Alumni Speaker Request`) + one child on Profile (`Alumni Speaker Topic`). New role: nothing new — referrers are alumni; speakers are alumni. Opt-in everywhere — `referral_offered` defaults to false on Job Post; speaker_topics is empty by default. Reputation points are display-only (no leaderboard gamification — this is professional, not Reddit). Speaker honorarium handled outside the system (notes on the request); we don't process speaker payments in v1.

---

## ADR-048 — Networking match suggestions: deterministic scoring, no ML in v1
**Status:** accepted
**Decision:** A "People you should know" panel on the dashboard shows 5 alumni picked by a deterministic scoring function: base score from shared chapter (3pt), shared passing-year ±2 (3pt), shared current city (2pt), shared current country (1pt), shared industry (2pt), shared willing-to-mentor flag (2pt for mentees seeing mentors, vice versa), shared interest tags (1pt per tag, capped at 3pt), recently active on the platform (1pt), already-connected exclusion (skip). Top 5 by score, ties broken by recent activity, refreshed weekly. Every shown card has a "Not interested" button (records to `Alumni Match Mute`) so the panel can self-correct. No ML model in v1: a hand-tuned scoring function is more transparent, debuggable, fair, and produces results indistinguishable from a v1 ML approach for networks under 50K alumni.
**Why:** Directory search assumes the alumni knows whom they're looking for. The reality is they don't — they want serendipity. A weekly "10 alumni you should know" surface is what every alumni network with strong engagement does. Starting deterministic over ML keeps it explainable (every user can see *why* they were matched), avoids cold-start problems, and ships in days instead of months. If the network grows past 50K alumni or institutions ask for more sophisticated recommendations, an ML reranker can be added behind the same API later.
**Consequences:** New DocType `Alumni Match Mute` (child or own table — alumni + muted_alumni + muted_on). New scheduled job `tasks.refresh_match_suggestions()` weekly. New API `get_match_suggestions_for(alumni)`. Dashboard widget. Tests verify scoring transparency: the controller exposes `_explain_score(viewer, candidate)` returning the breakdown for debugging and admin support.

---

## ADR-049 — SEO + Open Graph + JSON-LD + QR codes for shareable surfaces
**Status:** accepted
**Decision:** Every public alumni surface — campaign, candidate, story, news article, event, job post, alumni-of-the-month — emits rich preview metadata (Open Graph tags, Twitter Card tags, JSON-LD structured data of the right schema.org type), so a link shared on WhatsApp / X / LinkedIn / Slack / iMessage renders with the institution's branding, the right image, and a clear title and description. Crawlable robots.txt + sitemap.xml are auto-generated and updated daily. QR codes are shipped throughout: on event tickets (check-in), on member cards (verification), on candidate profiles (ballot lookup at polling stations), on alumni profile public URL (business-card swap), on perk redemption pages (partner scan). QR generation uses the `qrcode` Python library; codes are deterministic from the underlying URL so they're stable across sessions.
**Why:** Alumni networks live or die on word-of-mouth virality. A WhatsApp message from one alumni saying "look at this candidate's manifesto" with a thumbnail + title gets 6× the click-through of a bare URL. Same for donation campaigns going viral. Without OG tags these previews show as bare URLs and conversion craters. JSON-LD on top makes events show in Google calendar previews and jobs show in Google for Jobs — free traffic. QR codes turn every physical alumni event into a digital touchpoint and make verification (member card, ballot, ticket) instant.
**Consequences:** Every public Jinja template extends a `seo_meta.html` partial that renders OG / Twitter / JSON-LD from a `seo_meta()` helper on the corresponding controller. New utility `alumni.utils.qr.generate(url, size=200)` returning PNG bytes. `robots.txt` and `sitemap.xml` generated by `tasks.refresh_sitemap()` daily, listing only public DocTypes. Privacy: alumni profile public URL is opt-in (existing `privacy_visibility` field gates it); private campaign / candidate / event surfaces emit a `noindex` tag. Lighthouse SEO score required ≥ 95 in CI.

---

## ADR-050 — Per-Alumni vCard / Digital Business Card builder
**Status:** accepted
**Decision:** Every Alumni Profile can opt into a rich Digital Business Card (vCard) — a public-facing, branded, mobile-optimized landing page that goes beyond the basic public profile slug from ADR-049. New DocType `Alumni VCard` (1:1 with Profile, optional) holds the customization layer; thirteen child / linked DocTypes hold sections (social links, services, gallery, testimonials, iframes, business hours, blog posts, custom links, FAQ, inquiries, appointments, products, product orders) plus an analytics table (visits). The vCard builder is comprehensive — adapted from the InfyVCardsSaas surface area (40+ feature releases) but pre-populated from existing Alumni Profile data so alumni don't re-enter information. v1 ships **two** built-in templates only: **"Classic Professional"** (formal, light + dark variants, alumni-association branding-forward) and **"Modern Minimal"** (clean, image-led, mobile-first). All other templates are added by the institution admin through the **Alumni VCard Template registry** (see ADR-053). Alumni-association branding (institution seal, verified-alumni badge, member-tier badge, Hall-of-Fame badge) renders on every vCard regardless of template — these are alumni vCards, signed by the institution, not generic business cards. Custom JS is forbidden (security cost > value, evidenced by InfyVCards repeatedly fixing custom-JS bugs across releases); custom CSS is allowed but sanitized via `bleach` allow-list. AI assistance for bio writing and section drafting is built in (per ADR-054).

**Why:** vCards are how individuals brand themselves online — a polished, single URL they share on resumes, in email signatures, on WhatsApp status, on NFC cards. Alumni associations that offer this as a member benefit lift renewal rates substantially — the vCard ties to membership status (lapse → graceful break per ADR-051), creating a renewal pull. The InfyVCards feature set is the reference because it's been validated by hundreds of small-business customers across 14+ major versions; we adapt their surface area but ship a Frappe-native, alumni-tuned product. Critically, we ship only two default templates because (a) ADR-053 makes admin template management a first-class capability and (b) institutions know their alumni demographic better than we do — a doctor-heavy med-school alumni network needs different templates than a tech-college network.

**Consequences:** Fourteen new DocTypes for the vCard subsystem — see SPEC.md inventory. Public route `/v/<slug>` with `slug` unique per institution; reserves under `/v/admin`, `/v/api`, `/v/system` are blocked at validation. Pre-fill on first save: copies profile photo, name, current employer, current city, LinkedIn URL, education history into the vCard so the alumni only edits what they want different. Section-level visibility toggles let an alumni keep the vCard simple (just hero + contact + WhatsApp) or rich (everything). Storage governed by the existing per-site quota plus a **per-tier `vcard_storage_mb` allowance** on Membership Plan (per Lesson #5 in ADR-054 — InfyVCards added storage quota too late and customers blew past their hosting). Image cropper at all upload points (Lesson #4). Multiple vCards per alumni is *not* supported in v1 (1:1 with Profile); deferred to v2. NFC card ordering and affiliation commissions belong in `alumni_saas` v2.

---

## ADR-051 — Per-alumni custom domain support (extension of ADR-041)
**Status:** accepted
**Decision:** Alumni who hold an active Member tier (or whose institution has enabled the feature for all alumni) can attach their own custom domain (e.g., `ahmed.com`, `dr-sara-cardiology.com`) to their Alumni VCard. The same `Alumni Tenant Domain` DocType from ADR-041 is reused — extended with two fields: `domain_scope` (Select: Institution / Alumni VCard) and `target_vcard` (Link → Alumni VCard, only when scope = Alumni VCard). The DNS verification and Let's Encrypt SSL flow is identical: alumni enter the domain → system shows them a CNAME pointing to the institution's vcard endpoint plus a TXT record for verification → hourly job verifies → SSL provisioned → live. The feature is gated by `Alumni Settings.alumni_custom_domains_enabled` (default false; institutions decide whether to offer it) plus a per-tier eligibility check (Members-only by default, configurable). The institution sees aggregate visibility (how many alumni have custom domains) but never proxies the request — alumni-domain traffic hits nginx, terminates SSL, routes to the appropriate `Alumni VCard` controller by Host header, renders the vCard.
**Why:** A custom domain converts a vCard from "page on someone's site" to "my professional URL." Alumni who pay for membership specifically want this — `ahmed-engineering.com` reads as professional; `aramco-alumni.com/v/ahmed-1234` does not. The infrastructure already exists (ADR-041); making it work for vCards is reusing the same code path with a different routing target. Gating it as a paid Member benefit is also one of the strongest renewal incentives that exists — the domain breaks if membership lapses (after a configurable grace period), which alumni feel.
**Consequences:** Two new fields on `Alumni Tenant Domain`. **Two-field gating on `Alumni Settings`**: a master toggle `alumni_custom_domains_enabled` (Check, default 0 — institutions opt in) AND a per-tier allow-list `alumni_custom_domain_eligible_tiers` (Table → Alumni Membership Plan — which member tiers may attach a custom domain). The T-114 eligibility check ANDs both: feature off OR tier list empty OR alumni's tier not in the list ⇒ no custom domain. This separates "are we offering this at all?" from "to whom?" and lets institutions ship the feature dark while they decide pricing. Nginx vhost generation: SaaS deployments generate one server block per registered alumni custom domain pointing to the tenant's site. Membership lapse handling: a `tasks.handle_lapsed_member_domains()` job runs daily; configurable grace period (default 30 days) before the domain returns a 404 / branded "membership expired — renew to restore" page; SSL certificate keeps renewing through the grace period so no certificate errors. Bulk operations: the institution admin sees a "Custom domains" panel listing all alumni custom domains across the institution. Audit log entry on every domain registration / deletion. The v2 `alumni_saas` app extends this with billing for institutions that want to charge alumni for the custom-domain feature directly (vs bundling with membership). Multiple custom domains per vCard not supported in v1 (one primary per vCard); aliases / redirects deferred to v2.

---

## ADR-052 — WhatsApp Business integration: click-to-chat + Business Profile sync
**Status:** accepted
**Decision:** Alumni vCards (and the alumni profile) include a WhatsApp Business surface beyond a plain "click to chat" link. Two-tier integration: (a) **Lightweight click-to-chat** — alumni enter a WhatsApp number and an optional pre-filled message; the vCard renders a WhatsApp button that opens `wa.me/<number>?text=<message>`; tracked via `whatsapp_click_count` analytics on the vCard. (b) **WhatsApp Business API integration (optional, per ADR-040 channel)** — when an alumni operates a WhatsApp Business account and their institution has a registered WhatsApp Business `Alumni Communication Channel`, the vCard can additionally render a WhatsApp Business catalog (services + products synced from the vCard's existing Service / Product child tables to a WhatsApp Business catalog), accept inbound message replies into the alumni's vCard inbox, and send templated outbound messages (appointment confirmations, order updates) using the channel's existing infrastructure. Tier (a) ships in v1; tier (b) ships in v1 *behind a feature flag* because the WhatsApp Business catalog API requires Meta verification of each business which is non-trivial.
**Why:** WhatsApp is the dominant business communication channel in MENA, India, Bangladesh, Indonesia, Brazil, Africa, and large parts of Europe — exactly the regions where alumni networks operate. A vCard without a one-tap WhatsApp button is missing the most-used contact action. The lightweight click-to-chat tier ships in two days and covers 95% of use cases. The Business API tier (b) layers on top: alumni who run businesses (consultants, doctors, lawyers, retail) get a real customer channel hooked into the same vCard. Tying tier (b) to the existing `Alumni Communication Channel` means we don't reimplement WhatsApp — we reuse the Wati / Gupshup / 360Dialog / Twilio WhatsApp drivers from ADR-040.
**Consequences:** New fields on `Alumni VCard`: `whatsapp_number`, `whatsapp_business_message` (default pre-fill: "Hi! I found you on the alumni network."), `whatsapp_business_account_id`, `whatsapp_catalog_sync_enabled`. New optional `Alumni Communication Channel.purpose = 'alumni_business'` distinguishes alumni-personal channels from institutional broadcast channels — alumni can connect their own WhatsApp Business account for tier (b). `Alumni Profile.whatsapp` (existing field) is the lightweight default; vCard `whatsapp_number` overrides for the vCard surface specifically. Privacy: WhatsApp number is masked in directory listings unless the alumni explicitly publishes it; vCard publication is opt-in. Inbound messaging from vCard WhatsApp does NOT route into the internal Alumni Message Thread system — those are different audiences (vCard chat = customers / strangers; internal messaging = peer alumni). Catalog sync runs as a background job after every Service / Product save. Tier (b) enrollment (Meta business verification, phone number provisioning) is documented in `docs/integrations/whatsapp-business-setup.md`; the setup itself is the alumni's responsibility, not the institution's.

---

## ADR-053 — Admin-managed vCard / WhatsApp template registry (template marketplace pattern)
**Status:** accepted
**Decision:** vCard templates and WhatsApp Store templates are NOT compiled into the app. They live as portable **template packages** that admins can upload through the UI and that load dynamically. Each template package is a folder (or .zip on upload) at `vcard_templates/<id>/` containing exactly four files: `template.json` (manifest with id, display_name, version, author, license, supports_dark, supports_rtl, category, preview_image, sample_data path, declared sections, sanitization profile), `card.html` (Jinja2 template with a documented variable contract), `card.css` (theme-tokenized styles using the same CSS variables as the main themes from THEMES.md so every vCard inherits the institution's brand colors automatically), and `preview.png` (used in the picker). New DocType `Alumni VCard Template` (read-only, populated from disk) registers each available template. Admin upload flow: admin drops a `.zip` → server unzips into a quarantine dir → validator runs (manifest schema check, Jinja syntax check, CSS allow-list scan, no JS files, file-size limits, no path traversal) → on pass, files moved to live dir and Alumni VCard Template record created → on fail, validation errors shown with line numbers. Same pattern for **WhatsApp Store templates** at `whatsapp_templates/<id>/`. Built-in: 2 vCard templates (Classic Professional, Modern Minimal) + 1 WhatsApp Store template (Standard Storefront). Everything else added by admin. Templates can declare an optional `extends_template` field for inheritance — a "Doctor" template can extend "Classic Professional" and override only what's different.

**Why:** InfyVCards' 14+ version history shows they've shipped over 40 templates because customers always want more, niche-specific designs (Doctor, Lawyer, Photographer, Real Estate, GYM, Pet shop, School, Marriage, Travel, Garden, Reporter, Architect, Hotel, Restaurant, Beauty, Jewellery Store, Cloth Store, Grocery, etc.). Hardcoding templates means every new template requires a code release; the institution can't move without us. Making templates a first-class admin upload turns "we need a doctor template" from a 2-week dev cycle into a 10-minute admin task. The Frappe app stays small; the template ecosystem grows independently. This pattern also opens a future **template marketplace** where institutions can share templates with each other (deferred to a later milestone). The Jinja+CSS+JSON contract is exactly what Frappe Print Format uses internally, so we're not inventing a new mechanism — we're reusing an established Frappe pattern.

**Consequences:** New DocType `Alumni VCard Template` + `Alumni WhatsApp Store Template` (both read-only, disk-backed). Admin UI at `/alumni/admin/vcard-templates` showing installed templates with version, author, preview, install/uninstall, plus an "Upload template" button. Validator covers: manifest schema (JSON Schema validation), Jinja sandbox compilation (rejects `{% include %}` outside template folder, `{{ self }}` access, file-system access patterns), CSS sanitization (no `@import`, no `url(http...)` referencing external resources, no `expression()` IE legacy, no JavaScript URLs, only allow-listed properties), file count + size caps (≤30 files, ≤10MB total per package). On install, the manifest's `sample_data` JSON is used to render a preview that visually matches what an alumni will see — admins approve based on the preview, not just the manifest. Versioning: re-uploading a template with a higher `version` updates the live files; lower version refused. Audit log on every upload / install / uninstall. Template-pack signing (cryptographic signature in v2 of `alumni_saas`) deferred. Documentation: `docs/templates/authoring-vcard-templates.md` walks a designer through creating a template from scratch in under an hour, with the variable reference, sanitization rules, and preview workflow.

---

## ADR-054 — Lessons applied from InfyVCardsSaas's 14-version history
**Status:** accepted
**Decision:** A consolidated set of design choices made up-front rather than learned the hard way over years. We're shipping as v1 what InfyVCards added across v1.0 → v14.8 because we've watched their roadmap and don't need to repeat the same painful path.

**The lessons we applied:**

1. **Storage quotas are v1, not v8.** InfyVCards added storage limit settings only at v8.8.0 after customers ran their hosting bills up. We ship per-tier `vcard_storage_mb` and `total_vcard_storage_mb` on Membership Plan, with an enforced check on every upload, from day 1.

2. **Image cropper at upload time, not after.** InfyVCards added image cropper only at v14.6.0. We use Frappe's image-handling stack with `croppr.js`-style client-side cropping for every image upload point (vCard cover, profile, gallery, products, services). Avatars, banners, and gallery items are auto-cropped to documented aspect ratios.

3. **RTL is forever-tax if not done from day 1.** InfyVCards spent multiple releases fixing RTL bugs (Arabic in virtual backgrounds, RTL-LTR mobile-number conversion, Persian RTL added in v14.5). Per ADR-038 we ship full RTL on day 1 with `[dir="rtl"]` selectors and logical CSS properties; every vCard template MUST declare `supports_rtl: true` in its manifest, which the validator enforces (the validator reads the CSS for any LTR-only properties like `padding-left` instead of `padding-inline-start` and warns).

4. **Custom JS is permanently out of scope.** InfyVCards' changelog shows recurring "Fix: custom CSS and custom JS issue" entries. JavaScript injection is an XSS attack surface, an SEO-bot break, and a privacy risk. We allow CSS (sanitized) but never JS in vCard customization. Power users who want JS write a full Frappe app extension instead.

5. **Custom domain DNS state machine is its own subsystem.** InfyVCards' changelog shows custom domain added v12.1.2, then "added" again v14.5.0, then "Re-Apply Custom Domain After Rejected By Super Admin" v14.7.9 — meaning their state machine kept needing patches. Per ADR-041 + ADR-051, the `Alumni Tenant Domain` workflow has explicit states (Pending DNS → DNS Verified → SSL Pending → Live → Failed → Expired), retry semantics, and re-apply after rejection from day 1.

6. **2FA + recovery codes from day 1.** InfyVCards added 2FA at v14.6.0 and recovery codes at v14.7.6. Per ADR-036 we use Frappe's native TOTP plus 8 single-use recovery codes generated on enrollment, downloadable as a .txt or printable PDF.

7. **Visitor-based vCard view limits as a tier feature.** InfyVCards added this at v14.7.8. Per-tier `vcard_monthly_views_limit` on Membership Plan; counter resets monthly; over-limit shows "monthly view limit reached — share returns next month" branded page (or upgrades the tier inline).

8. **Block-email-domain antispam list is v1.** InfyVCards added this at v13.3.2. We ship `Alumni Settings.blocked_email_domains` (one domain per line) and `blocked_inquiry_keywords` (regex list) for the contact-form spam problem from day 1.

9. **Bulk operations are admin-time-savers, not nice-to-haves.** InfyVCards added bulk vCard delete + bulk user delete at v14.1.0. We ship bulk operations on every admin list view in v1: bulk approve (verifications, comments, tributes), bulk delete (with double-confirm), bulk export (CSV), bulk message (creates an Alumni Broadcast pre-populated with the selection per ADR-040).

10. **AI bio drafting + section content drafting.** InfyVCards added AI-generated vCard at v14.7.9. Per this ADR we add a new `alumni.integrations.ai` adapter (with `_real` for OpenAI / Anthropic / Bedrock and `_fallback` that's a no-op) callable from: vCard bio composer, story draft, donation campaign description, news article first-pass, awards citation. AI is opt-in per institution (Settings.`ai_enabled`); when off, the buttons hide. Privacy: alumni data passed to AI is minimized (no email, no phone, no other alumni's data), the prompt template is auditable, and every AI call is logged with prompt hash + model + token count for cost tracking.

11. **Business Directory.** InfyVCards added a public Business Directory at v14.7.8 listing all paid vCards. We add an "Alumni Business Directory" public page at `/alumni/businesses` showing alumni who have published vCards and have set `is_alumni_owned_business_owner=1`, indexed for SEO, filterable by industry / city / passing-year. Drives discovery + perks visibility.

12. **WhatsApp Store is a vCard section, not a separate product.** InfyVCards built WhatsApp Store as a parallel module to vCard at v13.0.0, duplicating most of the schema (their own products, their own templates, their own analytics). We integrate it as a section on the existing Alumni VCard with `enable_whatsapp_store=1`; products are the same `Alumni VCard Product` records; orders flow through the same receivables adapter; WhatsApp catalog sync (per ADR-052 tier b) handles outbound. Avoids 50% schema duplication.

13. **Tax field on products from day 1.** Tax was added to products + NFC orders late in InfyVCards. We model `tax_inclusive`, `tax_rate_percent`, `tax_label` on every monetizable surface (vCard Product, Donation, Membership Plan, Event ticket via Buzz wrapper) and let the receivables adapter compute the breakdown.

14. **PWA tested on iOS Safari from day 1.** InfyVCards' v13.0.0 had to fix "PWA not proper working on iphone." Per ADR-042, PWA CI tests run on iOS Safari (via WebKit) as well as Chromium and Firefox; install flow tested on iOS 16.4+ explicitly.

15. **Locale + number direction tested in CI.** InfyVCards repeatedly fixed Arabic / RTL number issues. We add a CI job that renders every page in Arabic + Hindi + Bengali + English and snapshot-tests (a) phone numbers always render LTR even in RTL contexts, (b) currency renders with the correct grouping per locale, (c) dates render in the locale's calendar where applicable.

**Consequences:** Most of these are already in earlier ADRs and tickets — this ADR is the consolidated index that explains *why* those choices were made up-front. New work introduced here: AI integration adapter (T-104), Alumni Business Directory page (T-105), antispam settings (folded into existing tickets), bulk operations on admin list views (folded into Phase 15 hardening).

---

## v2 cleanup notes

> Forward-looking deferrals captured during v3 spec hygiene. Not ADRs (no decision yet) — just reminders so future-us doesn't lose track. Promote to a real ADR when v2 planning starts.

- **Polymorphic comment consolidation.** v3 ships three comment-shaped DocTypes: the generic `Alumni Comment` (polymorphic on `parent_doctype` / `parent_name`, covers Story / News / Notice / Post / Donation Campaign / Candidate); the specialized `Alumni Campaign Comment` (donation-campaign-specific, supports guest commenters with `guest_name`); and `Alumni Candidate Comment` (election-specific, has its own moderation workflow with `published_by` / `published_on`). The two specialized tables predate the generic one and weren't migrated to it for v1 because (a) they each carry one or two fields the generic doesn't, and (b) churning election + donation flows during v3 stabilization is risky. v2 cleanup: extend `Alumni Comment` with optional `guest_name` and per-parent moderation hooks, then migrate Campaign Comment + Candidate Comment data into it and delete the two old tables. Permission rules and serializers will need a coordinated update.
