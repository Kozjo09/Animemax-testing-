# Sentinel's Journal - Critical Security Learnings

## 2026-07-20 - [DOM-Based XSS in Dynamic Settings Rendering]
**Vulnerability:** Persistent dynamic database fields like `app.user` (retrieved from the `anime_users` table in Supabase) were directly interpolated inside template literals and written to `innerHTML`. A user registering or modifying their username to a script payload could achieve persistent Stored / DOM-based XSS when navigating to the settings profile page.
**Learning:** Even when using highly secure backend systems like Supabase, relying solely on client-side state mapping (`app.user`) to directly build raw HTML payloads via `main.innerHTML` exposes the frontend to complete token hijack and context manipulation if the input wasn't sanitised in the UI.
**Prevention:** Always employ a custom HTML escaping utility function (`escapeHTML`) on any user-controlled dynamic variable before embedding them inside elements rendered via `innerHTML` template strings.

## 2026-07-21 - [DOM-Based XSS in Global Toast Notification System]
**Vulnerability:** The global toast notification system (`window.showToast`) used direct string interpolation to render dynamic messages into `innerHTML`, rendering the application vulnerable to DOM-based XSS whenever an unsanitized error message (such as database error details, AniList API payloads, or username inputs) was passed to the notification system.
**Learning:** Utilities that display text notifications across the UI must strictly segregate safe markup (like font-awesome icons) from the dynamic message payloads. Passing full payloads directly to `innerHTML` introduces application-wide XSS surface area.
**Prevention:** Restructure global notification elements to assign the dynamic payload safely using `textContent` inside an inner wrapper element (e.g. a `span`), preserving formatting styles without risking raw script or HTML injection.

## 2026-07-22 - [DOM-Based XSS in Third-Party API Descriptions]
**Vulnerability:** The application retrieved anime description fields directly from the AniList GraphQL API or the local caches and injected them using `.innerHTML` on both the details modal (`detail-desc`) and the hero card (`hero-desc`). If a description was maliciously injected or modified upstream to contain bad markup/scripts, a complete client-side takeover could happen when users loaded details or the home feed.
**Learning:** Rendering third-party rich-text API descriptions using raw `innerHTML` creates immediate XSS vectors. Utilizing basic string prefix-matching blocklists (e.g., matching `javascript:`) is easily bypassed with control/whitespace characters inside hrefs.
**Prevention:** Construct a lightweight browser-native DOM-based sanitizer using `DOMParser`. Strip out all unauthorized elements and attributes, and strictly validate hyperlink protocols to only allow a secure list (e.g., `http://`, `https://`, `/`, `#`) via a robust regex pattern instead of naive string comparisons.
