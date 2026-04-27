# DESIGN_SYSTEM.md — frontend design system

> The visual + interaction vocabulary the alumni app speaks. Every frontend ticket consults this doc. THEMES.md handles tokens; this doc handles the patterns those tokens compose into.

> **Status:** v3 — published with the Aurora dark-mode theme rollout (ADR-043). Authoritative for all frontend work.

---

## §1 Foundations

### 1.1 Design principles

1. **Quiet, not loud.** Alumni networks aren't social media — they don't reward dopamine-engineering. Lean toward calm density over animated novelty.
2. **Information first.** A directory entry should communicate role, location, and connection in one glance — not require five clicks to feel useful.
3. **Mobile-equal, not mobile-after.** Every component is designed at 375px viewport first. The desktop layout is composition, not redesign.
4. **Privacy is a visible feature.** Masked fields show *that* they're masked; lock icons are first-class. Users should *feel* their privacy.
5. **RTL is not a translation toggle.** Layouts must mirror correctly with no broken affordances. Test every component at `[dir="rtl"]`.
6. **Empty states earn their keep.** No "No results" gray text. Every empty state proposes a next action.
7. **One emphasis per screen.** A page has one primary CTA. Two primaries means design failure. Ghost / tertiary actions handle the rest.

### 1.2 Spacing scale

`--space-1` (4px) → `--space-12` (96px). Use only the scale; never arbitrary px values. Touch targets must hit `--space-11` (44px) minimum on mobile.

### 1.3 Typography scale

| Token | Mobile | Desktop | Use |
|---|---|---|---|
| `--font-size-display` | 32 | 48 | Hero headings, the Hall of Fame title |
| `--font-size-h1` | 24 | 32 | Page heading |
| `--font-size-h2` | 20 | 24 | Section heading |
| `--font-size-h3` | 17 | 19 | Sub-section |
| `--font-size-base` | 15 | 15 | Body |
| `--font-size-small` | 13 | 13 | Captions, metadata |
| `--font-size-tiny` | 11 | 11 | Tags, badges, microcopy |

Line height: 1.6 for body, 1.2 for display, 1.3 for h1/h2.

### 1.4 Elevation

Three levels. Below: none. Floating element: `--shadow-1`. Modal / dropdown: `--shadow-2`. Overlay (uncommon): `--shadow-3`. In dark mode (Aurora theme), shadows are subtler (lower alpha) and accompanied by a 1px hairline border so cards still separate from the background.

### 1.5 Motion

| Token | Duration | Easing | Use |
|---|---|---|---|
| `--motion-fast` | 120ms | cubic-bezier(0.2, 0, 0.2, 1) | Hover state, tooltip |
| `--motion-base` | 200ms | cubic-bezier(0.4, 0, 0.2, 1) | Modal open, drawer slide |
| `--motion-slow` | 320ms | cubic-bezier(0.16, 1, 0.3, 1) | Page transition, hero parallax |

`prefers-reduced-motion: reduce` halves all durations and replaces translate/scale with opacity-only transitions.

### 1.6 Breakpoints

```css
--bp-sm: 640px;   /* tablet portrait */
--bp-md: 1024px;  /* desktop / tablet landscape */
--bp-lg: 1280px;  /* large desktop */
```

Three breakpoints, never four. Designs validated at exactly 375 / 768 / 1280.

### 1.7 Color semantics

Never reach for raw colors. Always semantic tokens:
- `--color-bg` page background
- `--color-paper` card / panel surface
- `--color-ink` primary text
- `--color-ink-soft` secondary text
- `--color-rule` borders / dividers
- `--color-accent` primary action
- `--color-accent-soft` accent tint background (for highlighted rows, active nav)
- `--color-success` / `--color-info` / `--color-warning` / `--color-danger` for status

Themes can rebind any of these. Components must never hardcode hex.

---

## §2 Components

Each component has: purpose, anatomy, states, accessibility notes, dark-mode notes, RTL notes, and a Storybook story (per T-091).

### 2.1 Button

**Purpose:** trigger an action.
**Anatomy:** label + optional leading icon + optional trailing icon. No disabled-styled-as-loading — those are different states.
**Variants:**
- **Primary** — filled with `--color-accent`. Max one per screen-region.
- **Secondary** — outlined.
- **Ghost** — no border, just text. Used inside cards.
- **Danger** — filled with `--color-danger`. For destructive actions (delete, remove member, end election).
**Sizes:** `sm` (32px height), `md` (40px), `lg` (48px). `lg` for primary CTAs on landing / hero only.
**States:** rest, hover, active, focus (visible 2px outline using `--color-accent` at 60% alpha), disabled (40% opacity, no hover), loading (spinner replaces icon, label dims to 60%).
**A11y:** native `<button>` only — never a styled `<div>`. `aria-busy="true"` during loading. Disabled buttons get `aria-disabled` + descriptive `title`.
**RTL:** leading icon flips to trailing position automatically when `[dir="rtl"]`. Chevrons (›, ‹) mirror.
**Don't:** stack two primary buttons. Use checkbox + button instead of two buttons. Never set fixed widths — let content size.

### 2.2 Card

**Purpose:** group related content as a discrete unit.
**Anatomy:** outer shell (background `--color-paper`, border `--color-rule`, radius `--radius-md`), header (optional, with icon + title + actions), body (any content), footer (optional, usually with one action).
**Padding:** `--space-5` on tablet+, `--space-4` on mobile.
**States:** rest; clickable cards get hover (lift 2px + shadow upgrade) and active (no lift, shadow off).
**Variants:**
- **Plain** — just the shell.
- **Highlighted** — accent left border 4px, light tint background. Used for featured items.
- **Empty** — see Empty State pattern (§2.10).
**Don't:** nest cards inside cards more than one level. If you want a card-of-cards, use a `<section>` with no shell instead.

### 2.3 Avatar

**Purpose:** identify a person.
**Sizes:** xs (24), sm (32), md (40), lg (56), xl (96 — profile detail).
**Anatomy:** image (rounded — `--radius-pill`) OR initials (filled circle with `--color-accent-soft` background and `--color-accent` text).
**Group:** `<AlumniAvatarGroup count={5} />` overlaps avatars with `-12px` margin and shows "+N" at the end.
**Privacy:** when `privacy_visibility=Hidden`, render the locked-silhouette icon instead.
**Don't:** crop tightly. Profile photos have variable framing — center alignment only.

### 2.4 Input + variants

**Anatomy:** label (above), helper text (below — kept hidden until focus or error), input field, optional leading icon, optional trailing icon (clear button, password reveal).
**Variants:** text, email, phone (with country-code prefix dropdown that auto-detects from `Alumni Profile.current_country`), search (rounded), textarea (auto-grows up to 6 lines), select, multi-select, date, datetime, file upload, rich text.
**States:** rest, focus (2px outline, label color shifts to accent), error (border `--color-danger`, helper text replaced with error message), disabled (50% opacity).
**A11y:** `<label>` always associated; `aria-invalid` on error; `aria-describedby` pointing to helper or error text.
**RTL:** leading icon stays leading (visually flips to right side); placeholder right-aligned.
**Don't:** rely on placeholder as label. Disable autocomplete only when truly needed (e.g., password fields with strict requirements).

### 2.5 Modal

**Purpose:** capture user attention for a single decision or task too long for a tooltip.
**Sizes:** sm (400px), md (560px), lg (720px), full (mobile only — covers the screen).
**Anatomy:** header (title + close X), body, footer (cancel ghost + primary action).
**Behavior:** opens with fade + scale 0.96→1.0 over `--motion-base`. Esc closes. Click outside closes (unless `dismissOnOverlay={false}`). Focus trapped inside; first focusable element auto-focused on open.
**A11y:** `role="dialog"`, `aria-modal="true"`, `aria-labelledby` pointing to title.
**Don't:** stack modals. If you need a modal-from-modal, the design is wrong — use a wizard instead.

### 2.6 Toast

**Purpose:** brief feedback after an action.
**Variants:** success, info, warning, danger (matching color tokens).
**Anatomy:** status icon + message + optional action link + close X.
**Behavior:** appears top-right (top-center on mobile), auto-dismisses after 5s (success/info) or 8s (warning/danger). Hover pauses the timer. Stack vertically with `--space-3` gap.
**A11y:** `role="status"` for success/info, `role="alert"` for warning/danger.
**Don't:** show two toasts for the same action. Don't auto-dismiss errors that require user action — use a danger toast with an explicit "Got it" close, or escalate to a modal.

### 2.7 Tabs

**Purpose:** switch between related views without page navigation.
**Anatomy:** tab list (horizontal on tablet+, scroll-snapped on mobile), active indicator (2px bar in `--color-accent` under the active tab), tab panels.
**Variants:** underline (default), filled (pill), boxed (rare — only for settings).
**A11y:** `role="tablist"`, `role="tab"`, `aria-selected`, `aria-controls`. Arrow keys navigate; Home/End jump to first/last.
**RTL:** active indicator transition reverses direction.
**Don't:** use tabs for distinct destinations (use a sidebar or breadcrumbs instead). Don't stack two tab bars on the same page.

### 2.8 Pagination

**Purpose:** navigate paged lists.
**Variants:** numbered (admin tables), load-more button (feeds, directory), infinite scroll (only for chronological feeds — never directory).
**Mobile:** numbered collapses to "Page X of Y" + prev/next buttons.
**Don't:** infinite-scroll a directory — users lose their place. Always provide a clear page count for navigable lists.

### 2.9 Form layouts

**Single-column** is the default. Two-column forms only when fields are paired (city + country, first + last name).
**Field grouping:** related fields go in a fieldset with a small heading. Visual grouping via `--space-5` between groups, `--space-3` between fields within a group.
**Save bar:** sticky at the bottom on long forms, containing primary save + ghost cancel. On mobile, save bar takes full width.
**Validation:** inline on blur; submit disabled until form is valid (with explanation tooltip on hover for "why is this disabled").

### 2.10 Empty states

Every list, feed, search result, and tab panel has an empty state. Anatomy:
- Illustration (theme-tokenized SVG, ~120×120) — calm, not cartoonish.
- Heading explaining what's empty.
- One sentence proposing the next action.
- Primary action button (when applicable).

**Examples:**
- Directory empty after filter: "No alumni match these filters. Clear filters to see everyone."
- Job board empty: "No jobs posted yet. Be the first to share an opportunity. [Post a job]"
- Inbox empty: "No conversations yet. Find someone in the directory and say hi. [Browse directory]"

Never show "No results" alone. Always offer a way out.

### 2.11 Loading states

**Skeleton screens** (preferred) — gray rounded rectangles in the shape of incoming content, with a subtle shimmer animation.
**Spinners** — only for in-place actions (button click, refreshing a single card). Page-level spinners are forbidden — use a skeleton.
**Streaming** — for feeds, render content as it arrives. The skeleton fades; new items animate in with `--motion-fast`.

### 2.12 Error states

Three levels:
- **Field-level** — inline below the input with `--color-danger` text + leading icon.
- **Card-level** — when a single card fails to load: empty card with retry button, no toast.
- **Page-level** — when an API call fundamental to the page fails: full-page state with illustration, error code, retry button, and "Contact support" link.

**Never:** show raw error messages from the server in user-facing UI. The user-facing string is hand-written; the technical error is logged with a correlation ID that the user can copy.

### 2.13 Tooltip + Popover

**Tooltip** — hover-only on desktop, long-press on mobile, max 60 chars, no interactive content.
**Popover** — for richer content with actions; closes on outside click or Esc.
**Anchoring:** auto-flip when near viewport edge.

### 2.14 Badge + Tag

**Badge** — circular or pill, used for counts (unread, pending, status).
**Tag** — rectangular, used for categories, interests, skills.
**Don't:** use multiple badge colors on the same row — the user can't infer hierarchy. Reserve `--color-danger` badges for genuinely urgent items only.

### 2.15 Avatar Stack & Member Card

Specific to alumni:
- **Member Card** (per ADR-046) — front of digital identity: institution seal, photo, name, passing year, member tier badge, expiry, QR code. Back: emergency contact, perk balance. 600×380px aspect on desktop; full-width on mobile.
- **Profile Header** — avatar (xl), name, passing year, current role, location, completeness ring (small), 2FA + verification badges, primary action ("Message", "Connect", "Request Mentorship").

---

## §3 Patterns

### 3.1 Onboarding wizard (per T-097, ADR-044)
Six steps, progress dots at top, "Skip for now" available on every step except step 1. Each step has one focal field + helper context explaining *why* this field matters ("A photo makes you 4× more likely to be remembered at reunion"). Final step shows the completeness ring before/after.

### 3.2 Directory result row
Avatar + name (linked) + passing year + role + location + chapter (if any) + connection status. Hover reveals "Message" + "View profile" actions on desktop; tap reveals on mobile. Privacy-redacted fields show as `••••` not as empty.

### 3.3 Notification center
Slide-out panel from right (left in RTL). Three tabs: Activity / Mentions / System. Each notification has avatar + body + timestamp + optional action. Mark-all-read at top. Empty state per tab.

### 3.4 Profile public page (per ADR-049)
Full-bleed cover area with Open Graph–optimized layout (1200×630 OG image is the cover image). Sticky title bar appears on scroll past the cover. CTA in the sticky bar adapts: "Message" if logged-in alumni, "Sign in to connect" if guest, "Connect" if peer not in your network.

### 3.5 Election ballot
Three steps: pick position → review candidates side-by-side (manifesto + symbol + photo) → confirm. Each step is a separate page (no modal) — voting is consequential. Confirmation shows "Your vote has been recorded" + optional audit info.

### 3.6 Messaging composer
Iterates the standard chat pattern: thread list left, conversation right, composer pinned bottom. Mobile: thread list and conversation are separate routes. Composer supports text, emoji, image attachment. Typing indicator shown for ≤5s after the last keystroke.

### 3.7 Hero banner (per CMS DocType in T-073)
Full-bleed background image with theme-aware overlay (dark on light themes, gradient on dark theme), heading + subheading + 1 CTA. Multiple banners rotate every 7s with manual prev/next. Mobile: stacks vertically with image at top.

### 3.8 Donation campaign card
Cover image (16:9), title, raised/goal progress bar, days left counter, brief description (≤140 chars), donate CTA. Featured campaigns get the highlighted card variant.

### 3.9 Memorial page (per ADR-045)
Subdued color palette (theme-tokenized "memorial" overlay reducing accent saturation), candle icon, dates ("1972 – 2025"), bio, photo gallery, tributes. CTA: "Leave a tribute" (logged-in alumni) or "Sign in to leave a tribute" (guest with continued public read access).

### 3.10 Hall of Fame entry
Award badge (large), recipient photo, name + passing year, citation in display font, year of award. Click opens the recipient's profile.

---

## §4 Iconography

**Library:** Lucide (paid for the team license; SVG sprites bundled).
**Stroke width:** 1.75px default; 2px for status-critical icons (danger, warning).
**Sizing:** 16, 20, 24, 32 — match the typography scale.
**Color:** inherits from text color; never colored independently except for status icons.

**Special cases:**
- 🔒 lock icon for masked / private fields
- 🕯 candle icon for memorial pages (lit-state for active tributes)
- 🛡 shield icon for verified / 2FA-enabled badges
- 🎖 medal icon for award recipients
- 🎤 microphone icon for speakers in the speaker bureau

**RTL:** directional icons (arrow, chevron, send, undo, redo) auto-mirror via `[dir="rtl"] .icon-directional { transform: scaleX(-1); }`.

---

## §5 Imagery + photography

### 5.1 Profile photos
Auto-cropped to 1:1; stored at three sizes (96, 256, 800) via the storage adapter. AVIF + WebP + JPG fallback. Lazy-loaded below the fold.

### 5.2 Cover images
16:9 aspect; stored at 1200, 1800, 2400 widths. Used for events, campaigns, stories, news, awards.

### 5.3 Alt text required
Every image has alt text. Profile photos use the alumni's full name. Decorative images use empty `alt=""`. CMS-managed images (gallery, hero banner) have an alt-text field on the DocType — empty is rejected by validator.

### 5.4 Stock photography policy
None. Use institutional photography or alumni-submitted photos with explicit permission. Stock photos read as advertising and undermine alumni-network authenticity.

---

## §6 Mobile + PWA

### 6.1 Responsive strategy
Three layouts: mobile (<640), tablet (640–1023), desktop (≥1024). No fluid in-between. Components are designed to look correct at exactly the breakpoint, not interpolated.

### 6.2 Touch targets
All interactive elements ≥44×44 px (per WCAG). Buttons ≥40px height ok if margins extend the hit area to 44.

### 6.3 Bottom navigation (mobile)
Five tabs: Feed / Directory / Messages / Notifications / More. Active tab uses `--color-accent`. The "More" tab opens a drawer with the rest of the app (Events / Donations / Jobs / Mentorship / Elections / Settings).

### 6.4 PWA install prompt
Only after the third visit. Dismissed prompts respected for 30 days. Custom prompt styled per theme — never the browser default chrome.

### 6.5 Offline indicators
A persistent thin banner at the top when offline ("You're offline — showing cached data"). Write actions queue and show a "Will send when you're online" toast.

---

## §7 Accessibility floor

- WCAG 2.1 Level AA mandatory; Level AAA for color contrast on body text.
- Keyboard navigation: every interactive element reachable via Tab; focus order matches visual order; focus indicator always visible (never `outline: none` without replacement).
- Screen reader: tested against NVDA + JAWS + VoiceOver before each release.
- Reduced motion: `prefers-reduced-motion` honored throughout.
- Forced colors (Windows high-contrast mode): components don't break.
- Touch target 44×44 minimum.
- Form validation: announced via `aria-live="polite"` for inline, `assertive` for blocking.
- Dark mode: same accessibility floor — Aurora theme passes WCAG AA at 4.5:1 minimum.

---

## §8 Internationalization + RTL

### 8.1 Translation
All UI strings via `_()` (Python) or `__()` (Vue). No string concatenation — use placeholders. Pluralization via Frappe's `pluralize` helper.

### 8.2 RTL pattern checklist
Every component story has an RTL variant in Storybook. Common gotchas:
- Logical properties (`padding-inline-start`) preferred over `padding-left`.
- Icons that imply direction (arrow, send, undo) must mirror.
- Charts: x-axis flips; legend stays consistent.
- Phone numbers stay LTR even in RTL contexts (use `dir="ltr"` on the input).
- Numbers and dates: locale-aware via `Intl.NumberFormat` and `Intl.DateTimeFormat`.

### 8.3 Languages shipped
English (source), Arabic (RTL), Hindi, Bengali, Spanish, Portuguese, French, Indonesian — top-200 priority strings translated; remainder fall back to English (per T-074, ADR-038).

### 8.4 Content direction
Body alignment: `text-align: start` (logical), never `left` or `right`. RTL-only refinements via `[dir="rtl"]` selectors when logical properties don't suffice.

---

## §9 Performance budgets

- **First Contentful Paint** ≤ 1.8s on 4G mobile (Lighthouse mid-tier device).
- **Time to Interactive** ≤ 3.5s on 4G mobile.
- **Cumulative Layout Shift** ≤ 0.1.
- **Largest Contentful Paint** ≤ 2.5s.
- **Total JS bundle** ≤ 200 KB gzipped for the alumni SPA shell. Routes lazy-load.
- **Image lazy loading** with `loading="lazy"` for below-fold images; `fetchpriority="high"` for hero / above-fold.

CI runs Lighthouse on representative pages every PR; budget breaches block merge.

---

## §10 Storybook + visual regression

- Every documented component has a story with: default, all variants, all sizes, hover, focus, disabled, error, dark mode (Aurora), RTL.
- Visual regression via Chromatic-style snapshots; PRs that change tokens or component CSS surface diffs for review.
- Stories also serve as the source of truth for designers — Figma library auto-syncs nightly via the design tokens JSON.

---

## §11 Theming and white-labeling for SaaS

When SaaS tenants are on the white-label tier (`Alumni Settings.white_label_enabled = 1`):
- "Powered by Alumni" footer hidden.
- Custom favicon honored.
- Custom email signature HTML included in transactional emails.
- PWA manifest uses tenant's app short name + theme color + icons (per T-095, ADR-042).
- Tenant gets full theme override capability via uploaded theme zip.

Free / lower-tier SaaS tenants always show "Powered by Alumni" with a small link to the SaaS provider's marketing site.

---

## §12 Living document

This doc evolves with the product. Process for changes:
1. Open a PR titled "DESIGN_SYSTEM: <change>" with rationale.
2. Update Storybook story for any affected components.
3. Reference the affected ADR if the change is decision-level.
4. Get one frontend review + one design review.

When in doubt, lean toward the existing pattern. Consistency > novelty.
