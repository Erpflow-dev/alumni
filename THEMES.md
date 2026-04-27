# THEMES.md — theming system

Four production-ready themes ship by default — **Heritage**, **Modern**, **Bold**, and **Aurora** (dark mode). Switching is one click in **Alumni Settings → Theme**. Adding a new theme is one file.

> THEMES.md owns the **visual token contract** — what colors, fonts, spacing, and elevation a theme defines. The **interaction contract** (component patterns, motion, empty/loading/error states, accessibility floor, performance budgets, RTL specifics, white-labeling) lives in `DESIGN_SYSTEM.md`. A custom theme works on top of both: tokens here, patterns there.

---

## How themes work

Each theme is a folder under `alumni/themes/<theme_id>/` containing:

```
alumni/themes/heritage/
├── theme.json          # metadata + token overrides
├── tokens.css          # CSS custom properties (the contract)
├── preview.png         # 800×500 thumbnail for the picker
├── components.css      # optional: per-component overrides
└── assets/             # optional: theme-specific images, fonts
```

Both the public Jinja site (`www/`) and the Vue logged-in SPA (`frontend/`) read **CSS custom properties** from a single root stylesheet. Switching themes only swaps which `tokens.css` is loaded — no Vue rebuild needed, no Jinja change.

The contract is the token list. As long as a theme defines all required tokens, every page renders correctly.

### Required tokens

```css
/* tokens.css contract — every theme must define these */
:root {
  /* Colors */
  --color-bg:           #fbf8f3;   /* page background */
  --color-paper:        #ffffff;   /* card/panel background */
  --color-ink:          #1a1a1a;   /* primary text */
  --color-ink-soft:     #3a3a3a;   /* secondary text */
  --color-rule:         #d9d3c5;   /* borders / dividers */
  --color-accent:       #b4451f;   /* primary action */
  --color-accent-soft:  #fbece4;   /* accent tint background */
  --color-success:      #2d5a3d;
  --color-info:         #1e4d6b;
  --color-warning:      #8a6d1f;
  --color-danger:       #b4451f;

  /* Typography */
  --font-display:       'Fraunces', Georgia, serif;
  --font-body:          'IBM Plex Sans', system-ui, sans-serif;
  --font-mono:          'JetBrains Mono', monospace;
  --font-size-base:     15px;
  --line-height-base:   1.6;
  --letter-spacing-display: -0.02em;
  --font-weight-display: 800;
  --font-weight-body:   400;

  /* Spacing scale (4px base) */
  --space-1:  4px;
  --space-2:  8px;
  --space-3:  12px;
  --space-4:  16px;
  --space-5:  24px;
  --space-6:  32px;
  --space-8:  48px;
  --space-10: 64px;
  --space-12: 96px;

  /* Radii */
  --radius-sm: 3px;
  --radius-md: 6px;
  --radius-lg: 10px;
  --radius-pill: 999px;

  /* Elevation */
  --shadow-1: 0 1px 2px rgba(0,0,0,.06);
  --shadow-2: 0 4px 14px rgba(0,0,0,.08);
  --shadow-3: 0 12px 40px rgba(0,0,0,.12);

  /* Layout */
  --container-max: 1080px;
  --container-padding: 32px;
  --header-height: 72px;
}
```

A theme that omits any required token fails the validator at `bench install-app` time and on theme upload.

---

## RTL support (NEW v3, per ADR-038)

Per ADR-038 the app ships multilingual + RTL by default. Themes declare RTL capability in `theme.json`:

```json
{
  "id": "heritage",
  "name": "Heritage",
  "supports_rtl": true,
  ...
}
```

A theme that declares `supports_rtl: true` MUST either (a) work correctly with default RTL flipping (the common case — most token-driven themes do), or (b) ship a sibling `tokens.rtl.css` that overrides the LTR tokens with RTL-appropriate values (e.g., directional spacing, mirrored shadows, swapped quote glyphs).

### How RTL is applied

When the user's `preferred_language` is RTL (Arabic, Hebrew, etc.), the layout sets `dir="rtl"` on `<html>`. Component CSS handles the flip via `[dir="rtl"]` selectors:

```css
/* LTR default */
.alumni-card { padding-left: var(--space-4); border-left: 2px solid var(--color-accent); }

/* RTL override */
[dir="rtl"] .alumni-card { padding-left: 0; padding-right: var(--space-4);
                           border-left: 0; border-right: 2px solid var(--color-accent); }
```

For most cases CSS logical properties (`padding-inline-start`, `border-inline-start`) work without explicit `[dir="rtl"]` selectors. Use logical properties first; fall back to `[dir="rtl"]` only when a property has no logical equivalent (e.g., `transform` rotations on icons).

### Theme validator RTL checks

The validator additionally enforces (when `supports_rtl: true`):

- All directional spacing in component CSS uses logical properties OR has a matching `[dir="rtl"]` override
- No `text-align: left` / `text-align: right` literals — use `start` / `end`
- Icons that imply direction (arrows, chevrons) have a `[dir="rtl"]` mirror rule

A theme that claims RTL support but fails these rules is rejected at validation time.

### All three default themes support RTL

Heritage, Modern, and Bold all declare `supports_rtl: true` and pass the validator. The 3 themes were redesigned in v3 to use logical properties throughout.

### What about RTL-only themes?

A theme can set `supports_rtl: true` and additionally `ltr_supported: false` if it's an RTL-only design (e.g., a calligraphy-heavy Arabic-first theme). The picker shows it only when an RTL language is active.

---

## The 3 default themes

### 1. Heritage
Serif headlines, warm cream paper background, deep terracotta accent. Quiet, authoritative, classical. Best for old institutions.

```css
:root {
  --color-bg: #fbf8f3;
  --color-accent: #b4451f;
  --font-display: 'Fraunces', Georgia, serif;
  --font-weight-display: 800;
  --letter-spacing-display: -0.02em;
}
```

### 2. Modern
Clean sans-serif throughout, bright off-white background, soft indigo accent, generous whitespace. Best for tech institutes, modern colleges.

```css
:root {
  --color-bg: #ffffff;
  --color-paper: #f5f7fb;
  --color-accent: #4f46e5;
  --font-display: 'Inter', system-ui, sans-serif;
  --font-body: 'Inter', system-ui, sans-serif;
  --font-weight-display: 700;
  --letter-spacing-display: -0.025em;
  --container-padding: 40px;
}
```

### 3. Bold
High-contrast black/white, oversized display type, vivid primary accent, blocky panels. Best for sports schools, arts academies.

```css
:root {
  --color-bg: #0f0f0f;
  --color-paper: #1a1a1a;
  --color-ink: #ffffff;
  --color-ink-soft: #cfcfcf;
  --color-rule: #2a2a2a;
  --color-accent: #f43f5e;
  --font-display: 'Space Grotesk', sans-serif;
  --font-weight-display: 800;
  --letter-spacing-display: -0.04em;
  --radius-md: 0;     /* sharp corners */
}
```

### 4. Aurora — NEW v3 (dark mode, per ADR-043)
Calm dark surfaces, neon-cyan accent, hairline rules instead of strong shadows. Auto-engages when the user's OS preference is dark and they haven't set a theme. Maintains WCAG AA 4.5:1 contrast on all body text.

```css
:root {
  --color-bg: #0a1020;
  --color-paper: #111a30;
  --color-ink: #e5edf7;
  --color-ink-soft: #97a8c4;
  --color-rule: #1d2949;        /* hairline borders, not shadows */
  --color-accent: #38bdf8;
  --color-accent-soft: #0c2638;
  --color-success: #34d399;
  --color-info: #60a5fa;
  --color-warning: #fbbf24;
  --color-danger: #f87171;
  --font-display: 'Inter', system-ui, sans-serif;
  --font-body: 'Inter', system-ui, sans-serif;
  --shadow-1: 0 1px 0 rgba(255,255,255,.04);    /* subtle separation */
  --shadow-2: 0 4px 14px rgba(0,0,0,.5);
}
```

`theme.json` declares `"color_scheme": "Dark"` so the theme picker shows it under a dark-mode group, and the auto-detect logic (`prefers-color-scheme: dark`) defaults to it when the user has no explicit preference.

---

## Adding a custom theme

### Option A — UI upload (institution admin)

1. **Alumni Settings → Theme → Upload custom theme**.
2. Select a `.zip` containing the theme folder structure above.
3. The validator runs:
   - All required tokens present? ✅
   - `theme.json` parses? ✅
   - `preview.png` ≤ 500 KB? ✅
   - No `<script>` tags or `@import url(...)` to external domains in CSS? ✅
4. Theme appears in the picker. Activate.

This is for non-technical admins who get a ready-made theme from a designer. No code deploy.

### Option B — Repo (developer)

1. Create folder `alumni/themes/<your_id>/` in the source repo.
2. Add `theme.json`:
   ```json
   {
     "id": "midnight",
     "name": "Midnight",
     "description": "Dark mode with cyan accent for night owls.",
     "author": "Your School",
     "version": "1.0.0",
     "preview": "preview.png",
     "frappe_min_version": "16"
   }
   ```
3. Add `tokens.css` with all required tokens (override only what differs from defaults).
4. Add `preview.png` (800×500 PNG).
5. Optionally add `components.css` for per-component tweaks (button radius, card padding, etc).
6. Run `bench --site yoursite.local migrate` — the new theme is auto-discovered.
7. Pick it in **Alumni Settings → Theme**.

### Option C — Theme inheritance (designer-friendly)

Set a `parent` field in `theme.json` to inherit one of the defaults and override only what differs:

```json
{
  "id": "heritage_navy",
  "name": "Heritage — Navy",
  "parent": "heritage",
  "preview": "preview.png"
}
```

Then `tokens.css` only needs to override the changed tokens:

```css
:root {
  --color-accent: #1e3a8a;
  --color-accent-soft: #dbeafe;
}
```

The validator merges parent + child tokens at install time.

---

## Theme picker UX

The Settings → Theme page renders a 3-column grid of theme cards with the `preview.png` thumbnail, name, description, and an "Activate" button. The currently active theme has a green checkmark. Custom themes appear after the defaults in a separate section.

Hover on a card → live preview (loads tokens into a hidden iframe of the public landing page).

---

## How it's stored

`Alumni Settings.theme_id` — Data field, default `heritage`, options populated dynamically from the discovered theme folders.

On change, a `before_save` hook validates the theme exists, then writes the active theme's `tokens.css` to `/alumni/public/css/active-theme.css` (the file Jinja and Vue both load).

This means **switching themes is instant** — no rebuild, no migration.

---

## Public site vs logged-in SPA

Both consume the same `active-theme.css`. The Jinja public pages load it via `<link>` in the base layout. The Vue SPA imports it once at startup.

Component CSS in both contexts uses *only* the tokens — never literal hex codes. CI lints for hex/rgb literals in component files (allowed only in `tokens.css`).

---

## Performance

`active-theme.css` is small (~3 KB). It's served with `Cache-Control: max-age=86400, must-revalidate` and a content hash in the filename so theme changes invalidate cache instantly.

---

## Accessibility floor

Every shipped theme passes WCAG AA contrast for `--color-ink` on `--color-bg` and `--color-paper`. The validator runs an automated contrast check on upload using `wcag-contrast`. Themes failing minimum 4.5:1 contrast are rejected.

The Bold theme intentionally pushes contrast — that's why it passes easily. Modern uses indigo with soft contrast — verified at 7.2:1.

---

## What you cannot change via theme

The token system is deliberately scoped to visual presentation. These stay fixed:

- Layout topology (header above content above footer)
- Component structure (don't reorder feed → directory → events)
- Information hierarchy (don't promote a tertiary CTA to primary)
- Accessibility behaviors (focus rings, keyboard navigation, ARIA)

If a theme designer needs deeper changes, they can fork and override component templates — but that's a code-level change, not a theme.

---

## Testing your theme

```bash
# 1. Drop your theme folder in alumni/themes/<your_id>/
# 2. Run the theme test suite
bench --site test.local run-tests --app alumni --module tests.themes

# Tests check:
# - All required tokens defined
# - Preview image dimensions OK
# - WCAG AA contrast passes
# - No script injection / external imports in CSS
# - theme.json schema valid
```

CI runs this on every PR.
