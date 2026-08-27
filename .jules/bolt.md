# Bolt's Journal - Critical Learnings

This journal tracks critical performance optimization learnings specific to the AnimeMax codebase.

## 2025-07-21 - Client-side GraphQL Cache for Navigation
**Learning:** Frequent SPA view/tab switching triggers repeated high-weight network requests (such as GraphQL queries fetching trending/popular content) which degrades user experience and results in redundant network overhead on the client. Native browser caches do not reliably cache dynamic POST queries or complex GraphQL fetches on internal routing.
**Action:** Always implement lightweight in-memory caches (such as `homeFeedCache` or `detailsCache`) inside the SPA state layer for stable and static homepage elements, enabling sub-millisecond route-rehydration while keeping code modifications within the single-file constraint.

## 2025-08-27 - Non-blocking UI rendering for streaming sources & network timeouts
**Learning:** External stream provider endpoints (e.g. `ANIVEXA_BASE/episodes`) can hang or delay for extended periods (5+ minutes) when third-party servers degrade or rate-limit. Waiting on `await loadAllProviders()` before displaying static server embeds (`MEGAPLAY`, `FILM U`, `VIDLINK`, `VIDNEST`, `ANIMEPAHE`, `SUPAPLAY`) or initializing player streams blocks the entire player UI and prevents video playback on working servers.
**Action:** Always render static server buttons immediately in the UI synchronously before initiating asynchronous provider queries. Use explicit `AbortController` timeouts (e.g. 4s for provider list, 6s for stream links) on `fetchWithCorsFallback` calls so stalled third-party API requests fail gracefully to fallbacks without hanging the video player experience.
