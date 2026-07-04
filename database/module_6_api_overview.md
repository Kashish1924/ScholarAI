# ScholarAI Module 6: Expanded REST APIs

## Why This Module Matters

Once the backend has data models and public pages, the next step is exposing a broader API surface. This makes the project easier to scale into richer frontend interactions, mobile clients, dashboards, and testing workflows.

## New API Areas

- `GET /api/v1/search`
- `GET /api/v1/filters`
- `GET /api/v1/comparison`
- `POST /api/v1/comparison`
- `GET /api/v1/trending`
- `GET /api/v1/deadlines`
- `GET /api/v1/news`
- `GET /api/v1/faqs`
- `GET /api/v1/notifications`
- `GET /api/v1/analytics`
- `GET /api/v1/taxonomy/categories`
- `GET /api/v1/taxonomy/states`

## Design Principles

- Keep response shapes consistent
- Reuse service-layer business logic instead of duplicating queries in routes
- Keep frontend-facing filter metadata available through dedicated endpoints
- Return only real database-backed scholarship content

## Security Notes

- Comparison endpoints validate incoming ids
- News, FAQ, and notification endpoints return read-only serialized content
- Search and filter endpoints still rely on backend query logic rather than client-side trust
- No AI is required for any of these endpoints

## Interview Talking Points

- Why separate content and analytics services: different query responsibilities should not be forced into one large class
- Why offer filter metadata endpoints: frontend dropdowns and clients should not hardcode taxonomy assumptions
- Why keep comparison read-only: comparison is derived from canonical scholarship data, not a separate mutable resource
