# MATERIAL 3 SKY NIGHT Design

> Universal deep-night blue UI design system inspired by Material Design 3.
>
> This document generalizes the original product-specific specification into a reusable design system for dashboards, admin panels, internal tools, SaaS products, POS-style interfaces, CRUD applications, and modern web apps.

**Version:** 1.0  
**Status:** Production-ready specification  
**Primary UI direction:** Cool, subtle, calm, functional, elevated, rounded, and nocturnal.

---

## 1. Design Philosophy

MATERIAL 3 SKY NIGHT uses a deep navy foundation with moonlit sky-blue accents and restrained Material 3-inspired elevation.

The system should feel:

- Cool and atmospheric rather than sterile.
- Soft rather than flat or harsh.
- Modern without looking overly futuristic.
- Dense enough for operational interfaces, but still visually calm.
- Suitable for both data-heavy and form-heavy applications.
- Consistent across cards, tables, forms, navigation, feedback states, and overlays.

### Core visual principles

1. Use **deep navy blue** for the application background.
2. Use **layered navy surfaces** for elevated cards, panels, headers, and modals.
3. Use **moonlit sky blue** as the primary interactive color.
4. Prefer **subtle blue-gray borders + soft dark shadows** over strong outlines.
5. Use **large rounded containers** for major surfaces and **pill shapes** for compact states or selectors.
6. Active UI elements should consistently use the primary color family.
7. Status components should use a **tinted background + semantic text color** combination.
8. Motion should be short, subtle, and functional.

---

# 2. Design Tokens

## 2.1 Color Palette & Semantic Tokens

| Token | Value | Usage |
|---|---|---|
| `--bg-main` | `#0B1220` | Main page background; deep night navy |
| `--bg-surface` | `#111A2B` | Cards, headers, elevated panels |
| `--bg-surface-variant` | `#18243A` | Wells, grouped containers, pill backgrounds, table headers |
| `--bg-surface-hover` | `#21314B` | Hover state for items and table rows |
| `--primary` | `#8FB7FF` | Primary actions and visual accent |
| `--primary-hover` | `#A4C5FF` | Primary action hover state |
| `--primary-container` | `#1B355B` | Active badges, icon containers, logo blocks, active toggles |
| `--on-primary-container` | `#D6E5FF` | Text/icons displayed on primary container |
| `--secondary` | `#A9B6CA` | Secondary accent and hover-border emphasis |
| `--secondary-container` | `#263349` | Category tags and neutral badges |
| `--on-secondary-container` | `#E3EBF7` | Text/icons on secondary container |
| `--text-main` | `#EAF1FF` | Main text; cool moonlit near-white |
| `--text-muted` | `#A8B4C7` | Secondary text, helper text, labels |
| `--text-light` | `#76869D` | Tertiary text and placeholders |
| `--border-subtle` | `#29384F` | Default UI borders |
| `--border-active` | `#8FB7FF` | Focused/active border |

### Color usage rules

- The application canvas should normally use `--bg-main`.
- Content surfaces should normally use `--bg-surface`.
- Grouped controls and low-emphasis containers should use `--bg-surface-variant`.
- Do not use pure white for standard text; use `--text-main`.
- The primary sky blue is reserved for interaction, active state, important emphasis, and brand accent.
- Avoid large solid areas of primary sky blue unless the interface explicitly requires a strong focal section.

---

## 2.2 Status Colors

Use status colors semantically. A status is represented by a tinted background paired with its corresponding text color.

| Semantic State | Text | Background | Typical Meaning |
|---|---:|---:|---|
| Pending / Warning | `#E6C26A` | `#40351B` | Waiting, pending, warning |
| Processing / Info | `#8DBDFF` | `#19375A` | In progress, processing, informational |
| Completed / Success | `#79C69A` | `#173A2A` | Success, completed |
| Failed / Error | `#F09A9A` | `#482323` | Failure, error |
| Available | `#7ED3A1` | `#153829` | Available, active, ready |
| Unavailable | `#F0A0A0` | `#442326` | Unavailable, inactive, sold out |

Recommended semantic tokens:

```css
:root {
  --status-pending-text: #E6C26A;
  --status-pending-bg: #40351B;

  --status-info-text: #8DBDFF;
  --status-info-bg: #19375A;

  --status-success-text: #79C69A;
  --status-success-bg: #173A2A;

  --status-error-text: #F09A9A;
  --status-error-bg: #482323;

  --status-available-text: #7ED3A1;
  --status-available-bg: #153829;

  --status-unavailable-text: #F0A0A0;
  --status-unavailable-bg: #442326;
}
```

---

## 2.3 Priority Badges

Priority badges use compact typography and clear semantic emphasis.

| Priority | Color Treatment |
|---|---|
| High | Background `#452629`, text `#FFB4B4` |
| Normal | `--secondary-container` with `--on-secondary-container` |
| Low | Background `#202C3F`, text `#AAB8CC` |

Rules:

- Use `--radius-sm`.
- Use uppercase text.
- Recommended font size: `10px`.
- Keep the label short: `HIGH`, `NORMAL`, `LOW`.

---

# 3. Typography

## 3.1 Font Families

### Heading font

```css
--font-heading: "Lexend Deca", sans-serif;
```

Use **Lexend Deca**, weights `500-700`, for headings and title-level typography, including:

- brand titles
- page and section headings
- card titles
- modal titles
- prominent numeric/stat values when used as display typography

### Body font

```css
--font-body: "Inclusive Sans", sans-serif;
```

Use **Inclusive Sans**, weights `400-700`, for general interface text, including:

- body copy
- labels
- buttons
- form controls
- navigation
- captions and hints
- badges and status text

### Monospace font

```css
--font-mono: "JetBrains Mono", monospace;
```

Use **JetBrains Mono**, weights `400-600`, for:

- IDs
- technical values
- logs
- compact code-like metadata
- printable summaries
- receipts or transaction-style output

### Google Fonts import

```html
<link
  href="https://fonts.googleapis.com/css2?family=Inclusive+Sans:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&family=Lexend+Deca:wght@500;600;700&display=swap"
  rel="stylesheet"
/>
```

---

## 3.2 Type Scale

| Role | Specification |
|---|---|
| Brand Title | `20px / 700 / letter-spacing: -0.3px` |
| Section Title / H2 | `18px / 700` |
| Card Title | `15-16px / 600` |
| Form Label / Stat Label | `12px / 600` |
| Body UI Text | `13-14px / 400-500` |
| Caption / Hint / Badge | `10-12px / 400-600` |

### Typography rules

- Use `18px / 700` for strong section hierarchy inside application screens.
- Use `15-16px / 600` for card-level headings.
- Keep operational UI text compact; `13-14px` is the default body range.
- Do not overuse bold weights. Reserve `700` for brand, section emphasis, values, and primary actions.
- Labels are visually compact but should remain readable at `12px / 600`.

---

# 4. Radius & Elevation

## 4.1 Radius Tokens

| Token | Value | Usage |
|---|---:|---|
| `--radius-sm` | `8px` | Inputs, small buttons, priority badges |
| `--radius-md` | `14px` | Item cards, toast, icon/logo boxes |
| `--radius-lg` | `20px` | Main cards, headers, modals |
| `--radius-full` | `9999px` | Pills, tags, toggles, circular buttons |

Recommended CSS:

```css
:root {
  --radius-sm: 8px;
  --radius-md: 14px;
  --radius-lg: 20px;
  --radius-full: 9999px;
}
```

---

## 4.2 Shadow Tokens

All shadows use a restrained neutral-black tone suited to dark navy surfaces.

### Small shadow

```css
--shadow-sm:
  0 1px 3px rgba(0, 0, 0, 0.18),
  0 1px 2px rgba(0, 0, 0, 0.12);
```

Use for:

- cards
- headers
- small elevated surfaces

### Medium shadow

```css
--shadow-md:
  0 4px 14px rgba(0, 0, 0, 0.24),
  0 2px 6px rgba(0, 0, 0, 0.16);
```

Use for:

- elevated hover states
- sticky panels
- stronger content separation

### Large shadow

```css
--shadow-lg:
  0 12px 32px rgba(0, 0, 0, 0.32),
  0 4px 12px rgba(0, 0, 0, 0.20);
```

Use for:

- modal dialogs
- toast notifications
- foreground overlays

### Elevation rule

Prefer subtle elevation. A component should normally combine:

```text
surface + subtle border + radius + restrained shadow
```

Avoid strong drop shadows or bright glowing shadows.

---

# 5. Spacing & Layout

## 5.1 Main Container

```css
.app-container {
  max-width: 1240px;
  margin: 0 auto;
  padding: 24px 20px 60px;
}
```

## 5.2 Spacing Guidelines

- Main grid gap: `24px`
- Gap between related cards/items: `16px`
- Header padding: `16px 24px`
- Header bottom spacing: `24px`
- Typical card padding: `24px`
- Compact stat card padding: `18px 20px`

## 5.3 Responsive Behavior

At viewport widths `<= 960px`:

- Multi-column application layouts collapse to a single vertical column.
- Sticky side panels should return to normal document flow when appropriate.
- Horizontal control groups may wrap rather than shrink excessively.

## 5.4 Common Grid Patterns

### Form + content

```css
grid-template-columns: 420px 1fr;
gap: 24px;
```

Use when the left panel is a focused form/control area and the right panel contains the main dataset or preview.

### Main content + side panel

```css
grid-template-columns: 1fr 380px;
gap: 24px;
```

The side panel may use:

```css
position: sticky;
top: 24px;
```

Use for carts, summaries, inspectors, properties panels, or contextual details.

---

# 6. Component Specifications

## 6.1 App Bar / Header

**Visual recipe:**

```text
flex + surface + border + radius-lg + shadow-sm
```

### Structure

- `display: flex`
- `justify-content: space-between`
- `align-items: center`
- `background: var(--bg-surface)`
- `border: 1px solid var(--border-subtle)`
- `border-radius: var(--radius-lg)`
- `box-shadow: var(--shadow-sm)`
- `padding: 16px 24px`

### Left group

Optional brand/icon block:

- Size: `44px x 44px`
- Background: `--primary-container`
- Radius: `--radius-md`
- Icon size: about `22px`

Title group:

- Primary title: `20px / 700`
- Subtitle/context line: `13px`, muted

### Right group

May contain:

- connectivity/status pill
- user/account controls
- refresh/sync action
- circular icon button around `34px`

---

## 6.2 Status Pill

Use for compact live state indicators.

### Specification

- `border-radius: var(--radius-full)`
- Typography: `12px / 600`
- Optional status dot: `8px` circle
- Dot uses `currentColor`
- Use tinted semantic background + corresponding semantic text color

Examples of generic states:

```text
Online
Offline
Ready
Processing
Completed
Unavailable
```

---

## 6.3 Stat Card

Use for KPIs, counters, totals, operational metrics, or summaries.

### Structure

```text
[ icon wrapper ] [ label / value / supporting text ]
```

### Specification

- `display: flex`
- `gap: 16px`
- `padding: 18px 20px`
- Icon wrapper: `44px`
- Label: `12px`
- Main value: `18px / 700`
- Supporting text: `11px`
- Use a subtle tinted icon background relevant to the metric

---

## 6.4 Standard Card

The default reusable content surface.

### Specification

```css
.card {
  background: var(--bg-surface);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-sm);
  padding: 24px;
}
```

### Card header

- `display: flex`
- `justify-content: space-between`
- Optional icon: `18px`
- Title: `18px / 700` for major cards, or `15-16px / 600` for regular cards

Use this component as the default surface for:

- summaries
- detail panels
- forms
- data sections
- settings
- charts
- content groups

---

## 6.5 Pill Button & Tab Navigation

### Pill buttons

Base:

- `border-radius: var(--radius-full)`

Idle state:

- `border: 1px solid var(--border-subtle)`
- text: `--text-muted`
- background: surface or transparent

Hover:

- `background: var(--bg-surface-variant)`

Active:

- `background: var(--primary)`
- text: `#07111F`

### Segmented tab navigation

Container:

- `background: var(--bg-surface-variant)`
- `border-radius: var(--radius-full)`

Active segment:

- `background: var(--bg-surface)`
- text: `var(--primary)`
- `box-shadow: var(--shadow-sm)`

---

## 6.6 Buttons

### Primary Button

```css
.btn-primary {
  background: var(--primary);
  color: #07111F;
  font-weight: 700;
  border-radius: var(--radius-md);
  padding: 12px;
  box-shadow: var(--shadow-sm);
  transition: 0.15s ease;
}

.btn-primary:hover {
  background: var(--primary-hover);
  transform: translateY(-1px);
}
```

For production usage, horizontal padding may be added according to button content.

### Outline Button

- `1px` border using `--border-subtle`
- `--radius-sm`
- surface background
- font weight `600`
- cool high-contrast text

### Ghost Button

- no persistent background
- muted text/icon color
- use for low-emphasis utility actions

### Danger Ghost Button

- no persistent background
- muted or error text at rest
- red semantic emphasis on hover

### Button hierarchy

1. Primary - main action
2. Outline - secondary action
3. Ghost - utility action
4. Danger - destructive action

Avoid displaying multiple primary buttons within the same local action group.

---

## 6.7 Form Controls & Segmented Toggle

### Label

- `12px / 600`
- use `--text-main` or `--text-muted` depending on hierarchy

### Input / Select / Textarea

```css
.form-control {
  padding: 10px 12px;
  border-radius: var(--radius-sm);
  border: 1px solid var(--border-subtle);
  background: var(--bg-surface);
  color: var(--text-main);
}

.form-control:focus {
  border-color: var(--primary);
  outline: none;
}
```

Placeholder:

```css
color: var(--text-light);
```

### Segmented Toggle

Container:

- background `--bg-surface-variant`
- radius `--radius-full`
- padding `4px`

Active segment:

- background `--bg-surface`
- text `--primary`
- `--shadow-sm`

---

## 6.8 Badge / Tag Status

### Standard status badge

- `border-radius: var(--radius-full)`
- tinted semantic background
- semantic text color
- typography: `11px / 700`
- padding: `3px 10px`

### Priority badge

- `border-radius: var(--radius-sm)`
- uppercase
- approximately `10px`
- use High / Normal / Low priority colors from the priority token section

---

## 6.9 Progress Bar

### Base

- Height: `8px`
- `border-radius: var(--radius-full)`
- width transition: `0.3s`

### Progress colors

Processing gradient:

```css
background: linear-gradient(90deg, #6EA8FF, #9AC6FF);
```

Completed:

```css
background: #69C48D;
```

Pending:

```css
background: #DDB65D;
```

Failed:

```css
background: #E98383;
```

---

## 6.10 Modal

### Backdrop

```css
.modal-backdrop {
  background: rgba(3, 8, 16, 0.72);
  backdrop-filter: blur(4px);
  z-index: 1100;
  padding: 20px;
}
```

### Modal surface

- background: `--bg-surface`
- radius: `--radius-lg`
- shadow: `--shadow-lg`
- width: approximately `440-580px` depending on content

### Entry animation

```text
scale(0.96) -> scale(1)
opacity fade-in
0.2s
```

Use modals for focused decisions, confirmations, compact forms, and high-priority overlays.

---

## 6.11 Toast

### Placement

- `position: fixed`
- top-right offset: `24px`

### Surface

- `--radius-md`
- `--shadow-lg`

### Motion

- slide in from approximately `-12px` vertical offset
- opacity fade
- duration: `0.25s`
- auto-hide: approximately `3.5s`

### Variants

- Info - surface variant / blue semantic treatment
- Success - green tint
- Warning - amber tint
- Error - red tint

---

## 6.12 Table

### Header cells

```css
th {
  text-transform: uppercase;
  font-size: 12px;
  letter-spacing: 0.5px;
  background: var(--bg-surface-variant);
}
```

### Body cells

```css
td {
  font-size: 14px;
  border-bottom: 1px solid var(--border-subtle);
  padding: 14px 16px;
}
```

Recommended hover:

```css
tr:hover td {
  background: var(--bg-surface-hover);
}
```

Use tables for structured operational data; keep status values represented with semantic badges rather than raw colored text when space allows.

---

## 6.13 Monospace Summary / Printable Panel

This component generalizes the original receipt-style visual into a reusable technical or printable summary panel.

Suitable for:

- transaction summaries
- printable output
- logs
- order summaries
- invoices
- IDs and machine-readable metadata
- compact technical summaries

### Specification

- Dark technical background: `#0E1726`
- Border: `#263750`
- Radius: `--radius-md`
- Subtle inset shadow
- Font: JetBrains Mono, `13px`
- Dashed divider: `#3B4D67`
- Strong total/final divider: `#DDE8F8`

Example:

```text
REFERENCE #A1024
2026-09-25 14:30
----------------------------
Item A                  28.00
Item B                  30.00
============================
TOTAL                   58.00
```

---

## 6.14 Empty State

Use when a dataset, panel, search result, cart, list, or workspace has no content.

### Specification

- Center aligned
- Muted icon: `32px`
- Main empty-state text: `14px / 600`
- Supporting hint: `12px`
- Vertical/internal padding: approximately `48px`

Structure:

```text
[ muted icon ]
No Data Yet
Supporting instruction or next action.
```

The empty state should explain both **what is missing** and **what the user can do next**.

---

# 7. Animation & Micro-Interaction

| Animation | Duration / Easing | Effect / Target |
|---|---|---|
| `slideIn` | `0.25s` | Toast: `translateY(-12px) -> 0` + opacity fade |
| `modalPop` / `modalScale` | `0.2s` | Modal: `scale(0.96) -> 1` + opacity fade |
| `spin` | `1.2s linear infinite` | Loading or processing icon |
| Button hover | `0.15s` | Background transition + subtle `translateY(-1px)` |

## Motion principles

- Motion should explain state change, not decorate the screen.
- Avoid slow transitions.
- Avoid large translation distances.
- Prefer opacity, scale, and very small positional movement.
- Hover elevation should be subtle.

---

# 8. Iconography

Recommended library: **lucide-react**.

### Icon convention

- Standard size: `18-22px`
- Stroke width: `1.5-2.2`
- Color: inherit from container using `currentColor`

Example:

```tsx
<Search size={20} strokeWidth={1.8} />
```

Icons should support meaning, not replace critical labels when the action could be ambiguous.

---

# 9. Global Interaction Rules

## 9.1 Active Components

Active components should consistently use `--primary` or the primary color family.

Examples:

- active tab
- selected pill
- selected navigation item
- focused border
- primary action button
- active control indicator

## 9.2 Status Components

Always combine:

```text
tinted semantic background + matching semantic text color
```

Do not rely on a saturated text color alone when a badge/pill treatment is available.

## 9.3 Hover States

Recommended hierarchy:

- Neutral item hover -> `--bg-surface-hover`
- Primary action hover -> `--primary-hover`
- Elevated interactive surface -> optional `--shadow-md`
- Button hover -> optional `translateY(-1px)`

## 9.4 Focus States

Form controls and interactive bordered components should use:

```css
border-color: var(--border-active);
```

Keep focus treatment visually consistent with the primary color family.

---

# 10. Complete CSS Token Starter

```css
:root {
  /* Background */
  --bg-main: #0B1220;
  --bg-surface: #111A2B;
  --bg-surface-variant: #18243A;
  --bg-surface-hover: #21314B;

  /* Primary */
  --primary: #8FB7FF;
  --primary-hover: #A4C5FF;
  --primary-container: #1B355B;
  --on-primary-container: #D6E5FF;

  /* Secondary */
  --secondary: #A9B6CA;
  --secondary-container: #263349;
  --on-secondary-container: #E3EBF7;

  /* Text */
  --text-main: #EAF1FF;
  --text-muted: #A8B4C7;
  --text-light: #76869D;

  /* Border */
  --border-subtle: #29384F;
  --border-active: #8FB7FF;

  /* Status */
  --status-pending-text: #E6C26A;
  --status-pending-bg: #40351B;
  --status-info-text: #8DBDFF;
  --status-info-bg: #19375A;
  --status-success-text: #79C69A;
  --status-success-bg: #173A2A;
  --status-error-text: #F09A9A;
  --status-error-bg: #482323;
  --status-available-text: #7ED3A1;
  --status-available-bg: #153829;
  --status-unavailable-text: #F0A0A0;
  --status-unavailable-bg: #442326;

  /* Priority */
  --priority-high-bg: #452629;
  --priority-high-text: #FFB4B4;
  --priority-low-bg: #202C3F;
  --priority-low-text: #AAB8CC;

  /* Radius */
  --radius-sm: 8px;
  --radius-md: 14px;
  --radius-lg: 20px;
  --radius-full: 9999px;

  /* Shadow */
  --shadow-sm:
    0 1px 3px rgba(0, 0, 0, 0.18),
    0 1px 2px rgba(0, 0, 0, 0.12);

  --shadow-md:
    0 4px 14px rgba(0, 0, 0, 0.24),
    0 2px 6px rgba(0, 0, 0, 0.16);

  --shadow-lg:
    0 12px 32px rgba(0, 0, 0, 0.32),
    0 4px 12px rgba(0, 0, 0, 0.20);

  /* Typography */
  --font-heading: "Lexend Deca", sans-serif;
  --font-body: "Inclusive Sans", sans-serif;
  --font-mono: "JetBrains Mono", monospace;
}
```

---

# 11. Base Application Shell

```css
html,
body {
  margin: 0;
  min-height: 100%;
  background: var(--bg-main);
  color: var(--text-main);
  font-family: var(--font-body);
}

* {
  box-sizing: border-box;
}

h1,
h2,
h3,
h4,
h5,
h6,
.brand-title,
.card-title,
.modal-title {
  font-family: var(--font-heading);
}

.app-container {
  width: 100%;
  max-width: 1240px;
  margin: 0 auto;
  padding: 24px 20px 60px;
}
```

Recommended page hierarchy:

```text
Application Background
└── Main Container
    ├── App Header
    ├── Optional Metrics / Navigation
    └── Main Grid
        ├── Primary Content
        └── Optional Contextual Side Panel
```

---

# 12. Universal Component Composition Patterns

## Pattern A - Data Dashboard

```text
Header
Metrics Row
Main Grid
├── Data / Visualization Card
└── Detail / Summary Card
Table / Activity Card
```

## Pattern B - CRUD / Internal Tool

```text
Header
Tab / Filter Pills
Main Grid: 420px + 1fr
├── Form Card
└── Data List / Table Card
```

## Pattern C - Product / Transaction Flow

```text
Header
Category Pills
Main Grid: 1fr + 380px
├── Catalog / Main Content
└── Sticky Summary Panel
```

## Pattern D - Settings / Configuration

```text
Header
Section Card
├── Labels
├── Inputs / Selects / Toggles
└── Primary + Secondary Actions
```

These are composition patterns, not domain-specific requirements. The same tokens and component behavior should remain consistent across different products.

---

# 13. Implementation Guidance for React / Next.js / Vite

The design system is framework-agnostic, but implementation should preserve the token hierarchy.

Recommended structure:

```text
styles/
├── tokens.css
├── globals.css
└── components.css

components/ui/
├── Button
├── Card
├── Badge
├── StatusPill
├── Input
├── Select
├── SegmentedToggle
├── Tabs
├── Modal
├── Toast
├── Progress
├── Table
└── EmptyState
```

### Implementation rule

Do not hardcode visual values repeatedly inside individual components when an existing design token is available.

Prefer:

```css
color: var(--text-muted);
border-color: var(--border-subtle);
border-radius: var(--radius-md);
```

Instead of repeating raw values throughout the codebase.

---

# 14. Non-Negotiable Visual Rules

To keep the MATERIAL 3 SKY NIGHT identity consistent:

1. Main app background is deep navy, not pure black.
2. Elevated content uses layered navy surface tones.
3. Primary actions use moonlit sky blue.
4. Active controls belong to the same primary color family.
5. Major cards and overlays use rounded geometry.
6. Pills/tags/toggles use `--radius-full`.
7. Borders remain subtle and blue-gray.
8. Shadows remain soft and dark.
9. Semantic states use tinted backgrounds plus matching semantic text.
10. Headings and title-level typography use Lexend Deca.
11. General UI and body typography use Inclusive Sans.
12. Technical/print-style values use JetBrains Mono.
13. Motion remains brief and functional.
14. Responsive layouts collapse cleanly to one column at `<= 960px`.

---

# 15. Quick Reference

```text
STYLE NAME
MATERIAL 3 SKY NIGHT

PRIMARY
#8FB7FF

PRIMARY HOVER
#A4C5FF

PAGE BG
#0B1220

SURFACE
#111A2B

SURFACE VARIANT
#18243A

TEXT MAIN
#EAF1FF

TEXT MUTED
#A8B4C7

BORDER
#29384F

HEADING FONT
Lexend Deca

BODY FONT
Inclusive Sans

MONO FONT
JetBrains Mono

RADIUS
8 / 14 / 20 / pill

MAIN CONTAINER
1240px

MAIN GRID GAP
24px

CARD GAP
16px

RESPONSIVE COLLAPSE
<= 960px

CARD
surface + subtle border + radius-lg + shadow-sm

ACTIVE STATE
primary color family

STATUS STATE
tinted semantic bg + semantic text
```

---

## Design System Identity

**MATERIAL 3 SKY NIGHT** is a universal cool-dark UI system built around:

```text
Deep Navy Night Canvas
+ Layered Navy Elevated Surfaces
+ Moonlit Sky Blue Primary Accent
+ Rounded Material-Inspired Geometry
+ Soft Dark Tonal Elevation
+ Compact Operational Typography
+ Semantic Tinted Feedback States
```

Use this document as the single visual reference when implementing or generating interfaces that should follow the MATERIAL 3 SKY NIGHT design language.
