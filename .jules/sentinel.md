# Sentinel's Journal - Critical Security Learnings

## 2026-07-20 - [DOM-Based XSS in Dynamic Settings Rendering]
**Vulnerability:** Persistent dynamic database fields like `app.user` (retrieved from the `anime_users` table in Supabase) were directly interpolated inside template literals and written to `innerHTML`. A user registering or modifying their username to a script payload could achieve persistent Stored / DOM-based XSS when navigating to the settings profile page.
**Learning:** Even when using highly secure backend systems like Supabase, relying solely on client-side state mapping (`app.user`) to directly build raw HTML payloads via `main.innerHTML` exposes the frontend to complete token hijack and context manipulation if the input wasn't sanitised in the UI.
**Prevention:** Always employ a custom HTML escaping utility function (`escapeHTML`) on any user-controlled dynamic variable before embedding them inside elements rendered via `innerHTML` template strings.
