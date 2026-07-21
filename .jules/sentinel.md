# Sentinel's Journal - Critical Security Learnings

## 2026-07-20 - [DOM-Based XSS in Dynamic Settings Rendering]
**Vulnerability:** Persistent dynamic database fields like `app.user` (retrieved from the `anime_users` table in Supabase) were directly interpolated inside template literals and written to `innerHTML`. A user registering or modifying their username to a script payload could achieve persistent Stored / DOM-based XSS when navigating to the settings profile page.
**Learning:** Even when using highly secure backend systems like Supabase, relying solely on client-side state mapping (`app.user`) to directly build raw HTML payloads via `main.innerHTML` exposes the frontend to complete token hijack and context manipulation if the input wasn't sanitised in the UI.
**Prevention:** Always employ a custom HTML escaping utility function (`escapeHTML`) on any user-controlled dynamic variable before embedding them inside elements rendered via `innerHTML` template strings.

## 2026-07-21 - [DOM-Based XSS in Global Toast Notification System]
**Vulnerability:** The global toast notification system (`window.showToast`) used direct string interpolation to render dynamic messages into `innerHTML`, rendering the application vulnerable to DOM-based XSS whenever an unsanitized error message (such as database error details, AniList API payloads, or username inputs) was passed to the notification system.
**Learning:** Utilities that display text notifications across the UI must strictly segregate safe markup (like font-awesome icons) from the dynamic message payloads. Passing full payloads directly to `innerHTML` introduces application-wide XSS surface area.
**Prevention:** Restructure global notification elements to assign the dynamic payload safely using `textContent` inside an inner wrapper element (e.g. a `span`), preserving formatting styles without risking raw script or HTML injection.
