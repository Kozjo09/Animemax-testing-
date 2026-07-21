# Bolt's Journal - Critical Learnings

This journal tracks critical performance optimization learnings specific to the AnimeMax codebase.

## 2025-07-21 - Client-side GraphQL Cache for Navigation
**Learning:** Frequent SPA view/tab switching triggers repeated high-weight network requests (such as GraphQL queries fetching trending/popular content) which degrades user experience and results in redundant network overhead on the client. Native browser caches do not reliably cache dynamic POST queries or complex GraphQL fetches on internal routing.
**Action:** Always implement lightweight in-memory caches (such as `homeFeedCache` or `detailsCache`) inside the SPA state layer for stable and static homepage elements, enabling sub-millisecond route-rehydration while keeping code modifications within the single-file constraint.
