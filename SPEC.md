# SPEC.md — alumni canonical reference

The authoritative spec. Code and SPEC must agree; fix the wrong one.

> **Frappe v16 only.** Use type annotations on every controller method. UUID autoname for opaque IDs (audit, polymorphic, votes). Format-string autoname for human-readable IDs.

> **Spec version:** v3 — adds private messaging, document-based verification, full election system, donation categories + comments + guest donations, taxonomy for News/Notices, social login, 2FA, multilingual/RTL, and a documented multi-tenancy story. These were added after a feature-parity review against ZaiAlumni and several incumbent alumni products.

---

## §00 Module overview

`alumni` is a standalone Frappe v16 app. Two install modes selected at first-run wizard, switchable in `Alumni Settings`.

**Modes:**
- `school_connected` — auto-promote from `frappe/education`, payments through ERPNext, analytics linkable to Insights.
- `standalone` — self-registration + manual + CSV import; lightweight built-in receivables; in-app Chart.js analytics.

**Multi-tenancy:** one Frappe site = one institution (per ADR-010). To run a SaaS — many institutions on one bench — use Frappe's native multi-site (per ADR-035). A v2 companion app `alumni_saas` adds super-admin / billing on top; not in v1.

**Required external apps (both modes):** `frappe v16+`, `payments`, `buzz`.

**Reads:** `tabStudent` (school_connected), `tabBuzz Event` (always, via adapter).
**Writes:** ERPNext `Customer`/`Sales Invoice`/`Payment Entry` (school_connected) OR `Alumni Invoice`/`Alumni Payment` (standalone). Always: `Buzz Event` and related (via events adapter).

---

## §01 Roles

| Role | Inherits | Can |
|---|---|---|
| Guest | — | Public site only; donate to public campaigns; view public Q&A; view candidate profiles in active elections |
| Alumni | Guest | Edit own profile, post pending content, buy memberships/tickets, donate, message peers, RSVP, request mentorship as mentee, ask network, sign up for volunteering, join chapter, vote in elections, comment on candidates and campaigns |
| Alumni Mentor | Alumni | Accept mentorship requests, log sessions |
| Alumni Moderator | Alumni | Approve/reject pending content (Stories, Job Posts, News, Notices, Network Questions) |
| Alumni Board Member | Alumni | Oversee elections — review nominations, approve final candidate list, audit votes, publish results |
| Alumni Admin | Moderator | Full management of all DocTypes including Settings, Newsletters, Memberships, Themes, Elections, CMS pages, Donation Campaigns |
| System Manager | Admin | Frappe-level (break-glass) |

> **Note:** Frappe v16 supports per-site Two-Factor Authentication (TOTP / Google Authenticator). Per ADR-036, 2FA is **mandatory** for Admin / Board Member / System Manager roles and **optional** (admin-toggleable as a soft requirement) for Alumni.

---

## §02 Lifecycle

### School-Connected mode
1. **Auto-promote** nightly job: Students with completed final term + zero outstanding fees → Alumni Profile (Draft) → invitation email next morning.
2. **Manual conversion**: admin button on Student record.
3. **Self-registration**: public form for pre-deployment graduates (with verification documents per ADR-032).

### Standalone mode
1. **Self-registration**: public form, requires email verification + one or more verification documents → admin approval workflow.
2. **Manual create**: admin enters individual records (with optional welcome email + temp password).
3. **CSV import**: admin bulk-imports old yearbook data.
4. **Past Student stub**: admin enters historical alumni in `Past Student` DocType, then converts in batches.

### Alumni Profile state machine
`Draft → Pending (Email Verified) → Pending (Docs Submitted) → Active → Suspended | Deceased`

The two Pending substates exist so admins can see whether a self-registered profile has cleared each gate. School-Connected auto-promoted profiles skip Pending entirely → land at Active (Draft only if `auto_promote_requires_review` is set).

---

## §03 DocType inventory

> Counts updated for spec v3 (final revision Apr 2026): 33 → ~103 first-class DocTypes after the full v3 review (channels per ADR-040, domains per ADR-041, completeness per ADR-044, memorial+awards per ADR-045, perks per ADR-046, referrals+speakers per ADR-047, match mute per ADR-048, vCards + WhatsApp Store + AI logs per ADR-050/053/054).

### Identity & Profile (4)
1. Alumni Profile
2. Alumni Career Entry (child)
3. Alumni Education Entry (child)
4. Alumni Verification Document (child) — uploaded transcripts, ID, degree certs

### Membership (3)
5. Alumni Membership Plan
6. Alumni Membership Perk (child)
7. Alumni Membership

### Events (Buzz wrappers, 2)
8. Alumni Event Wrapper *(thin wrapper over Buzz Event)*
9. Alumni Event Category

### Jobs & Volunteering (5)
10. Alumni Job Category
11. Alumni Job Post
12. Alumni Job Application
13. Alumni Volunteer Opportunity
14. Alumni Volunteer Signup

### Content (8)
15. Alumni Story
16. Alumni Story Category
17. Alumni News Article
18. Alumni News Category
19. Alumni News Tag (child)
20. Alumni Notice
21. Alumni Notice Category
22. Alumni Post (short feed updates)

### Social engagement, polymorphic (2 — UUID autoname)
23. Alumni Comment (polymorphic)
24. Alumni Reaction (polymorphic)

### Network Q&A (2)
25. Alumni Network Question
26. Alumni Network Answer (child)

### Private Messaging (3) — **NEW in v3**
27. Alumni Message Thread
28. Alumni Message
29. Alumni Message Read Receipt (child)

### Donations (5)
30. Alumni Donation Category — **NEW in v3** (groups campaigns: Scholarships, Library, Sports, etc.)
31. Alumni Donation Campaign
32. Alumni Donation Tier (child)
33. Alumni Campaign Comment — **NEW in v3** (engagement on campaigns)
34. Alumni Donation (supports `is_guest`, `guest_email`, `guest_name` per ADR-034)

### Committees & Elections (12) — **EXPANDED in v3** (was 3)
35. Alumni Committee Category
36. Alumni Committee
37. Alumni Committee Designation — positions like President, Treasurer, Secretary
38. Alumni Committee Member (child)
39. Alumni Committee Meeting
40. Alumni Election
41. Alumni Election Position (child of Election — which designations are up this election)
42. Alumni Election Symbol — Bicycle, Tree, Star, etc., assigned to candidates
43. Alumni Nomination — alumni applies to be candidate, may include nomination fee
44. Alumni Candidate — approved nominee in an election (created when Nomination is approved)
45. Alumni Candidate Comment — public engagement on candidate profile (moderated)
46. Alumni Vote — UUID autoname, audited, optionally anonymous
47. Alumni Election Result (child of Election)

### Chapters & Reunions (3)
48. Alumni Chapter
49. Alumni Chapter Member (child)
50. Alumni Reunion Group

### Mentorship (2)
51. Alumni Mentorship Request
52. Alumni Mentorship Session

### Outcomes (4)
53. Alumni Outcome Survey Template
54. Alumni Survey Question (child)
55. Alumni Outcome Survey Response
56. Alumni Survey Answer (child)

### Site CMS (4) — **NEW in v3**
57. Alumni FAQ
58. Alumni Testimonial
59. Alumni Image Gallery Item
60. Alumni Hero Banner — for landing-page rotating banners

### Comms (4 — 1 Frappe extension + 3 NEW v3)
61. Alumni Newsletter (custom fields on Frappe Newsletter for segmentation)
62. Alumni Communication Channel — **NEW v3** per ADR-040 — SMS / WhatsApp provider configurations
63. Alumni Broadcast — **NEW v3** per ADR-040 — bulk SMS / WhatsApp sends to alumni segments
64. Alumni Broadcast Log Entry (child) — **NEW v3** — per-recipient delivery tracking

### Configuration & audit (3)
65. Alumni Theme (read-only, populated from `themes/` folders)
66. Alumni Settings (Single)
67. Alumni Audit Log (UUID autoname)

### Standalone-only (5)
68. Past Student
69. Alumni Department (Education Department stub)
70. Alumni Invoice
71. Alumni Invoice Item (child)
72. Alumni Payment

### SaaS / Multi-tenancy (1) — **NEW v3** per ADR-041
73. Alumni Tenant Domain — subdomain + custom domain provisioning, DNS verification, SSL state

### Recognition & Memorial (4) — **NEW v3** per ADR-045
74. Alumni Memorial Tribute (child of Profile when status=Deceased)
75. Alumni Award (catalog of award types — Distinguished, Hall of Fame, etc.)
76. Alumni Award Recipient (joins Award + Profile + year + citation)
77. Alumni Memorial Maintainer (child of Profile — family / authorized peers who can update memorial page)

### Member Perks (3) — **NEW v3** per ADR-046
78. Alumni Perk Category
79. Alumni Perk
80. Alumni Perk Redemption (audit trail + QR-scan log)

### Career & Speaker (3) — **NEW v3** per ADR-047
81. Alumni Job Referral
82. Alumni Speaker Topic (child of Profile — alumni opt in)
83. Alumni Speaker Request

### Networking (1) — **NEW v3** per ADR-048
84. Alumni Match Mute (alumni + muted_alumni — privacy-respecting "not interested")

### Digital Business Cards / vCards (15) — **NEW v3** per ADR-050 + ADR-053
85. Alumni VCard (1:1 with Alumni Profile, optional)
86. Alumni VCard Template (read-only, populated from `vcard_templates/` folders — admin uploads new ones via the registry per ADR-053; v1 ships 2: "Classic Professional", "Modern Minimal")
87. Alumni VCard Social Link (child)
88. Alumni VCard Service (child — supports tax fields per ADR-054 lesson #13)
89. Alumni VCard Gallery Item (child — Gallery Category support, image-cropper enforced per ADR-054 lesson #2)
90. Alumni VCard Gallery Category (child of vCard or top-level for shared categories)
91. Alumni VCard Testimonial (child)
92. Alumni VCard Iframe (child)
93. Alumni VCard Business Hour (child)
94. Alumni VCard Custom Link (child — generic "Add link" surface for arbitrary buttons)
95. Alumni VCard FAQ (child)
96. Alumni VCard Inquiry — contact-form submissions (filtered by `Alumni Settings.blocked_email_domains` + keyword regex per ADR-054 lesson #8)
97. Alumni VCard Appointment — bookable time slots, optionally paid via receivables adapter
98. Alumni VCard Product — items / services for sale (with tax fields)
99. Alumni VCard Product Order — purchase records via receivables adapter (with tax breakdown + PDF receipt)

### WhatsApp Store integration (3) — **NEW v3** per ADR-052 + ADR-053
100. Alumni WhatsApp Store Template (read-only, populated from `whatsapp_templates/` folders — admin uploads via registry; v1 ships 1: "Standard Storefront")
101. Alumni VCard WhatsApp Catalog Sync Log (audit trail of catalog pushes to Meta WhatsApp Business)
102. Alumni VCard Visit (analytics, aggregated daily for privacy; tracks `whatsapp_click_count`, view count, view limit per ADR-054 lesson #7)

### AI assistance (1) — **NEW v3** per ADR-054 lesson #10
103. Alumni AI Generation Log (audit trail: who asked AI to draft what, prompt hash, model, token count)

> One vCard per alumni in v1. Multiple vCards / brands per alumni deferred to v2.

### What we do NOT create (deferred to Buzz / payments / Frappe core)
- Buzz Event ✕ (we wrap it)
- Buzz Event Ticket Type ✕ (Buzz owns)
- Buzz Event Add On ✕ (Buzz owns)
- Buzz Event Booking ✕ (Buzz owns)
- Buzz Event Sponsorship Tier ✕ (Buzz owns)
- Payment Gateway records ✕ (frappe/payments owns)
- OAuth Provider Settings ✕ (Frappe core owns — see ADR-037)
- Translation ✕ (Frappe core handles, see ADR-038)
- Two Factor Settings ✕ (Frappe core owns)

---

## §04 Schemas — top-level fields

> Only fields that are new, changed, or non-obvious are detailed below. Trivial fields (description, is_active flags, etc.) are omitted for brevity — see the controller stubs in source.

### Alumni Profile
- `name` autoname `ALU-{passing_year}-{####}`
- `student` Link → Student (school_connected only)
- `past_student` Link → Past Student (standalone only)
- `full_name` Data req
- `profile_photo` Attach Image (storage adapter)
- `passing_year` Int req
- `department` Link → (Education Department | Alumni Department, depending on mode)
- `section` Data
- `roll_number` Data
- `email` Data unique req
- `email_verified` Check
- `email_verified_on` Datetime
- `phone` Data — **v16 data masking applied** when displayed to non-owner
- `phone_verified` Check
- `whatsapp` Data — **masked**
- `current_city` Data
- `current_country` Link → Country
- `current_employer`, `current_designation` Data
- `industry` Link → Industry Type (or Alumni Industry stub)
- `career_history` Table → Alumni Career Entry
- `education_history` Table → Alumni Education Entry
- `verification_documents` Table → Alumni Verification Document — **NEW v3**
- `verification_status` Select: Not Submitted / Pending Review / Verified / Rejected
- `linkedin_url` Data
- `bio` Long Text
- `willing_to_mentor` Check
- `mentorship_topics` Small Text
- `privacy_visibility` / `email_visibility` / `phone_visibility` Select: Public / Alumni-only / Members-only / Hidden
- `messaging_preference` Select: All Alumni / Same Batch / Mentees Only / Off — **NEW v3** (controls who can DM)
- `newsletter_subscribed` Check default 1
- `chapters` Table → Alumni Chapter Member
- `status` Select: Draft / Pending Email / Pending Docs / Active / Suspended / Deceased
- `verified_by` Link → User
- `verified_on` Datetime
- `customer_id` Data (opaque from receivables adapter)
- `last_login` Datetime virtual
- `code_of_conduct_accepted_on` Datetime
- `2fa_enabled` Check (mirrors Frappe User flag for display)
- `social_login_provider` Select (read-only): Google / Facebook / LinkedIn / Apple / None
- `preferred_language` Link → Language
- `preferred_theme` Link → Alumni Theme — **NEW v3** (overrides institution default per ADR-043)
- `profile_completeness_percent` Int virtual — **NEW v3** (0–100, computed per ADR-044)
- `interests` Data — **NEW v3** (comma-separated tags; informs match scoring per ADR-048)
- `skills` Data — **NEW v3** (comma-separated; LinkedIn-style)
- `referral_reputation_points` Int default 0 — **NEW v3** (per ADR-047, increments on each accepted referral that became a hire)
- `speaker_topics` Table → Alumni Speaker Topic — **NEW v3** (per ADR-047, opt-in)
- `memorial_maintainers` Table → Alumni Memorial Maintainer — **NEW v3** (used only when status=Deceased per ADR-045)
- `family_contact_email` Data — **NEW v3** (used to notify next-of-kin when status changes to Deceased)
- `is_alumni_owned_business_owner` Check — **NEW v3** (signals the alumni has a business to optionally list as a perk)
- `push_subscription` Long Text — **NEW v3** (encrypted JSON; PWA Web Push subscription per ADR-042)
- `public_profile_slug` Data — **NEW v3** (URL-safe slug, optional, used by `/u/<slug>` short-share URL with QR code per ADR-049; null = no public profile page)

Controller signature (v16):
```python
class AlumniProfile(Document):
    def validate(self) -> None: ...
    def before_save(self) -> None: ...
    def on_update(self) -> None: ...
```

### Alumni Verification Document (child) — NEW v3
- `document_type` Select: Transcript / Degree Certificate / National ID / Passport / Yearbook Page / Other
- `file` Attach req (private — storage adapter, never public)
- `notes` Small Text
- `reviewed_by` Link → User
- `reviewed_on` Datetime
- `review_decision` Select: Pending / Accepted / Rejected
- `rejection_reason` Small Text

### Alumni Membership Plan
- `name` autoname `MP-{####}`
- `plan_name` Data req
- `description` Text Editor
- `price` Currency req
- `currency` Link → Currency
- `duration_months` Int (0 = lifetime)
- `perks` Table → Alumni Membership Perk
- `item_code` Data (filled by receivables.ensure_item or no-op)
- `is_active` Check

### Alumni Membership
- `alumni` Link req
- `plan` Link req
- `start_date` / `expiry_date` Date
- `auto_renew` Check (cosmetic in v1; honored in v2 when recurring is enabled)
- `invoice_id` Data (opaque from receivables)
- `status` Select: Pending Payment / Active / Expired / Cancelled / Refunded
- `card_pdf` Attach (storage adapter)

### Alumni Event Wrapper *(1:1 with Buzz Event)*
- `name` autoname `EVT-{YYYY}-{####}`
- `buzz_event` Link → Buzz Event unique req
- `category` Link → Alumni Event Category
- `visibility` Select: Public / Alumni-only / Members-only
- `chapter` Link → Alumni Chapter (optional, for chapter-only events)
- `member_pricing_enabled` Check
- `passing_year_filter_min` Int
- `passing_year_filter_max` Int
- `organizer_alumni` Link → Alumni Profile
- `moderator_approved` Check
- `featured` Check
- `cover_image_override` Attach Image (overrides Buzz's cover for our themed display)

> Ticket types, add-ons, sponsorships, bookings, payments — all in Buzz. Read via `events.list_ticket_types(buzz_event)` etc.

### Alumni Donation Category — NEW v3
- `name` autoname `DCAT-{####}`
- `category_name` Data req unique
- `description` Small Text
- `icon` Data (icon class or emoji)
- `cover_image` Attach Image
- `is_active` Check default 1

### Alumni Donation Campaign
- `name` autoname `CAM-{YYYY}-{####}`
- `category` Link → Alumni Donation Category
- `title` Data req
- `cover_image` Attach Image
- `summary` Small Text
- `description` Text Editor (Markdown OK)
- `goal_amount` Currency req
- `currency` Link → Currency
- `raised_amount` Currency (computed by `tasks.refresh_campaign_totals`)
- `start_date` / `end_date` Date
- `tiers` Table → Alumni Donation Tier
- `allow_guest_donations` Check default 1 — **NEW v3 (per ADR-034)**
- `allow_comments` Check default 1
- `match_multiplier` Float default 0 (corporate match)
- `match_cap` Currency (cap on matched amount)
- `featured` Check
- `status` Select: Draft / Running / Paused / Expired / Completed

### Alumni Campaign Comment — NEW v3
- `name` autoname `uuid`
- `campaign` Link → Alumni Donation Campaign req
- `commenter_alumni` Link → Alumni Profile (null if guest)
- `guest_name` Data (only if commenter_alumni is null)
- `body` Small Text req (≤500 chars)
- `is_published` Check default 0 (admin moderates)
- `parent_comment` Link → Alumni Campaign Comment (allows 1-level threading)
- `commented_on` Datetime auto

### Alumni Donation
- `name` autoname `DON-{YYYY}-{######}`
- `donor` Link → Alumni Profile (null if anonymous OR guest)
- `is_guest` Check — **NEW v3** (per ADR-034)
- `guest_name` Data (only if is_guest)
- `guest_email` Data (only if is_guest)
- `anonymous` Check (alumni donor wishing to be anonymous publicly)
- `donor_alias` Data
- `campaign` Link → Alumni Donation Campaign (null = general fund)
- `tier` Link → Alumni Donation Tier
- `amount` Currency req
- `currency` Link → Currency
- `recurring` / `recurring_interval` / `next_charge_date` (v2 reserved)
- `payment_method` Select: Card / Bank / Wallet / Manual
- `invoice_id` Data
- `payment_id` Data
- `tax_receipt_pdf` Attach
- `donor_message` Small Text
- `match_amount` Currency (amount added by corporate match)
- `status` Select: Pending / Completed / Refunded / Failed

> Guests donate without registering. Their `Alumni Donation` record is keyed only by `guest_email`; tax receipt is emailed to that address. They never gain access to the rest of the alumni network.

### Alumni Network Question
- `name` autoname `Q-{YYYY}-{######}`
- `title` Data req
- `body` Text Editor
- `category` Select: Career / Education / Industry / Travel / General / Other
- `country_filter` / `industry_filter` Link (optional)
- `asker` Link → Alumni Profile
- `is_public` Check (per ADR-022, public-site visible if ticked)
- `status` Select: Open / Answered / Closed
- `answers` Table → Alumni Network Answer
- `views` Int

### Alumni Mentorship Request
- `student` Link → Student (school_connected) OR `external_requester_email` Data (standalone)
- `student_grade` Int (snapshot)
- `mentor` Link → Alumni Profile req
- `topic` Data req
- `message` Small Text (200 char)
- `status` Select: Pending / Accepted / Declined / Auto-Declined / Completed
- `requested_on` / `responded_on` Datetime
- `auto_decline_after` Date
- `coc_accepted_by_mentor` / `coc_accepted_by_student` Check

### Alumni Audit Log
- `name` autoname `uuid`
- `event_type` Data req (e.g. `mentorship_session_flagged`, `donation_refunded`, `profile_visibility_changed`, `vote_cast`, `nomination_approved`, `message_reported`, `broadcast_sent`)
- `actor_user` Link → User
- `target_doctype` Data
- `target_name` Data
- `payload_json` JSON (sanitized — no PII)
- `occurred_at` Datetime auto

### Alumni Communication Channel — NEW v3 (per ADR-040)
- `name` autoname `CCH-{####}`
- `channel_name` Data req unique (e.g. "Saudi Local SMS — Unifonic", "WhatsApp Business — Wati")
- `channel_type` Select: SMS / WhatsApp / Both — req
- `provider` Select: Twilio / Twilio WhatsApp / MessageBird / Vonage / Plivo / Africa's Talking / Wati / Gupshup / 360Dialog / Unifonic / MSG91 / SSL Wireless / Custom HTTP — req
- `auth_credentials` Password (encrypted; provider-specific JSON: api_key, api_secret, account_sid, sender_id, etc.)
- `from_address` Data (sender ID for SMS, WhatsApp Business number for WA)
- `default_for_country` Link → Country (auto-route recipients with matching country code; null = no auto-routing)
- `is_default` Check (one per channel_type max — controller enforces)
- `daily_quota` Int default 0 (0 = unlimited)
- `sends_today` Int (computed; reset by daily job)
- `sends_this_month` Int (computed)
- `cost_per_send` Currency (informational; for budget dashboard)
- `is_active` Check default 1
- `last_used_at` Datetime
- `last_error` Small Text (latest error message, if any)
- `webhook_url` Data (delivery-receipt callback; auto-populated when channel saved — `/api/method/alumni.api.communication_webhook?channel=<name>`)

> Custom HTTP provider exposes additional fields (`http_url`, `http_method`, `http_auth_header`, `http_payload_template` Jinja, `http_response_id_path`) so any HTTP-API gateway can be wired without code changes.

### Alumni Broadcast — NEW v3 (per ADR-040)
- `name` autoname `BC-{YYYY}-{######}`
- `title` Data req (admin-only label, e.g. "2026 Reunion Reminder — All 2018 Batch")
- `channel` Link → Alumni Communication Channel (optional — falls back to default-by-country routing if null)
- `medium` Select: SMS / WhatsApp / Both (controls which channel pool to draw from when `channel` is null)
- `message_body` Long Text req (≤1600 chars for SMS concatenation; WhatsApp per-template limits)
- `whatsapp_template_name` Data (required when WhatsApp Business is the medium and recipients haven't messaged in 24h)
- `whatsapp_template_variables` JSON (substitutions for the template, e.g. `{"1": "{{full_name}}", "2": "{{passing_year}}"}`)
- `segment_type` Select: All Active Alumni / Chapter / Reunion Group / Committee / Class / Department / Membership Tier / Custom List / Election Eligible Voters — req
- `segment_filter` JSON (segment-specific params: `{chapter}`, `{passing_year, section}`, `{committee}`, `{department}`, `{plan}`, `{file_id}` for uploaded CSV, `{election}`)
- `min_passing_year` / `max_passing_year` Int (additional filter, applies to all segment types)
- `country_filter` Link → Country (additional filter — only alumni in this country)
- `respect_messaging_preference` Check default 1 (skip alumni whose `messaging_preference = Off`)
- `respect_phone_verified` Check default 1 (skip alumni with unverified phone — protects against spam-trap numbers)
- `scheduled_for` Datetime (null = send immediately on submit)
- `recipients_count` Int (computed at submit; preview shown in admin UI before send)
- `sent_count` / `delivered_count` / `failed_count` Int (live counters)
- `status` Select: Draft / Preview / Scheduled / Queued / Sending / Sent / Failed / Cancelled
- `created_by` Link → User
- `submitted_at` / `started_at` / `completed_at` Datetime
- `log_entries` Table → Alumni Broadcast Log Entry

> Permission: Admin only (Moderator can read drafts but not submit). Submitting a Broadcast writes one Audit Log entry per send; the body is hashed (not stored plaintext) in the audit payload.

### Alumni Broadcast Log Entry (child) — NEW v3
- `recipient_alumni` Link → Alumni Profile
- `recipient_phone` Data (snapshot at send time — alumni may change number later)
- `delivery_status` Select: Queued / Sent / Delivered / Read / Failed / Skipped
- `skip_reason` Small Text (only when status=Skipped: "messaging_preference=Off", "phone unverified", "no phone on file", "country mismatch", "quota exceeded")
- `provider_message_id` Data (id returned by the provider, used for delivery receipts)
- `error_message` Small Text
- `sent_at` / `delivered_at` Datetime
- `attempt_count` Int (1, 2, 3 — capped at 3 retries)

### Alumni Theme
- `name` Data (matches folder ID, e.g. `heritage`, `modern`, `bold`, `aurora`)
- `display_name` Data (e.g. `Heritage`)
- `description` Small Text
- `author` Data
- `version` Data
- `parent_theme` Link → Alumni Theme (for inherited themes)
- `is_active` Check
- `preview_image` Attach Image
- `supports_rtl` Check — **NEW v3**
- `color_scheme` Select: Light / Dark / Auto — **NEW v3** (Auto = follow OS `prefers-color-scheme`)

Read-only — populated from disk. Four themes ship by default per ADR-043: Heritage / Modern / Bold (light) + Aurora (dark).

### Alumni Tenant Domain — NEW v3 (per ADR-041)
- `name` autoname `DOM-{####}`
- `domain` Data req unique (e.g. `alumni.aramco-school.edu.sa`, `mit.alumni-saas.com`)
- `domain_type` Select: Subdomain / Custom Domain
- `tenant_site` Data (the Frappe site name — used by `bench setup nginx` regeneration)
- `is_primary` Check (one per site; primary domain is what `frappe.utils.get_url` returns)
- `redirect_to_primary` Check (if 1, this domain 301s to primary instead of serving)
- `verification_status` Select: Pending DNS / DNS Verified / SSL Pending / Live / Failed / Expired
- `dns_token` Data (the unique TXT-record value the admin must add to prove control)
- `cname_target` Data (auto-populated, what the admin's CNAME should point to)
- `ssl_status` Select: Not Issued / Pending / Issued / Renewing / Failed
- `ssl_issued_on` / `ssl_expires_on` Datetime
- `ssl_provider` Select: Let's Encrypt / Custom Upload / None (Let's Encrypt is default)
- `ssl_custom_cert` Long Text (PEM, only when `ssl_provider = Custom Upload`)
- `ssl_custom_key` Password (PEM private key, only when `ssl_provider = Custom Upload`)
- `last_verified_at` Datetime
- `last_failure_reason` Small Text
- `created_by` Link → User
- `notes` Small Text

> Lifecycle: admin creates → status `Pending DNS` → hourly `tasks.verify_pending_domains()` checks DNS → on success → status `SSL Pending` → triggers Let's Encrypt → on success → status `Live`. Cert renewal scheduled 30d before `ssl_expires_on` via `tasks.renew_expiring_certs()` daily.

### Alumni Memorial Tribute (child) — NEW v3 (per ADR-045)
- `tributer_alumni` Link → Alumni Profile (or null if guest)
- `guest_name` Data (only if tributer_alumni is null)
- `relationship` Data (e.g., "Classmate, 1998", "Daughter", "Colleague at Aramco")
- `tribute_text` Small Text req (≤500 chars)
- `tribute_date` Date auto
- `is_published` Check default 0 (Moderator approves)

### Alumni Memorial Maintainer (child of Profile) — NEW v3
- `user` Link → User
- `relationship` Data (e.g., "Spouse", "Sibling", "Designated by family")
- `granted_on` Datetime
- `granted_by` Link → User

### Alumni Award — NEW v3 (per ADR-045)
- `name` autoname `AWD-{####}`
- `award_name` Data req unique (e.g., "Distinguished Alumni Award", "Young Achiever", "Hall of Fame")
- `description` Text Editor
- `cycle` Select: Annual / Biannual / Ad-hoc
- `criteria` Text Editor
- `selection_method` Select: Peer Nomination + Board Review / Board Direct / Public Vote
- `is_active` Check default 1
- `cover_image` Attach Image
- `category` Select: Career / Service / Academic / Lifetime / Sports / Arts / Other
- `confers_permanent_badge` Check default 0 (if 1, recipients get a profile badge forever)

### Alumni Award Recipient — NEW v3 (per ADR-045)
- `name` autoname `AR-{YYYY}-{####}`
- `award` Link → Alumni Award req
- `alumni` Link → Alumni Profile req
- `year` Int req
- `citation` Small Text req (the public citation, what's read at the ceremony)
- `photo` Attach Image (optional ceremony photo)
- `nominated_by` Link → Alumni Profile (audit; null if Board Direct)
- `is_published` Check default 0

> Public Hall of Fame page at `/alumni/hall-of-fame` filters by award_name and year; renders citations; recipient profiles get a permanent badge in the directory if `award.confers_permanent_badge=1`.

### Alumni Perk Category — NEW v3 (per ADR-046)
- `name` autoname `PCAT-{####}`
- `category_name` Data req unique (e.g., "Travel", "Dining", "Education", "Tech", "Health", "Local Business", "Alumni-Owned")
- `icon` Data
- `is_active` Check default 1
- `sort_order` Int

### Alumni Perk — NEW v3 (per ADR-046)
- `name` autoname `PRK-{YYYY}-{####}`
- `title` Data req
- `category` Link → Alumni Perk Category
- `partner_name` Data req
- `partner_logo` Attach Image
- `partner_website` Data
- `description` Text Editor
- `discount_value` Data (e.g., "15% off", "Free first month", "₹500 off ₹2000")
- `redemption_type` Select: Code / URL / Show Member Card / Contact Partner
- `redemption_code` Data (only if redemption_type=Code)
- `redemption_url` Data (only if redemption_type=URL)
- `eligible_audience` Select: All Active Alumni / Members Only / Specific Tier / Specific Chapter
- `eligible_tier` Link → Alumni Membership Plan (only if eligible_audience=Specific Tier)
- `eligible_chapter` Link → Alumni Chapter (only if eligible_audience=Specific Chapter)
- `geographic_filter_country` Link → Country (optional)
- `valid_from` / `valid_to` Date req
- `redemption_limit_per_alumni` Int default 0 (0 = unlimited)
- `total_redemption_limit` Int default 0 (0 = unlimited; tracks budget for partner-funded promos)
- `current_redemption_count` Int (computed)
- `is_alumni_owned` Check (highlight if the partner is itself an alumni-owned business)
- `featured` Check
- `status` Select: Draft / Active / Paused / Expired
- `is_published` Check default 0 (Moderator approves new perks)

### Alumni Perk Redemption — NEW v3 (per ADR-046)
- `name` autoname `PR-{YYYY}-{######}`
- `perk` Link → Alumni Perk req
- `alumni` Link → Alumni Profile req
- `redeemed_at` Datetime auto
- `redemption_method` Select: Code Reveal / URL Click / QR Scan / Partner Lookup
- `partner_scanned_token` Data (only when partner verified the QR)
- `notes` Small Text

### Alumni Job Referral — NEW v3 (per ADR-047)
- `name` autoname `REF-{YYYY}-{######}`
- `job_post` Link → Alumni Job Post req
- `referrer_alumni` Link → Alumni Profile req (the alumni who posted or has internal access)
- `referee_alumni` Link → Alumni Profile (the alumni asking for referral; null if external candidate)
- `referee_external_email` Data (only if referee_alumni is null)
- `referee_external_resume` Attach (only if external)
- `referee_message` Small Text req (the candidate's pitch to the referrer)
- `referrer_response` Small Text (referrer's reply or referral note)
- `status` Select: Requested / Accepted / Declined / Submitted / Hired / Not Hired / Withdrawn
- `requested_on` / `responded_on` / `submitted_on` / `outcome_on` Datetime
- `outcome_notes` Small Text

> When status moves to `Hired`, referrer's `Alumni Profile.referral_reputation_points` increments by `Alumni Settings.referral_points_per_hire` (default 10).

### Alumni Speaker Topic (child of Profile) — NEW v3 (per ADR-047)
- `topic` Data req
- `level` Select: Introductory / Intermediate / Advanced / Any
- `format` Select: In-Person / Virtual / Both
- `travel_willingness` Select: Local Only / Regional / National / International
- `honorarium_expectation` Select: Free / Negotiable / Fixed
- `fixed_honorarium_amount` Currency (only if honorarium_expectation=Fixed)
- `is_active` Check default 1

### Alumni Speaker Request — NEW v3 (per ADR-047)
- `name` autoname `SPK-{YYYY}-{######}`
- `requester_alumni` Link → Alumni Profile (or null for school-connected student requests)
- `student` Link → Student (school_connected only; null otherwise)
- `requester_external_email` Data (fallback)
- `speaker_alumni` Link → Alumni Profile req
- `topic_requested` Data req
- `event_title` Data req
- `proposed_date` Datetime req
- `expected_audience_size` Int
- `format` Select: In-Person / Virtual / Hybrid
- `venue` Data
- `budget` Currency
- `message` Text Editor req
- `status` Select: Sent / Accepted / Declined / Counter-Proposed / Withdrawn / Completed
- `counter_proposal` Small Text
- `responded_on` Datetime
- `linked_event` Link → Alumni Event Wrapper (auto-created on Accepted)

### Alumni Match Mute — NEW v3 (per ADR-048)
- `name` autoname `uuid`
- `viewer_alumni` Link → Alumni Profile req
- `muted_alumni` Link → Alumni Profile req
- `muted_on` Datetime auto
- `unique` index on (viewer_alumni, muted_alumni)

> Used by the `get_match_suggestions_for(alumni)` API to skip pairs where the viewer clicked "Not interested". Never visible to the muted alumni.

### Alumni VCard — NEW v3 (per ADR-050)
- `name` autoname `VCARD-{####}`
- `alumni` Link → Alumni Profile req unique (1:1 in v1)
- `slug` Data req unique-per-site (URL-safe; 3–48 chars; reserved-word list blocked)
- `template` Link → Alumni VCard Template req (defaults to "Classic Professional")
- `is_active` Check default 1
- `is_published` Check default 0 (draft until alumni publishes)
- `password_protected` Check default 0
- `access_password` Password (only when password_protected=1)
- `dynamic_accent_color` Color (overrides template default; tokenized at render)
- `dynamic_button_style` Select: Pill / Square / Rounded / Sharp
- `dynamic_font` Link → Alumni VCard Font (registry with safe-listed Google Fonts)
- **Hero / Cover**
  - `cover_image` Attach Image (cropped 16:9 by uploader per ADR-054 lesson #2)
  - `cover_video_url` Data (YouTube / Vimeo URL — embedded with privacy mode; auto-generates poster image)
  - `profile_photo` Attach Image (cropped 1:1; falls back to Alumni Profile.profile_photo)
  - `display_name` Data (fallback: Alumni Profile.name)
  - `tagline` Data (≤80 chars)
  - `current_role` Data (fallback: profile employer + designation)
  - `bio` Long Text (rich text; sanitized)
  - `bio_drafted_by_ai` Check (audit flag — set when AI helped draft per ADR-054 lesson #10)
- **Contact**
  - `display_email` Data
  - `display_phone` Data
  - `display_alt_phone` Data
  - `whatsapp_number` Data — per ADR-052
  - `whatsapp_business_message` Small Text — pre-filled greeting, per ADR-052
  - `whatsapp_business_account_id` Data — for tier-b WhatsApp Business per ADR-052
  - `whatsapp_catalog_sync_enabled` Check default 0
  - `address` Small Text
  - `location_map_embed` Long Text (sanitized iframe URL only — Google Maps / OSM)
  - `display_website` Data
- **Sections (visibility toggles)**
  - `show_social_links` Check default 1
  - `show_services` Check default 1
  - `show_gallery` Check default 1
  - `show_testimonials` Check default 0
  - `show_business_hours` Check default 0
  - `show_appointments` Check default 0
  - `show_products` Check default 0
  - `show_blog` Check default 0
  - `show_iframes` Check default 0
  - `show_custom_links` Check default 0
  - `show_faq` Check default 0
  - `enable_inquiry_form` Check default 1
  - `enable_whatsapp_store` Check default 0 (per ADR-052 + ADR-054 lesson #12 — store is a vCard section, not a separate product)
  - `enable_add_to_contact` Check default 1
  - `enable_share_buttons` Check default 1
- **WhatsApp Store** (used when enable_whatsapp_store=1, per ADR-052 + ADR-053)
  - `whatsapp_store_template` Link → Alumni WhatsApp Store Template (defaults to "Standard Storefront")
  - `whatsapp_store_announcement` Small Text — banner shown above products
  - `whatsapp_store_business_hours_enabled` Check default 1
  - `whatsapp_store_terms_url` Data
  - `whatsapp_store_refund_policy_url` Data
  - `whatsapp_store_shipping_policy_url` Data
- **Children**
  - `social_links` Table → Alumni VCard Social Link
  - `services` Table → Alumni VCard Service
  - `gallery_items` Table → Alumni VCard Gallery Item
  - `gallery_categories` Table → Alumni VCard Gallery Category
  - `testimonials` Table → Alumni VCard Testimonial
  - `business_hours` Table → Alumni VCard Business Hour
  - `iframes` Table → Alumni VCard Iframe
  - `custom_links` Table → Alumni VCard Custom Link
  - `faqs` Table → Alumni VCard FAQ
- **Customization**
  - `custom_css` Long Text (sanitized via bleach allow-list — no `@import`, no JS URLs, no `expression()`)
  - `custom_meta_title` Data (SEO)
  - `custom_meta_description` Small Text (SEO)
  - `custom_og_image` Attach Image (1200×630 — per ADR-049)
  - `custom_favicon` Attach Image
  - `google_analytics_id` Data
  - `meta_pixel_id` Data
  - `hide_alumni_branding` Check default 0 (Members-only feature when `Alumni Settings.allow_branding_hide=1`)
- **QR Code**
  - `qr_color` Color (default = institution accent)
  - `qr_background_color` Color (default = white)
  - `qr_eye_style` Select: Square / Rounded / Circle
  - `qr_logo_overlay` Attach Image (defaults to institution logo)
- **Privacy / access**
  - `monthly_view_limit` Int (auto-set from membership tier per ADR-054 lesson #7; 0 = unlimited)
  - `monthly_view_count` Int (computed; reset by daily job)
  - `total_view_count` Int (lifetime)
  - `disable_indexing` Check default 0 (renders `noindex` if 1)
- **Lifecycle**
  - `published_on` Datetime
  - `last_edited_on` Datetime
  - `template_changed_on` Datetime
  - `views_last_30_days` Int (cached)

> Permission: Alumni edits own vCard; cannot edit `hide_alumni_branding` if Settings doesn't allow it; cannot exceed storage quota; Admin reviews flagged vCards. The `slug` cannot be reused once a vCard is deleted (kept in tombstone for 90 days to prevent impersonation hijack of an old URL).

### Alumni VCard Template — NEW v3 (per ADR-050 + ADR-053)
- `name` Data (folder ID, e.g. `classic-professional`, `modern-minimal`, `doctor`, `lawyer-uploaded-2026-04`)
- `display_name` Data req
- `description` Small Text
- `category` Select: General / Healthcare / Legal / Tech / Creative / Real Estate / Education / Hospitality / Retail / Services / Finance / Wedding / Other
- `version` Data
- `author` Data
- `license` Data
- `supports_dark` Check
- `supports_rtl` Check (validator enforces actual RTL compatibility per ADR-054 lesson #3)
- `extends_template` Link → Alumni VCard Template (optional inheritance)
- `preview_image` Attach Image (auto-generated from `sample_data` on install)
- `is_built_in` Check (1 = ships with the app, never modified by admin; 0 = admin-uploaded)
- `is_active` Check (admin can hide a template without deleting it)
- `manifest_json` JSON (cached copy of template.json for fast querying)
- `installed_on` Datetime
- `installed_by` Link → User
- `times_used` Int (computed: how many alumni use this template)

> Read-only at the DocType level; populated by the install pipeline (admin upload → validator → live dir → record creation). Re-uploading the same template id with a higher version updates files in place; lower version is rejected.

### Alumni VCard Social Link (child) — NEW v3
- `platform` Select: LinkedIn / Twitter (X) / Facebook / Instagram / YouTube / TikTok / Snapchat / Pinterest / Reddit / Tumblr / GitHub / GitLab / Bitbucket / Behance / Dribbble / Medium / Substack / Spotify / SoundCloud / Twitch / Discord / Telegram / Signal / Threads / Bluesky / Mastodon / WhatsApp / Custom
- `url` Data req (URL-validated; rejected if domain doesn't match the chosen platform when not Custom)
- `display_label` Data (only when platform=Custom)
- `is_visible` Check default 1
- `sort_order` Int

### Alumni VCard Service (child) — NEW v3
- `service_name` Data req
- `description` Small Text
- `icon` Attach Image (square, ≤256KB)
- `price` Currency
- `tax_inclusive` Check
- `tax_rate_percent` Float
- `tax_label` Data (e.g. "VAT 15%")
- `book_via_appointment` Check (if 1, links to vCard appointment booking with this service preselected)
- `inquiry_button` Check default 1
- `external_url` Data (optional — direct link to landing page)
- `sort_order` Int

### Alumni VCard Gallery Item (child) — NEW v3
- `media_type` Select: Image / Video / Audio / YouTube / File / Instagram Embed / LinkedIn Embed
- `category` Link → Alumni VCard Gallery Category
- `image` Attach Image (when media_type=Image; auto-cropped to declared aspect)
- `video_file` Attach (when media_type=Video; max 50MB; `controls` always enabled)
- `audio_file` Attach (when media_type=Audio)
- `external_url` Data (when media_type ∈ {YouTube, Instagram Embed, LinkedIn Embed})
- `caption` Small Text
- `sort_order` Int
- `is_visible` Check default 1

### Alumni VCard Gallery Category (child) — NEW v3
- `category_name` Data req
- `cover_image` Attach Image
- `sort_order` Int

### Alumni VCard Testimonial (child) — NEW v3
- `author_name` Data req
- `author_role` Data
- `author_photo` Attach Image
- `quote` Long Text req
- `rating` Int (1–5, optional)
- `is_published` Check default 1

### Alumni VCard Iframe (child) — NEW v3
- `title` Data req
- `iframe_url` Data req (sanitized: only allow-listed domains — YouTube, Vimeo, Google Maps, OSM, Calendly, Notion, Loom, Mural — admin can extend the list in Settings)
- `height` Int default 400
- `is_visible` Check default 1

### Alumni VCard Business Hour (child) — NEW v3
- `day_of_week` Select: Monday / Tuesday / Wednesday / Thursday / Friday / Saturday / Sunday
- `is_open` Check
- `open_time` Time
- `close_time` Time
- `notes` Data (e.g. "Lunch break 1–2pm")

### Alumni VCard Custom Link (child) — NEW v3
- `label` Data req
- `url` Data req
- `icon` Data (Lucide icon name) or `icon_image` Attach Image
- `style` Select: Primary / Secondary / Ghost
- `sort_order` Int
- `is_visible` Check default 1

### Alumni VCard FAQ (child) — NEW v3
- `question` Data req
- `answer` Long Text req (rich text, sanitized)
- `sort_order` Int
- `is_visible` Check default 1

### Alumni VCard Inquiry — NEW v3
- `name` autoname `INQ-{YYYY}-{######}`
- `vcard` Link → Alumni VCard req
- `inquirer_name` Data req
- `inquirer_email` Data req (validated against `Alumni Settings.blocked_email_domains` per ADR-054 lesson #8)
- `inquirer_phone` Data
- `subject` Data
- `message` Long Text req (scanned against `blocked_inquiry_keywords` regex)
- `attachment` Attach (admin-toggleable)
- `submitted_on` Datetime auto
- `submitted_ip` Data (for spam audit; auto-purged after 90 days)
- `status` Select: New / Read / Replied / Spam / Archived
- `is_spam` Check (auto-flagged or admin-marked)
- `replied_on` Datetime
- `vcard_owner_notified` Check (notification sent to alumni)

### Alumni VCard Appointment — NEW v3
- `name` autoname `APT-{YYYY}-{######}`
- `vcard` Link → Alumni VCard req
- `service` Link → Alumni VCard Service (when booked-via-service per recent InfyVCards v14.7.5)
- `customer_name` Data req
- `customer_email` Data req
- `customer_phone` Data
- `requested_date` Date req
- `requested_time` Time req
- `duration_minutes` Int default 30
- `notes` Long Text
- `is_paid` Check
- `payment_amount` Currency
- `payment_status` Select: Not Required / Pending / Paid / Refunded / Failed
- `payment_link` Data (auto-generated via receivables adapter)
- `status` Select: Pending / Approved / Rejected / Completed / Cancelled / No Show
- `notification_email_template` Link → Email Template
- `vcard_owner_calendar_event` Data (optional — ICS UID if exported to alumni's calendar via communication adapter)

### Alumni VCard Product — NEW v3
- `name` autoname `PRD-{YYYY}-{######}`
- `vcard` Link → Alumni VCard req
- `title` Data req
- `description` Long Text
- `images` Table → Alumni VCard Product Image (multiple images supported per InfyVCards v13.0.0)
- `price` Currency req
- `discounted_price` Currency
- `tax_inclusive` Check
- `tax_rate_percent` Float
- `tax_label` Data
- `currency` Link → Currency
- `available_stock` Int default 0 (0 = unlimited / made-to-order)
- `is_in_stock` Check virtual (computed from available_stock)
- `delivery_options` Small Text
- `category` Link → Alumni VCard Product Category (child of vCard or shared)
- `sort_order` Int
- `is_published` Check default 0
- `inquiry_button` Check default 1

### Alumni VCard Product Order — NEW v3
- `name` autoname `ORD-{YYYY}-{######}`
- `vcard` Link → Alumni VCard req
- `product` Link → Alumni VCard Product req
- `quantity` Int default 1
- `customer_name` Data req
- `customer_email` Data req
- `customer_phone` Data
- `shipping_address` Long Text
- `subtotal` Currency
- `tax_amount` Currency
- `discount_amount` Currency
- `coupon_code` Data
- `total_amount` Currency
- `payment_status` Select: Pending / Paid / Refunded / Failed
- `payment_method` Select (matches enabled gateways from Alumni Settings)
- `order_status` Select: Placed / Confirmed / Processing / Shipped / Delivered / Cancelled / Refunded
- `placed_on` Datetime auto
- `tracking_number` Data
- `notes` Long Text

> A PDF receipt is auto-generated on payment-status=Paid (via certificates adapter); receipts include tax breakdown.

### Alumni VCard Visit — NEW v3
- `name` autoname `VIS-{YYYY}-{######}`
- `vcard` Link → Alumni VCard req
- `visit_date` Date req
- `view_count` Int (aggregated daily)
- `unique_view_count` Int (cookie-based)
- `whatsapp_click_count` Int
- `add_to_contact_count` Int
- `inquiry_count` Int
- `appointment_count` Int
- `share_count` Int
- `top_country` Link → Country (most-visited from this country today)
- `top_referrer` Data (truncated; aggregate)

> Aggregated daily for privacy. No per-visitor IP storage in production. Visit counter reset is `tasks.reset_monthly_vcard_views()` on the 1st of each month.

### Alumni WhatsApp Store Template — NEW v3 (per ADR-052 + ADR-053)
- Same shape as Alumni VCard Template: `name`, `display_name`, `category`, `version`, `author`, `license`, `supports_dark`, `supports_rtl`, `extends_template`, `preview_image`, `is_built_in`, `is_active`, `manifest_json`, `installed_on`, `installed_by`, `times_used`.

> v1 ships 1 built-in template ("Standard Storefront"). All others uploaded by admin via the same registry pattern as vCard templates.

### Alumni VCard WhatsApp Catalog Sync Log — NEW v3 (per ADR-052)
- `name` autoname `WCS-{YYYY}-{######}`
- `vcard` Link → Alumni VCard req
- `sync_started_at` Datetime
- `sync_completed_at` Datetime
- `products_pushed` Int
- `services_pushed` Int
- `status` Select: Success / Partial / Failed
- `error_summary` Small Text
- `meta_response_payload` Long Text (truncated)

### Alumni AI Generation Log — NEW v3 (per ADR-054 lesson #10)
- `name` autoname `AIL-{YYYY}-{######}`
- `requested_by` Link → User
- `target_doctype` Data (e.g., "Alumni VCard", "Alumni Story", "Alumni Donation Campaign", "Alumni Award Recipient")
- `target_name` Data (linked record)
- `purpose` Select: Bio Draft / Section Description / Story Draft / Campaign Description / News Article / Citation / Other
- `prompt_hash` Data (SHA-256 of the rendered prompt — never the prompt text itself, for privacy)
- `model_provider` Data (e.g., "openai", "anthropic", "bedrock", "custom-http")
- `model_id` Data
- `input_token_count` Int
- `output_token_count` Int
- `latency_ms` Int
- `accepted_by_user` Check (1 if user kept the result; 0 if regenerated or discarded)
- `created_on` Datetime auto

> Used for cost tracking, abuse detection, and privacy auditing. Prompt content is hashed, not stored. Output is not stored either — only the metadata. The user sees the output in their composer; once they save (or discard) it, the only artifact is this metadata log.

### Alumni Settings (Single)
- `mode` Select: school_connected / standalone (locked after first save unless reset by System Manager)
- `institution_name` Data req
- `institution_logo` Attach Image
- `public_domain` Data (e.g. alumni.school.edu)
- `default_currency` Link → Currency
- `default_language` Link → Language — **NEW v3**
- `enabled_languages` Table → Language Pivot — **NEW v3**
- `payment_gateway` Link → Payment Gateway (from frappe/payments)
- `theme` Link → Alumni Theme (default `heritage`)
- `enable_mentorship` Check default 1
- `mentorship_min_age` Int default 16
- `mentorship_auto_decline_days` Int default 7
- `enable_volunteer_board` Check default 1
- `enable_chapters` Check default 1
- `enable_network_qa` Check default 1
- `enable_outcome_surveys` Check default 1
- `enable_public_qa` Check default 0
- `enable_messaging` Check default 1 — **NEW v3**
- `enable_elections` Check default 0 — **NEW v3** (off by default; turn on when association is ready)
- `enable_guest_donations` Check default 1 — **NEW v3**
- `recurring_donations_enabled` Check default 0 (v2)
- `application_retention_days` Int default 365
- `donation_tax_receipt_template` Data
- `social_facebook_url` / `linkedin_url` / `twitter_url` / `instagram_url` Data

#### Verification & Security section — NEW v3
- `require_email_verification` Check default 1
- `require_phone_verification` Check default 0
- `require_verification_documents` Check default 1
- `min_verification_documents` Int default 1
- `mandatory_2fa_for_admin` Check default 1 — per ADR-036
- `social_login_enabled` Check default 0
- `social_login_providers` Small Text (comma-separated; per ADR-037 valid: google, facebook, linkedin, apple, microsoft)

#### Messaging section — NEW v3
- `messaging_message_max_length` Int default 4000
- `messaging_attachments_enabled` Check default 1
- `messaging_attachment_max_mb` Int default 10
- `messaging_block_unverified_senders` Check default 1

#### Election section — NEW v3
- `nomination_fee_enabled` Check default 0
- `default_nomination_fee` Currency
- `vote_audit_required` Check default 1 (each vote reviewed by a Board Member before counted — per ZaiAlumni's transparency model)
- `voter_eligibility` Select: All Active Alumni / Active Members Only / Specific Chapter

#### Communication channels & Broadcast — NEW v3 (per ADR-040)
- `default_sms_channel` Link → Alumni Communication Channel (used by `send_sms` when no explicit channel and no country match)
- `default_whatsapp_channel` Link → Alumni Communication Channel (used by `send_whatsapp` when no explicit channel)
- `transactional_sms_channel` Link → Alumni Communication Channel (overrides default for OTPs and one-shots — usually a higher-reliability provider)
- `broadcast_max_recipients_per_minute` Int default 60 (rate limit, protects sender reputation and quota)
- `broadcast_require_admin_double_confirm_above` Int default 500 (force a "type the title to confirm" gate when sending to ≥N recipients)
- `broadcast_default_country_filter` Link → Country (optional default for broadcasts, e.g. "Saudi Arabia" for a KSA institution)

#### Domains, branding & PWA — NEW v3 (per ADR-041 + ADR-042 + ADR-043)
- `primary_domain` Data (auto-mirrored from primary `Alumni Tenant Domain` record; used by `frappe.utils.get_url`)
- `pwa_enabled` Check default 1 — per ADR-042
- `pwa_app_short_name` Data (≤12 chars; appears under the home-screen icon)
- `pwa_theme_color` Data (hex; auto-defaults to active theme's `--color-accent`)
- `pwa_background_color` Data
- `enable_dark_mode_auto` Check default 1 — when active theme has a paired dark variant, follow OS `prefers-color-scheme`
- `white_label_enabled` Check default 0 (SaaS tenants on higher tiers can hide "Powered by" footer; v1 always allows it for paying tenants)
- `custom_email_signature_html` Long Text (overrides default Frappe email footer)

#### Completeness & onboarding — NEW v3 (per ADR-044)
- `completeness_rules` JSON (default ships per ADR-044; admin can edit weights to suit institution)
- `directory_min_completeness` Int default 0 (0 = show everyone; ≥X gates directory listing)
- `messaging_min_completeness` Int default 0 (≥X gates messaging — soft enforcement)
- `onboarding_steps` JSON (admin-configurable list of welcome steps)

#### Perks & member card — NEW v3 (per ADR-046)
- `perks_enabled` Check default 1
- `member_card_logo_position` Select: Top-Left / Top-Center / Top-Right
- `member_card_seal_image` Attach Image (institution seal, embossed on the digital card)
- `apple_wallet_pass_type_id` Data (optional, only when configured for PassKit)
- `google_wallet_issuer_id` Data (optional)

#### Career, speakers, referrals — NEW v3 (per ADR-047)
- `referrals_enabled` Check default 1
- `referral_points_per_hire` Int default 10 (reputation award)
- `speaker_bureau_enabled` Check default 1
- `speaker_request_default_response_days` Int default 7 (auto-decline after N days no response)

#### SEO & sharing — NEW v3 (per ADR-049)
- `seo_default_og_image` Attach Image (1200×630 — fallback for surfaces without a specific image)
- `seo_twitter_handle` Data (e.g., `@aramcoSchoolAlumni`)
- `seo_organization_jsonld_overrides` JSON (admin-controlled overrides for the schema.org Organization block)
- `qr_code_branding_color` Data (hex; null = use accent color)

#### Digital Business Cards / vCards — NEW v3 (per ADR-050)
- `vcards_enabled` Check default 1
- `vcards_require_membership` Check default 1 (only Members can publish vCards)
- `default_vcard_template` Link → Alumni VCard Template (default = "Classic Professional")
- `default_whatsapp_store_template` Link → Alumni WhatsApp Store Template (default = "Standard Storefront")
- `vcard_storage_per_alumni_mb` Int default 100 (per ADR-054 lesson #1; overridable per Membership Plan)
- `vcard_storage_total_per_site_mb` Int default 50000 (institution-level cap)
- `vcard_default_monthly_view_limit` Int default 0 (0 = unlimited; non-zero gates per ADR-054 lesson #7)
- `allow_branding_hide` Check default 0 (whether higher-tier alumni can hide "Powered by [Institution]" footer on their vCard)
- `vcard_iframe_allowlist_domains` Long Text (one domain per line; defaults: youtube.com, vimeo.com, google.com/maps, openstreetmap.org, calendly.com, notion.so, loom.com, mural.co)
- `vcard_blocked_slugs` Long Text (one slug per line; e.g. admin, api, system, www, support — institution-specific reservations)
- `vcard_template_upload_max_mb` Int default 10
- `vcard_template_upload_allowed_roles` Table (default: System Manager only — institutions can extend to specific designers per ADR-053)
- `vcard_template_validator_strict_mode` Check default 1 (rejects templates that don't fully declare RTL support per ADR-054 lesson #3)

#### WhatsApp Business — NEW v3 (per ADR-052)
- `whatsapp_business_integration_enabled` Check default 0 (tier-b — requires Meta verification per institution)
- `whatsapp_business_default_channel` Link → Alumni Communication Channel (must be channel_type=WhatsApp; routes vCard tier-b traffic)
- `whatsapp_catalog_sync_frequency` Select: Manual / Hourly / Daily (default Daily)

#### AI assistance — NEW v3 (per ADR-054 lesson #10)
- `ai_enabled` Check default 0 (institution opts in)
- `ai_provider` Select: None / OpenAI / Anthropic / Bedrock / Custom HTTP
- `ai_credentials` Password (provider-specific JSON)
- `ai_model_default` Data (e.g., "gpt-4o-mini", "claude-haiku-4-5", "claude-sonnet-4-7")
- `ai_max_monthly_tokens_per_alumni` Int default 50000 (caps abuse / cost; resets monthly)
- `ai_purposes_enabled` Multi-Select: Bio Draft / Section Description / Story Draft / Campaign Description / News Article / Citation
- `ai_data_retention_days` Int default 90 (Alumni AI Generation Log auto-purge after N days)

#### Antispam & abuse — NEW v3 (per ADR-054 lesson #8)
- `blocked_email_domains` Long Text (one domain per line — emails from these domains rejected from registration, vCard inquiry, donation guest, broadcast custom-list upload)
- `blocked_inquiry_keywords` Long Text (one regex per line — vCard inquiry messages matching are auto-flagged is_spam=1)
- `inquiry_min_seconds_on_page` Int default 3 (anti-bot honeypot — submissions faster than this are spam)
- `vcard_inquiry_attachments_enabled` Check default 0 (gates whether inquiries can include file attachments)
- `recovery_codes_count` Int default 8 (per ADR-054 lesson #6)

#### School-Connected section *(Section, only if mode=school_connected)*
- `auto_promote_enabled` Check
- `auto_promote_passing_years_back` Int default 1
- `require_zero_outstanding_fees` Check default 1
- `auto_promote_requires_review` Check default 0

---

### Alumni Message Thread — NEW v3
- `name` autoname `uuid`
- `participant_a` Link → Alumni Profile req
- `participant_b` Link → Alumni Profile req (1:1 messaging only in v1; group chats deferred to v2)
- `last_message_at` Datetime
- `last_message_preview` Small Text (≤120 chars, sanitized)
- `participant_a_unread_count` Int
- `participant_b_unread_count` Int
- `is_blocked_by` Link → Alumni Profile (null = open thread)
- `flagged` Check
- `flag_reason` Small Text

> Uniqueness: there is only ever one thread per pair. Controller normalizes (`participant_a` < `participant_b` lexicographically) on save.

### Alumni Message — NEW v3
- `name` autoname `uuid`
- `thread` Link → Alumni Message Thread req
- `sender` Link → Alumni Profile req
- `body` Long Text req
- `attachments` Table → File (via storage adapter; private)
- `sent_at` Datetime auto
- `edited_at` Datetime
- `is_deleted_for_sender` / `is_deleted_for_recipient` Check
- `read_receipts` Table → Alumni Message Read Receipt

### Alumni Message Read Receipt (child) — NEW v3
- `reader` Link → Alumni Profile
- `read_at` Datetime

> Realtime: `frappe.publish_realtime("alumni_new_message", payload, user=recipient_user)` from the controller after insert. Frontend subscribes via Frappe's socketio. No separate Pusher needed.

---

### Alumni Committee Category — NEW v3
- `name` autoname `CC-{####}`
- `category_name` Data req unique
- `description` Small Text
- `is_active` Check default 1

### Alumni Committee
- `name` autoname `COM-{YYYY}-{####}`
- `committee_name` Data req
- `category` Link → Alumni Committee Category
- `description` Text Editor
- `term_start` / `term_end` Date
- `members` Table → Alumni Committee Member
- `is_elected` Check (true if produced by an Election; locks editing of members table)
- `parent_election` Link → Alumni Election (set when is_elected=1)
- `status` Select: Active / Past / Disbanded

### Alumni Committee Designation — NEW v3
- `name` autoname `DES-{####}`
- `designation_name` Data req unique (e.g. "President", "Treasurer", "Secretary", "Member")
- `description` Small Text
- `term_months` Int default 24
- `is_elected_role` Check default 1 (false for appointed roles like "Honorary Advisor")
- `is_active` Check default 1

### Alumni Committee Member (child)
- `alumni` Link → Alumni Profile req
- `designation` Link → Alumni Committee Designation req
- `start_date` / `end_date` Date
- `is_current` Check
- `bio_snapshot` Small Text
- `appointed_or_elected` Select: Appointed / Elected

### Alumni Committee Meeting
- `name` autoname `MTG-{YYYY}-{####}`
- `committee` Link → Alumni Committee req
- `scheduled_at` Datetime req
- `duration_minutes` Int
- `mode` Select: In-Person / Online / Hybrid
- `venue` Data
- `online_link` Data (from live_class adapter if online)
- `agenda` Text Editor
- `minutes` Text Editor
- `status` Select: Scheduled / Completed / Cancelled

---

### Alumni Election — NEW v3
- `name` autoname `ELEC-{YYYY}-{####}`
- `election_title` Data req (e.g. "Alumni Association 2026 Board Election")
- `committee` Link → Alumni Committee req (which committee this election is for)
- `nomination_open_at` / `nomination_close_at` Datetime req
- `voting_open_at` / `voting_close_at` Datetime req
- `result_publish_at` Datetime
- `nomination_fee` Currency (default from Settings)
- `voter_eligibility` Select: All Active Alumni / Active Members Only / Specific Chapter
- `eligibility_chapter` Link → Alumni Chapter (only if voter_eligibility = Specific Chapter)
- `min_passing_year` / `max_passing_year` Int (eligibility filter)
- `positions` Table → Alumni Election Position
- `status` Select: Draft / Nomination Open / Nomination Closed / Voting Open / Voting Closed / Results Published / Cancelled
- `results` Table → Alumni Election Result
- `vote_audit_required` Check (mirrors Setting; can be overridden per election)

### Alumni Election Position (child) — NEW v3
- `designation` Link → Alumni Committee Designation req
- `seats` Int default 1 (e.g., 5 General Member seats; 1 President)
- `description` Small Text

### Alumni Election Symbol — NEW v3
- `name` autoname `SYM-{####}`
- `symbol_name` Data req unique (e.g. "Tree", "Star", "Bicycle", "Compass")
- `symbol_image` Attach Image req
- `is_assigned` Check (auto, derived from current usage)

### Alumni Nomination — NEW v3
- `name` autoname `NOM-{YYYY}-{######}`
- `election` Link → Alumni Election req
- `position` Link → Alumni Committee Designation req (must be in election.positions)
- `nominee` Link → Alumni Profile req
- `manifesto` Text Editor (≤2000 chars)
- `photo` Attach Image (override of profile photo for ballot)
- `proposed_symbol` Link → Alumni Election Symbol
- `assigned_symbol` Link → Alumni Election Symbol (board sets after approval)
- `nomination_fee` Currency
- `payment_status` Select: Not Required / Pending / Paid / Refunded
- `invoice_id` Data
- `application_status` Select: Submitted / Under Review / Approved / Rejected / Withdrawn
- `reviewed_by` Link → User (Board Member)
- `reviewed_on` Datetime
- `rejection_reason` Small Text

> When `application_status = Approved` AND `payment_status` ∈ {Not Required, Paid}, controller creates an `Alumni Candidate` record and notifies the nominee.

### Alumni Candidate — NEW v3
- `name` autoname `CAND-{YYYY}-{######}`
- `nomination` Link → Alumni Nomination unique req
- `election` Link → Alumni Election req
- `position` Link → Alumni Committee Designation req
- `alumni` Link → Alumni Profile req
- `display_name` Data (denormalized from alumni for ballot display)
- `assigned_symbol` Link → Alumni Election Symbol req
- `manifesto_published` Text Editor
- `votes_count` Int (computed; not editable; from validated Vote records)
- `is_winner` Check (set when results published)

### Alumni Candidate Comment — NEW v3
- `name` autoname `uuid`
- `candidate` Link → Alumni Candidate req
- `commenter_alumni` Link → Alumni Profile (null for guest if `enable_public_candidate_comments`)
- `body` Small Text req (≤500 chars)
- `is_published` Check default 0 (Board Member moderates)
- `published_by` Link → User
- `published_on` Datetime
- `commented_on` Datetime auto

### Alumni Vote — NEW v3
- `name` autoname `uuid` (opaque so voter cannot be reverse-engineered easily)
- `election` Link → Alumni Election req
- `position` Link → Alumni Committee Designation req
- `candidate` Link → Alumni Candidate req
- `voter` Link → Alumni Profile req (used only for one-vote-per-position enforcement; redacted in audit views via permissions.py)
- `cast_at` Datetime auto
- `voter_ip_hash` Data (sha256(ip + secret); kept for audit; never displayed)
- `audit_status` Select: Pending Review / Validated / Rejected — Per ZaiAlumni's transparency model, each vote is reviewed by a Board Member before counted (gate is on `vote_audit_required`)
- `audited_by` Link → User
- `audit_notes` Small Text
- `audit_decision_at` Datetime

> One-vote-per-position-per-voter enforced via DB-level unique index `(election, position, voter)`. Voters cannot see other voters' choices; admin queries are audit-logged.

### Alumni Election Result (child) — NEW v3
- `position` Link → Alumni Committee Designation
- `seats_to_fill` Int
- `winning_candidates` Small Text (comma-separated candidate names — denormalized for printing)

---

### Alumni News Category — NEW v3
- `name` autoname `NCAT-{####}`
- `category_name` Data req unique
- `description` Small Text
- `is_active` Check default 1

### Alumni News Tag — NEW v3
- `name` autoname `TAG-{####}`
- `tag_name` Data req unique

### Alumni News Article (extended)
- adds: `category` Link → Alumni News Category, `tags` Table → Alumni News Tag

### Alumni Notice Category — NEW v3
- `name` autoname `NOTC-{####}`
- `category_name` Data req unique
- `is_active` Check default 1

### Alumni Notice (extended)
- adds: `category` Link → Alumni Notice Category

---

### Site CMS — NEW v3

> Most marketing pages (Home, About, Pricing, FAQ landing) are built in Frappe Builder per ADR-029. The four DocTypes below capture *structured* content that the Builder pages embed via dynamic blocks.

### Alumni FAQ
- `name` autoname `FAQ-{####}`
- `question` Data req
- `answer` Text Editor req
- `category` Data
- `display_order` Int
- `is_published` Check default 1

### Alumni Testimonial
- `name` autoname `TEST-{####}`
- `quote` Text req (≤500 chars)
- `author_name` Data req
- `author_title` Data
- `author_passing_year` Int
- `author_photo` Attach Image
- `is_published` Check default 1
- `display_order` Int

### Alumni Image Gallery Item
- `name` autoname `GAL-{####}`
- `title` Data
- `image` Attach Image req
- `caption` Small Text
- `gallery` Data (slug, e.g. "annual-day-2024")
- `display_order` Int
- `is_published` Check default 1

### Alumni Hero Banner
- `name` autoname `HERO-{####}`
- `headline` Data req
- `subheadline` Small Text
- `cta_label` Data
- `cta_url` Data
- `background_image` Attach Image
- `display_order` Int
- `is_published` Check default 1
- `start_date` / `end_date` Date (optional scheduling)

---

## §05 Workflows

### Content (Job / Story / News / Notice)
`Draft → Pending → Approved → Published → Expired` · side: `Pending → Rejected` · approver: Moderator

### Alumni Event Wrapper
`Draft → Pending → Open → Closed → Completed` · side: any → `Cancelled` · approver: Moderator
> Buzz Event status (Draft/Published/Sold-out) is managed by Buzz; our wrapper status reflects moderation/lifecycle.

### Membership
`Pending Payment → Active → Expired` · side: `Active → Cancelled`, `Pending Payment → Refunded`

### Mentorship Request
`Pending → Accepted → Completed` · side: `Pending → Declined`, `Pending → Auto-Declined`

### Alumni Nomination — NEW v3
`Submitted → Under Review → Approved → (creates Candidate)` · side: `Under Review → Rejected`, `Submitted → Withdrawn` · approver: Board Member

### Alumni Election — NEW v3 (status transitions, time-driven by scheduler)
`Draft → Nomination Open → Nomination Closed → Voting Open → Voting Closed → Results Published` · any → `Cancelled` · transitions driven by scheduled job `tasks.advance_election_states()` based on dates

### Alumni Verification (gate inside Profile lifecycle) — NEW v3
- `Profile.status = Pending Email` → email link clicked → `Pending Docs` (if `require_verification_documents`)
- `Pending Docs` → admin reviews, marks each `Verification Document.review_decision = Accepted` → if at least `min_verification_documents` accepted → `Profile.verification_status = Verified` → admin approves → `Active`

---

## §06 Permissions matrix (R/W/C/D)

| DocType | Guest | Alumni | Mentor | Board Mem. | Moderator | Admin |
|---|---|---|---|---|---|---|
| Alumni Profile | — | R own + W own + R directory | R+W own | R | R | RWCD |
| Alumni Verification Document | — | R own + C own | R own | R+W (review) | — | RWCD |
| Alumni Event Wrapper | R public | R + WC own | RWC own | R | R + Approve | RWCD |
| Buzz Event (read via adapter) | R public | R + filtered | R + filtered | R | R | (Buzz roles) |
| Alumni Job Post | R public | R + WC own | R+W own | R | R + Approve | RWCD |
| Alumni Job Application | — | R own + R apps to own posts | R own | — | — | RWCD |
| Alumni Story | R approved | R + WC own | R+W own | R | R + Approve | RWCD |
| Alumni Volunteer Opportunity | — | R + Sign up | R | R | — | RWCD |
| Alumni Membership | — | R own | R own | R | — | RWCD |
| Alumni Donation | C as guest | R own + C | R own | R | — | RWCD |
| Alumni Donation Campaign | R if running | R + Comment | R | R | — | RWCD |
| Alumni Campaign Comment | R published | RWC own | RW own | R + Moderate | R + Moderate | RWCD |
| Alumni Committee | — | R if member or elected | R if member | R | R | RWCD |
| Alumni Chapter | R | R + Join | R + Join | R | R | RWCD |
| Alumni Network Question | R public flagged | RWC | RWC | R | R + Moderate | RWCD |
| Alumni Mentorship Request | — | C as mentee | RW own as mentor | — | — | RWCD |
| Alumni Mentorship Session | — | R own | RW own | — | — | RWCD |
| Alumni Outcome Survey Response | — | R own + W own | R own | — | — | RWCD |
| Alumni Newsletter | — | — | — | R | R | RWCD |
| Alumni Audit Log | — | — | — | R own scope | R own scope | R |
| Alumni Theme | — | — | — | — | R | RWCD |
| Alumni Invoice (standalone) | — | R own | R own | R | — | RWCD |
| Alumni Payment (standalone) | — | R own | R own | R | — | RWCD |
| Alumni Settings | — | — | — | — | — | RW |
| **Alumni Message Thread** | — | RW own threads | RW own | R own | — | R (audit) |
| **Alumni Message** | — | RW own | RW own | R own thread | — | R (audit) |
| **Alumni Election** | R if Voting Open | R + Vote | R + Vote | R + Audit | R | RWCD |
| **Alumni Nomination** | — | RWC own | RW own | R + Approve/Reject | — | RWCD |
| **Alumni Candidate** | R during election | R + Comment | R | R+W (set symbol) | R | RWCD |
| **Alumni Candidate Comment** | R published | RWC own | RW own | R + Moderate | R + Moderate | RWCD |
| **Alumni Vote** | — | C own | C own | R + Audit | — | R (audit only — never write) |
| **Alumni Election Symbol** | R | R | R | RWC (during election setup) | — | RWCD |
| **Alumni Committee Designation** | R | R | R | R | R | RWCD |
| **Alumni FAQ** | R published | R | R | R | R | RWCD |
| **Alumni Testimonial** | R published | R | R | R | R | RWCD |
| **Alumni Hero Banner** | R published | R | R | R | R | RWCD |
| **Alumni Image Gallery Item** | R published | R | R | R | R | RWCD |

Field-level redaction (privacy_visibility / email_visibility / phone_visibility) plus v16 data masking on `phone`/`whatsapp`/`email` when displayed to non-owner. The voter field on `Alumni Vote` is always redacted to non-System-Manager; reads are logged to `Alumni Audit Log` with event_type `vote_record_read`.

---

## §07 API surface (`alumni/api.py`)

```python
from __future__ import annotations
import frappe

# Profiles & directory
@frappe.whitelist()
def directory_search(q: str | None = None, batch: int | None = None,
                     department: str | None = None, industry: str | None = None,
                     country: str | None = None, city: str | None = None,
                     willing_to_mentor: int = 0, page: int = 0) -> dict: ...

@frappe.whitelist()
def get_profile(name: str | None = None) -> dict: ...

@frappe.whitelist()
def update_profile(payload: dict) -> dict: ...

@frappe.whitelist()
def submit_verification_document(document_type: str, file_url: str,
                                 notes: str | None = None) -> dict: ...   # NEW v3

# Mentorship
@frappe.whitelist()
def request_mentorship(mentor: str, topic: str, message: str) -> dict: ...

@frappe.whitelist()
def respond_mentorship(request_name: str, decision: str,
                       reason: str | None = None) -> dict: ...

@frappe.whitelist()
def schedule_mentorship_session(request_name: str, scheduled_at: str,
                                duration: int, mode: str, agenda: str) -> dict: ...

# Money — events forward to Buzz adapter; memberships and donations through receivables
@frappe.whitelist()
def book_event(event_wrapper: str, ticket_type: str, qty: int,
               add_ons: list[dict] | None = None,
               coupon: str | None = None) -> dict: ...

@frappe.whitelist()
def buy_membership(plan: str) -> dict: ...

@frappe.whitelist()
def donate(amount: float, currency: str, campaign: str | None = None,
           anonymous: int = 0, donor_alias: str | None = None,
           donor_message: str | None = None) -> dict: ...

@frappe.whitelist(allow_guest=True)                                # NEW v3
def donate_as_guest(amount: float, currency: str,
                    guest_name: str, guest_email: str,
                    campaign: str, donor_message: str | None = None) -> dict: ...

# Social
@frappe.whitelist()
def feed(page: int = 0) -> dict: ...

@frappe.whitelist()
def react(parent_doctype: str, parent_name: str, kind: str) -> dict: ...

@frappe.whitelist()
def comment(parent_doctype: str, parent_name: str, body: str) -> dict: ...

# Network Q&A
@frappe.whitelist()
def ask_network(title: str, body: str, category: str, is_public: int = 0,
                country: str | None = None, industry: str | None = None) -> dict: ...

@frappe.whitelist()
def answer_question(question: str, body: str) -> dict: ...

# Volunteering
@frappe.whitelist()
def list_volunteer_opportunities(category: str | None = None) -> list[dict]: ...

@frappe.whitelist()
def signup_volunteer(opportunity: str, note: str | None = None) -> dict: ...

# Chapters & Reunions
@frappe.whitelist()
def join_chapter(chapter: str) -> dict: ...

@frappe.whitelist()
def list_my_reunion_batchmates() -> list[dict]: ...

# Surveys
@frappe.whitelist()
def submit_outcome_survey(template: str, answers: list[dict]) -> dict: ...

# === Private Messaging (NEW v3) ===
@frappe.whitelist()
def list_threads(page: int = 0) -> dict: ...

@frappe.whitelist()
def get_thread(thread: str, page: int = 0) -> dict: ...

@frappe.whitelist()
def open_thread_with(other_alumni: str) -> dict:
    """Returns existing thread or creates one. Honors messaging_preference + is_blocked_by."""

@frappe.whitelist()
def send_message(thread: str, body: str,
                 attachments: list[str] | None = None) -> dict: ...

@frappe.whitelist()
def mark_thread_read(thread: str) -> dict: ...

@frappe.whitelist()
def block_user(other_alumni: str) -> dict: ...

@frappe.whitelist()
def report_thread(thread: str, reason: str) -> dict: ...

# === Elections (NEW v3) ===
@frappe.whitelist()
def list_elections() -> list[dict]: ...

@frappe.whitelist()
def get_election(election: str) -> dict: ...

@frappe.whitelist()
def submit_nomination(election: str, position: str,
                      manifesto: str, photo: str | None = None,
                      proposed_symbol: str | None = None) -> dict: ...

@frappe.whitelist()
def withdraw_nomination(nomination: str) -> dict: ...

@frappe.whitelist()
def cast_vote(election: str, votes: list[dict]) -> dict:
    """votes = [{"position": str, "candidate": str}, ...]
    Atomic: either all positions recorded or none. Idempotent per (voter, position)."""

@frappe.whitelist()
def comment_on_candidate(candidate: str, body: str) -> dict: ...

# Board Member operations (separate guard)
@frappe.whitelist()
def review_nomination(nomination: str, decision: str,
                      assigned_symbol: str | None = None,
                      reason: str | None = None) -> dict: ...

@frappe.whitelist()
def audit_vote(vote: str, decision: str, notes: str | None = None) -> dict: ...

@frappe.whitelist()
def publish_election_results(election: str) -> dict: ...

# Themes
@frappe.whitelist()
def list_themes() -> list[dict]: ...

@frappe.whitelist()
def activate_theme(theme: str) -> dict: ...

# Webhooks
@frappe.whitelist(allow_guest=True)
def payment_webhook() -> dict: ...

@frappe.whitelist(allow_guest=True)
def bounce_webhook() -> dict: ...

# Public
@frappe.whitelist(allow_guest=True)
def public_stats() -> dict: ...

@frappe.whitelist(allow_guest=True)
def public_events() -> list[dict]: ...

@frappe.whitelist(allow_guest=True)
def public_questions() -> list[dict]: ...   # only is_public=1

@frappe.whitelist(allow_guest=True)
def public_campaigns() -> list[dict]: ...   # NEW v3 — for guest donations

@frappe.whitelist(allow_guest=True)
def public_election_candidates(election: str) -> list[dict]: ...   # NEW v3

@frappe.whitelist(allow_guest=True)
def self_register(payload: dict) -> dict: ...

@frappe.whitelist(allow_guest=True)
def request_email_verification(email: str) -> dict: ...   # NEW v3 — sends OTP/link

@frappe.whitelist(allow_guest=True)
def confirm_email_verification(token: str) -> dict: ...   # NEW v3
```

---

## §08 Scheduled jobs (`tasks.py`)

| Job | Schedule | Mode | Function |
|---|---|---|---|
| Auto-promote graduated students | daily 02:00 | school_connected | `tasks.auto_promote_graduates()` |
| Send pending invitations | daily 09:00 | both | `tasks.send_pending_invitations()` |
| Expire memberships | daily 01:00 | both | `tasks.expire_memberships()` |
| Membership renewal reminders | daily 09:00 | both | `tasks.send_renewal_reminders()` |
| Auto-decline stale mentorship requests | daily 03:00 | both | `tasks.auto_decline_mentorship()` |
| Sync Buzz event statuses | every 30 min | both | `tasks.sync_buzz_event_statuses()` |
| Recompute campaign raised totals | every 15 min | both | `tasks.refresh_campaign_totals()` |
| Send outcome surveys | weekly Mon 10:00 | both | `tasks.dispatch_outcome_surveys()` |
| Refresh reunion group counts | daily 04:00 | both | `tasks.refresh_reunion_groups()` |
| Recurring donations | daily 05:00 | both (no-op v1) | `tasks.process_recurring_donations()` |
| **Advance election states** | every 5 min | both | `tasks.advance_election_states()` — **NEW v3** |
| **Notify nomination deadline** | hourly | both | `tasks.notify_nomination_deadlines()` — **NEW v3** |
| **Recount candidate votes** | every 10 min during voting | both | `tasks.recount_validated_votes()` — **NEW v3** |
| **Purge expired email verification tokens** | daily 00:30 | both | `tasks.purge_expired_tokens()` — **NEW v3** |
| **Cleanup unread message previews** | daily 04:30 | both | `tasks.cleanup_message_previews()` — **NEW v3** |

---

## §09 Email templates (28)

`alumni_invitation`, `alumni_self_registered_pending`, `alumni_email_verification`, `alumni_phone_verification_otp`, `alumni_verification_docs_pending_review`, `alumni_verification_approved`, `alumni_verification_rejected`, `alumni_approved`, `event_booking_confirmed`, `event_reminder_24h`, `job_application_received`, `job_application_status_changed`, `membership_card_issued`, `membership_renewal_reminder`, `donation_receipt`, `guest_donation_receipt`, `mentorship_request_received`, `mentorship_request_accepted`, `mentorship_session_reminder`, `committee_meeting_invite`, `outcome_survey_invitation`, `nomination_received`, `nomination_approved`, `nomination_rejected`, `voting_open_for_eligible_voters`, `vote_confirmation`, `election_results_published`, `new_message_received`, `campaign_comment_published`.

---

## §10 Folder structure

```
alumni/
├── alumni/
│   ├── __init__.py
│   ├── hooks.py
│   ├── api.py
│   ├── tasks.py
│   ├── permissions.py
│   ├── setup/
│   │   ├── wizard.py
│   │   └── install.py
│   ├── integrations/             # Adapter Layer
│   │   ├── __init__.py
│   │   ├── education.py + _real.py + _fallback.py
│   │   ├── receivables.py + _real.py + _fallback.py
│   │   ├── events.py + _real.py     # Buzz wrapper, no fallback
│   │   ├── storage.py + _real.py + _fallback.py
│   │   ├── mail.py + _real.py + _fallback.py
│   │   ├── analytics.py + _real.py + _fallback.py
│   │   ├── live_class.py + _real.py + _fallback.py
│   │   ├── certificates.py + _real.py + _fallback.py
│   │   ├── communication.py + _real.py + _fallback.py
│   │   ├── messaging.py + _real.py + _fallback.py    # NEW v3
│   │   └── verification.py + _real.py + _fallback.py # NEW v3
│   ├── doctype/                  # ~58 doctypes including children
│   ├── workflow/                 # Content / Event / Mentorship / Nomination / Election workflows
│   ├── fixtures/                 # role, role_profile, workflow*, email_template, notification, builder pages, election symbols seed
│   ├── templates/
│   │   ├── pages/                # Jinja public pages
│   │   ├── emails/               # MJML/HTML transactional templates
│   │   └── pdf/                  # WeasyPrint templates for fallback certs
│   ├── www/alumni/               # public site
│   ├── public/{js,css,images}/
│   ├── frontend/                 # Vue 3 + Vite logged-in SPA
│   ├── themes/                   # Default + custom themes
│   │   ├── heritage/
│   │   ├── modern/
│   │   └── bold/
│   ├── reports/                  # Frappe Script Reports for advanced queries
│   ├── dashboard_chart/          # in-app Chart.js dashboards
│   ├── gateways/                 # Custom gateway adapters not in frappe/payments
│   │   └── manual.py
│   ├── tests/                    # test_* files including parametrized mode tests
│   └── modules.txt
├── pyproject.toml
├── requirements.txt              # frappe>=16.0, payments, buzz
├── README.md
├── CLAUDE.md
├── DECISIONS.md
├── SPEC.md
├── INTEGRATIONS.md
├── THEMES.md
├── BUILD_TICKETS.md
├── PROJECT_STATE.md
├── CLAUDE_CODE_SETUP.md
├── CHANGELOG.md
└── license.txt                   # AGPL-3.0
```

---

## §11 Receivables flow (mode-agnostic)

```
[User clicks Buy / Donate / Nominate]           [User clicks Book Event]
        ↓                                                 ↓
[api.py creates source DocType                  [api.book_event(...) calls
 (Membership / Donation / Nomination,            events.book(...) → Buzz]
  status=Pending)]                                       ↓
        ↓                                       [Buzz uses frappe/payments
[receivables.ensure_customer(alumni)]            directly to create
        ↓                                        Payment Request → returns
[receivables.ensure_item(item_code, name)]       payment URL]
        ↓                                                 ↓
[receivables.create_invoice(...)]               [User pays at Buzz checkout]
   → returns invoice_id, payment_url                     ↓
        ↓                                       [Buzz confirms booking via
[Source doc stores invoice_id]                   its own webhook handlers]
        ↓                                                 ↓
[User pays via gateway]                         [tasks.sync_buzz_event_statuses
        ↓                                        picks up confirmed bookings
[gateway → /api/method/alumni.api.payment_webhook]  and emits our notifications]
        ↓
[gateways/<provider>.verify(payload)]
        ↓
[receivables.record_payment(...)]
        ↓
[Source doc → Active / Completed / Approved]
        ↓
[certificates.render(<template>, ctx)]
        ↓
[storage.upload(pdf, folder)]
        ↓
[mail.send_transactional(<template>, ...)]
```

Three parallel paths now (events through Buzz, memberships/donations/**nominations** through our receivables adapter).

---

## §12 In-app dashboards (no Insights dependency)

10 Vue dashboards using Chart.js, data from `analytics_<mode>.py`:

1. **Network Overview** — total alumni, active vs dormant, by passing year, by country, monthly newcomers, profile completion %.
2. **Membership Funnel** — eligible → subscribed → active → renewed; renewal rate; churn reasons.
3. **Event Performance** — pulled from Buzz Event data: tickets sold, no-show %, revenue, repeat attendees.
4. **Donations** — total raised by campaign, donor cohorts, top-N donors, recurring vs one-time, **guest vs alumni split**.
5. **Job Board** — active jobs, apps per job, time-to-hire, posters vs hirers.
6. **Mentorship Impact** — active pairs, sessions per pair, mentee outcomes, reported issues.
7. **Newsletter Engagement** — open rate, click rate, unsubs, segment comparison.
8. **Messaging Health** — **NEW v3** — threads opened, response rate, % blocked, reports filed.
9. **Election Participation** — **NEW v3** — eligible voters, turnout %, turnout by passing year, turnout by chapter, nomination volume by position.
10. **Verification Pipeline** — **NEW v3** — pending email verifications, pending docs review, average time-to-verified, rejection reasons.

If Insights installed, each dashboard shows "Open in Insights →" link.

---

## §13 Cross-app contracts (canonical)

### Whitelisted methods (called externally)
- `alumni.api.payment_webhook` — gateway callbacks
- `alumni.api.bounce_webhook` — Frappe Mail bounces
- `alumni.api.public_stats`
- `alumni.api.public_events`
- `alumni.api.public_questions`
- `alumni.api.public_campaigns`
- `alumni.api.public_election_candidates`
- `alumni.api.self_register`
- `alumni.api.request_email_verification`
- `alumni.api.confirm_email_verification`
- `alumni.api.donate_as_guest`

### Hooks (mode-aware)
- `Student` `on_update` — only school_connected, listens for graduation
- `Buzz Event Booking` `on_update` — listens for booking confirmation, triggers our notifications
- `Alumni Message` `after_insert` — publishes realtime event to recipient's user channel
- `Alumni Vote` `before_insert` — enforces one-vote-per-position-per-voter; logs to audit
- `Alumni Election` scheduler hook — `tasks.advance_election_states()`
- Daily/hourly scheduler — see §08

### Adapter consumers
- `frappe.education.*` (school_connected real)
- `erpnext.*` (school_connected real)
- `buzz.*` (always, via events adapter)
- `frappe/payments` (via Buzz for events; direct config for memberships/donations/nominations)
- `frappe/drive` (storage real)
- `frappe/mail` (mail real)
- `frappe/insights` (analytics real, link only)
- `school_live_class` (optional)
- `school_certificates` (optional)
- `school_communication` (optional)
- Frappe core: OAuth Provider Settings (social login), Two Factor Authentication, Translation, socketio (realtime messaging)
