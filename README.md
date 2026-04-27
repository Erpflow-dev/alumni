# Alumni — a standalone Frappe v16 app for alumni networks

A standalone Frappe app for any school, college, university, or professional institution to run a complete alumni network. **Not a plugin** — a full product with profiles, private messaging, events, jobs, donations (including from non-alumni guests), mentorship, committees with elections, geographic chapters, multilingual public site (RTL ready), and 2FA + social login. Designed to be the best alumni system regardless of institution type, geography, or scale.

> **Frappe v16 only.** This app uses v16-specific features (UUID autoname, data masking, virtual DocTypes, type annotations, scheduler improvements). No backport to v15 / v14.

Two install modes, switched in **Alumni Settings** at first run:

- **🔗 School-Connected mode** — sits on the same Frappe bench as `frappe/education` and ERPNext. Auto-promotes graduating Students to Alumni; links Customer / Sales Invoice / Payment Entry directly; uses Frappe Drive, Mail, Insights when present.
- **🏛️ Standalone mode** — runs on any Frappe site under your own domain or subdomain. No Education or ERPNext required. Built-in lightweight Receivables (Invoice + Payment) replace ERPNext. Storage falls back to Frappe File. Mail uses any SMTP. No Insights dependency — analytics rendered with Chart.js inside the app.

Same DocTypes, same UI, same payments, same messaging, same elections. The only difference is which integrations are wired up — driven by a single **Adapter Layer** (see `INTEGRATIONS.md`).

> **SaaS / multi-tenant?** Yes. One Frappe bench can host many alumni networks via Frappe's native multi-site (one site per institution, true data isolation). See `docs/ops/multi-site-saas.md`. A v2 companion app `alumni_saas` adds super-admin / billing / domain provisioning on top of that pattern.

---

## Built on top of

| App | Purpose | Required? |
|---|---|---|
| `frappe` v16+ | Framework, auth, OAuth, TOTP/2FA, socketio realtime, translations, multi-site | ✅ Always |
| `payments` | Payment Gateway abstraction | ✅ Always |
| [`buzz`](https://github.com/BuildWithHussain/buzz) | Event engine — dynamic ticket types, add-ons, sponsorships, attendee dashboard | ✅ Always |
| `education` | Source of Student records | School-Connected only |
| `erpnext` | Customer / Sales Invoice / Payment Entry | School-Connected only |
| `mail`, `drive`, `insights` | Optional uplifts | Optional |

We **don't rebuild events from scratch** — we sit on Buzz. We **don't rebuild auth** — we use Frappe core OAuth Provider Settings (Google, Facebook, LinkedIn, Apple, Microsoft) and Frappe's TOTP for 2FA. We **don't rebuild realtime** — private messaging runs on Frappe's built-in socketio. Standing on Frappe means every feature works with the rest of the Frappe ecosystem and benefits from Frappe upgrades for free.

---

## Themes

Four production-ready themes ship by default. Switch instantly from **Alumni Settings → Theme**. All themes support both LTR and RTL layouts.

| Theme | Vibe | Suits |
|---|---|---|
| **Heritage** | Serif headlines, warm cream paper, deep accents | Old established schools, universities, traditional institutions |
| **Modern** | Sans-serif, bright neutrals, soft accent, generous whitespace | Tech institutes, modern colleges, startup-spirit alumni groups |
| **Bold** | High-contrast, oversized type, primary-color blocks | Sports schools, performing arts, brand-heavy institutions |
| **Aurora** | Dark mode — deep midnight surfaces, calm neon accent, hairline rules | Universal dark-mode preference; auto-engages when OS prefers dark |

You can add custom themes — see `THEMES.md`. The full component vocabulary, motion guidelines, and accessibility floor are documented in `DESIGN_SYSTEM.md`.

---

## Install

```bash
# Get dependencies
bench get-app payments
bench get-app https://github.com/BuildWithHussain/buzz

# Get this app
bench get-app https://github.com/your-org/alumni
bench --site yoursite.local install-app alumni

# First-run wizard chooses mode + theme + language
bench --site yoursite.local browse  # opens /setup-wizard
```

The wizard asks:

1. Mode: School-Connected or Standalone
2. Institution name, public domain, currency, primary color, logo
3. Theme: Heritage / Modern / Bold
4. Default language + enabled languages (English, Arabic, Hindi, Bengali, Spanish, Portuguese, French, Indonesian)
5. Payment provider: Stripe / Razorpay / HyperPay / PayTabs / Moyasar / bKash / Manual
6. Email: Frappe Mail (if available) or SMTP credentials
7. Storage: Frappe Drive (if available) or Frappe File
8. Verification policy: email required + min documents required + optional phone OTP
9. 2FA gating: mandatory for Admin / Board (default on)

Done. Site reloads at `/alumni` (or your configured subdomain).

---

## What you get

### People & identity
**Profiles & directory** with privacy controls, PII masking, and per-field visibility — **document-based registration verification** (transcripts, ID, degree certs uploaded; admin-reviewed) — **email verification** (mandatory for self-registration) and **optional phone OTP** — **social login** via Google / Facebook / LinkedIn / Apple / Microsoft (uses Frappe core OAuth) — **2FA / TOTP** (mandatory for Admin and Board roles, optional with soft prompts for alumni) — **8 built-in languages with RTL** (full Arabic support out of the box).

### Communication & community
**Private 1:1 messaging** with realtime delivery via Frappe socketio (no Pusher / external broker; messages stay on your server) — recipient preferences (All / Same Batch / Mentees Only / Off), block list, report flow, moderator review queue — **Posts, Stories, News, Notices** with categories and tags — **Comments and Reactions** (polymorphic) — **"Ask the Network" Q&A** (publicly indexable for SEO).

### Money flows
**Memberships** with tiered plans, perks, auto-renewal — **Events** (powered by Buzz, with alumni-specific filters: visibility, chapter scope, passing-year filter, member pricing) — **Job board** + **Volunteer board** — **Donations** with categories (Scholarships, Library, Sports, Emergency Fund…), public moderated comments, **guest donations** so non-registered visitors (parents, friends, corporate matchers) can give and receive a tax receipt without ever entering the alumni network.

### Governance & engagement
**Committees** with categories and designations (President, Treasurer, Secretary, Member, …) — **Full election system** (first-class, not an add-on): nominations with optional fees, board-member review, election symbols (Tree / Star / Bicycle / Compass), candidate profiles with public moderated comments, vote casting with DB-level integrity, optional board-audited validation, automatic results publication and Committee handover — **Geographic chapters** — **Reunion hub** — **Mentorship** with safeguarded student-to-alumni matching — **Outcome surveys** at 1 / 3 / 5 / 10 years post-graduation.

### Mobile experience
**Installable PWA** with offline reading of the directory, own profile, and recent messages — **Web Push notifications** for new messages and event reminders — **Mobile-equal design** (every component designed at 375px first) — bottom-tab navigation on mobile.

### Recognition
**Memorial Wall** with moderated tributes for alumni who passed away, family-designated maintainers, locked privacy permanently — **Distinguished Alumni Awards** with peer nominations, board review, and a public Hall of Fame; recipients earn a permanent profile badge.

### Member value
**Alumni Perks marketplace** — partner businesses (and alumni-owned businesses) offer discounts; alumni redeem via code, URL, or QR — **Digital member card** with QR code, downloadable as PDF/PNG or to Apple Wallet / Google Wallet — partner verification endpoint returns minimal info to confirm alumni status without exposing PII.

### Career & community
**Job referral system** layered on Job Posts — alumni offer to refer applicants internally; referrers earn reputation on hires — **Speaker Bureau** — alumni opt in with topics and availability; current students or admin request talks; auto-creates Alumni Event on accept.

### Discovery
**Networking match suggestions** on the dashboard — 5 alumni picked weekly by deterministic scoring (chapter + batch + city + industry + interests overlap) — "Not interested" mute respected — every score is admin-explainable for transparency.

### Sharing & SEO
**Open Graph + Twitter Card + JSON-LD** on every public surface — donations, candidates, events, jobs, stories all preview richly on WhatsApp / X / LinkedIn — **QR codes** throughout (event tickets, member cards, candidate ballots, profile share, perk redemption) — auto-generated `sitemap.xml` and `robots.txt`.

### Digital Business Cards (vCards)
**Per-alumni vCard builder** at `/v/<slug>` — a polished, single URL alumni share on resumes, email signatures, and WhatsApp — pre-filled from profile data so alumni only edit what's different — **two built-in templates** (Classic Professional and Modern Minimal); **all other templates added by the institution admin** through a portable `.zip` upload pipeline with full validation (no code releases needed for new designs) — sections: services, gallery, testimonials, business hours, custom links, FAQ, embedded iframes — appointments (free or paid via receivables), products with multi-image + tax + PDF receipts, contact form with antispam — **per-alumni custom domain** (`dr-sara-cardiology.com`) gated to active Members with the same Let's Encrypt SSL flow as institution domains — **Public Alumni Business Directory** at `/alumni/businesses` indexing all published alumni-owned-business vCards.

### WhatsApp Business
**Click-to-chat button** on every vCard with one-tap pre-filled messages and click analytics — **WhatsApp Business catalog sync** (optional tier-b) pushes vCard products + services to a connected WhatsApp Business catalog using the institution's existing communication channels — **Standard Storefront** template ships built-in; admin uploads any number of additional templates via the same registry pattern as vCards.

### AI assistance
**Opt-in AI bio drafting + content composer** for vCards, stories, donation campaigns, news articles, award citations — supports **OpenAI, Anthropic, Bedrock, or Custom HTTP** — strict PII minimization (no email, phone, message body, vote history, or other-alumni data ever crosses the boundary) — per-alumni monthly token quota — every generation logged with prompt hash + model + token count for cost tracking — auto-purge logs after 90 days.

### Public site & comms
**Public landing built with Frappe Builder**, fully theme-aware — **Site CMS DocTypes** (FAQ, Testimonials, Image Gallery, Hero Banner) so non-developers maintain the marketing site without touching Builder — **Newsletters** with passing-year, chapter, and country segmentation — **Multi-channel SMS / WhatsApp** with 12 built-in provider drivers (Twilio, Twilio WhatsApp, MessageBird, Vonage, Plivo, Africa's Talking, Wati, Gupshup, 360Dialog, Unifonic, MSG91, SSL Wireless) plus Custom HTTP for any other gateway — **Broadcast composer** sends to All Active / Chapter / Reunion Group / Committee / Class / Department / Membership tier / Custom list / Election eligible voters, with country and passing-year filters, scheduled or immediate, with per-recipient delivery tracking — **Push notifications** via the communication adapter.

### Operations
**10 dashboards** (Network, Membership, Event, Donations, Jobs, Mentorship, Newsletter, Messaging Health, Election Participation, Verification Pipeline) rendered in-app with Chart.js, with one-click Insights deep-link when Insights is installed — **Audit log** on every sensitive operation (vote cast, profile visibility change, donation refund, message reported, verification decided) — **Multi-site SaaS deployment** runbook for hosting many institutions on one bench — **Custom domain + subdomain auto-provisioning** with Let's Encrypt SSL automation, DNS verification flow, and 30-day renewal — **White-labeling** for higher-tier SaaS tenants (hide "Powered by", custom favicon, custom email signature) — **Profile completeness scoring** with admin-configurable rules and gated-onboarding gamification.

> Everything works in both modes. The ten public-listed pages — directory, events, give, news, notices, network Q&A, elections, candidates, jobs, volunteer — are public by default and toggle to alumni-only with one switch each.

---

## Documentation

- [`SPEC.md`](./SPEC.md) — canonical reference: doctypes, fields, workflows, permissions, API (spec v3, ~105 DocTypes)
- [`INTEGRATIONS.md`](./INTEGRATIONS.md) — adapter contract for connecting to other apps (12 adapters: education, receivables, events, storage, mail, analytics, live_class, certificates, communication, messaging, verification, ai)
- [`THEMES.md`](./THEMES.md) — how themes work, how to add a custom one (LTR + RTL, 4 default themes incl. Aurora dark)
- [`DESIGN_SYSTEM.md`](./DESIGN_SYSTEM.md) — frontend design system: components, motion, accessibility, RTL, performance budgets
- [`DECISIONS.md`](./DECISIONS.md) — 54 locked architectural decisions (ADR-001 through ADR-054)
- [`CLAUDE.md`](./CLAUDE.md) — conventions and rules for Claude Code sessions
- [`BUILD_TICKETS.md`](./BUILD_TICKETS.md) — 116-ticket implementation order across 19 phases
- [`CLAUDE_CODE_SETUP.md`](./CLAUDE_CODE_SETUP.md) — how to set up Claude Code with the OpenAEC Frappe Skill Package
- [`CHANGELOG.md`](./CHANGELOG.md) — release history

---

## Migrating from ZaiAlumni or another alumni product?

A migration script (`alumni/migration/from_zaialumni.py`, ticket T-087) reads a ZaiAlumni MySQL export and produces Frappe-importable CSVs for profiles, memberships, donations, campaigns, committees, jobs, stories, and notices. Idempotent + dry-run mode. Field mapping documented in `docs/migration/zaialumni-mapping.md`.

For migrations from custom systems, see the same doc as a template.

---

## License

AGPL-3.0 (matches Frappe and Buzz).

**Network-use note (AGPL §13).** AGPL-3.0 obligates anyone who runs a modified version of this app as a network service to make the corresponding source available to the users it serves. The forthcoming v2 companion app **`alumni_saas`** (per ADR-035) is the multi-tenant SaaS surface and inherits the same obligation — institutions deploying it must keep their source available to the alumni they serve, regardless of whether those alumni log in. This is enforceable per AGPL §13 and is why we chose AGPL over MIT / Apache for an alumni-network product (we want institutional deployments to remain in the open ecosystem). An operator's compliance checklist will live at `docs/ops/agpl-saas.md` alongside the v2 plan.
