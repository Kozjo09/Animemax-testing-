# Palette's Journal - Critical Learnings

This journal tracks critical UX and accessibility (a11y) learnings specific to the AnimeMax codebase.

## 2026-07-22 - Global Modal Escape Key Dismissal & Screen Reader Dutch A11y
**Learning:** Modals and dynamic drawers (like 'details-modal' and 'confirm-modal') should always support intuitive dismissal via the standard keyboard 'Escape' key, with precedence given to higher-z-index elements first. Additionally, interactive and icon-only HTML elements (such as close icons, navigation, and header items) must feature descriptive Dutch-localized 'aria-label' attributes matching their hover tooltips to satisfy screen-reader accessibility.
**Action:** Always implement a top-level keyboard listener (outside `DOMContentLoaded` to prevent test-bypass conditions) for global keyboard navigation, and ensure both static and dynamically rendered icons or controls contain matching `aria-label` and `title` attributes in the user's primary locale.
