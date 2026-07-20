# Palette's Journal - Critical UX & Accessibility Learnings

## 2026-07-20 - [Escape Key Modal Dismissal & Accessible Buttons]
**Learning:** High-fidelity web applications with custom full-screen slide-up drawer details modals and confirmation overlays need intuitive keyboard support. Power-users and screen-reader users expect the `Escape` key to instantly dismiss modals. Standard title tooltips do not replace `aria-label` attributes on icon-only interactive controls.
**Action:** Always bind a global keydown handler for `Escape` to close active UI overlays in single-page HTML apps, and attach `aria-label` to custom close or navigation buttons.
