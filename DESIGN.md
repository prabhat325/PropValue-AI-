---
name: Real Estate Analytics Design System
colors:
  surface: '#faf8ff'
  surface-dim: '#d2d9f4'
  surface-bright: '#faf8ff'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#f2f3ff'
  surface-container: '#eaedff'
  surface-container-high: '#e2e7ff'
  surface-container-highest: '#dae2fd'
  on-surface: '#131b2e'
  on-surface-variant: '#444653'
  inverse-surface: '#283044'
  inverse-on-surface: '#eef0ff'
  outline: '#757684'
  outline-variant: '#c4c5d5'
  surface-tint: '#3755c3'
  primary: '#00288e'
  on-primary: '#ffffff'
  primary-container: '#1e40af'
  on-primary-container: '#a8b8ff'
  inverse-primary: '#b8c4ff'
  secondary: '#006a61'
  on-secondary: '#ffffff'
  secondary-container: '#86f2e4'
  on-secondary-container: '#006f66'
  tertiary: '#4c2e00'
  on-tertiary: '#ffffff'
  tertiary-container: '#6b4200'
  on-tertiary-container: '#ffa929'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#dde1ff'
  primary-fixed-dim: '#b8c4ff'
  on-primary-fixed: '#001453'
  on-primary-fixed-variant: '#173bab'
  secondary-fixed: '#89f5e7'
  secondary-fixed-dim: '#6bd8cb'
  on-secondary-fixed: '#00201d'
  on-secondary-fixed-variant: '#005049'
  tertiary-fixed: '#ffddb8'
  tertiary-fixed-dim: '#ffb95f'
  on-tertiary-fixed: '#2a1700'
  on-tertiary-fixed-variant: '#653e00'
  background: '#faf8ff'
  on-background: '#131b2e'
  surface-variant: '#dae2fd'
typography:
  display-lg:
    fontFamily: Inter
    fontSize: 48px
    fontWeight: '700'
    lineHeight: 56px
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Inter
    fontSize: 32px
    fontWeight: '600'
    lineHeight: 40px
    letterSpacing: -0.01em
  headline-lg-mobile:
    fontFamily: Inter
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
  headline-md:
    fontFamily: Inter
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
  body-lg:
    fontFamily: Inter
    fontSize: 18px
    fontWeight: '400'
    lineHeight: 28px
  body-md:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  body-sm:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
  label-caps:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '700'
    lineHeight: 16px
    letterSpacing: 0.05em
  data-mono:
    fontFamily: JetBrains Mono
    fontSize: 14px
    fontWeight: '500'
    lineHeight: 20px
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  base: 4px
  xs: 4px
  sm: 8px
  md: 16px
  lg: 24px
  xl: 32px
  2xl: 48px
  3xl: 64px
  container-max: 1280px
  gutter: 24px
---

## Brand & Style

The design system is built for a clear and data-focused user experience. The interface emphasizes usability, fast comprehension, and clean visual hierarchy for evaluating real estate figures and financial metrics.

The visual style is **Clean Modern**, utilizing structured cards, consistent spacing, and purposeful contrast. It keeps visual clutter to a minimum so users can focus on inputs, calculations, maps, and comparison charts.

## Colors

The color palette provides strong contrast and clear state indications:

- **Primary (#1E40AF):** Deep blue for primary actions, active navigation, and key headings.
- **Secondary (#0D9488):** Teal for positive growth indicators and secondary highlights.
- **Tertiary (#F59E0B):** Amber for warnings, notes, or high-value callouts.
- **Neutral:** Slate grays (`#0F172A` to `#F8FAFC`) for background canvas, borders, and body text.

Background surfaces remain clean and light (`#F8FAFC` to `#FFFFFF`) to maintain strong contrast for data tables and charts.

## Typography

The design system utilizes **Inter** as the primary typeface for its exceptional legibility and neutral, modern character. For specific data-heavy contexts, such as financial tables or coordinate mapping, **JetBrains Mono** is introduced to ensure tabular figures align perfectly and remain distinct from prose.

- **Headlines:** Use tight letter-spacing and semi-bold weights to convey authority.
- **Body:** Standardized on a 16px base for comfort, with 14px used for secondary metadata.
- **Data Labels:** Small-caps are used for section headers within panels to create a clear structural distinction without needing excessive font size increases.

## Layout & Spacing

The layout is built on a **12-column fluid grid** for desktop, transitioning to a **4-column grid** for mobile. A strict **4px baseline grid** governs all vertical rhythm.

- **Desktop (1280px+):** 24px gutters, 40px side margins.
- **Tablet (768px - 1279px):** 16px gutters, 24px side margins.
- **Mobile (Up to 767px):** 16px gutters, 16px side margins.

Content is organized into "Data Modules" (Cards). Related modules should be grouped with `24px` spacing, while internal element spacing within a module should stick to `16px` to maintain a tight, professional density.

## Elevation & Depth

This design system uses **Tonal Layers** combined with **Ambient Shadows** to define hierarchy. In an analytical context, depth should be functional, not decorative.

- **Level 0 (Background):** `#F8FAFC` — The canvas.
- **Level 1 (Cards/Surface):** `#FFFFFF` — Used for the primary content containers. Features a subtle `1px` stroke in `#E2E8F0` and a soft, diffused shadow (Y: 2px, Blur: 4px, Opacity: 4%).
- **Level 2 (Hover/Active):** An increased shadow (Y: 8px, Blur: 16px, Opacity: 8%) to indicate interactivity.
- **Level 3 (Modals/Popovers):** Highest elevation with a distinct backdrop blur (8px) on the underlying content to maintain focus on the data entry or detail view.

## Shapes

The shape language is **Softly Systematic**. 

- **Standard Elements (Buttons, Inputs, Cards):** `0.5rem` (8px) corner radius. This strikes the balance between the precision of a sharp corner and the approachability of a rounded one.
- **Large Containers:** `1rem` (16px) for major dashboard sections.
- **Status Pills:** Fully rounded (pill-shaped) to distinguish status indicators from clickable buttons.

Icons should follow a consistent `2px` stroke weight with slightly rounded terminals to match the UI's geometry.

## Components

- **Buttons:** Primary buttons are solid `#1E40AF` with white text. Secondary buttons use a `#1E40AF` stroke with a transparent background. All buttons have a height of `40px` (md) or `48px` (lg).
- **Input Fields:** Use a white background with a `#CBD5E1` border. On focus, the border shifts to the primary blue with a `2px` outer glow.
- **Data Cards:** Every card must have a consistent header area with a `body-sm` bold title and optional "Export" or "Filter" icon buttons.
- **Chips/Badges:** Use the secondary teal for "Positive Growth" indicators and a neutral gray for "Category" tags.
- **Data Tables:** Row heights are set to `52px`. Use alternating row highlights (Zebra striping) in `#F8FAFC` only when the table exceeds 10 rows.
- **Charts:** Utilize the secondary teal for primary data lines and the primary blue for comparison lines. Grid lines within charts must be highly subtle (`#F1F5F9`).