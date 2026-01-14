# Research: Course Attendance Registration

**Feature**: 001-course-attendance  
**Date**: 2026-01-13

## Technology Decisions

### Frontend Approach

**Decision**: Server-rendered HTML with Jinja2 templates and Tailwind CSS

**Rationale**:
- Aligns with constitution requirement for Python-based solutions
- Server-rendered HTML provides excellent accessibility out of the box
- Reduces JavaScript complexity, improving maintainability
- Progressive enhancement approach ensures functionality without JS
- Tailwind CSS provides utility-first styling with brand customisation

**Alternatives Considered**:
- React/Vue SPA: Rejected due to added complexity and accessibility challenges
- Pure static HTML: Rejected as dynamic data requires templating
- HTMX: Good alternative but adds learning curve; may adopt later for enhanced interactivity

### API Integration Strategy

**Decision**: Adapter pattern with interface abstraction for external API

**Rationale**:
- External API provides course, session, and attendee data
- Adapter pattern allows easy switching between real API and test data
- LOCAL_MODE environment variable toggles between adapters
- Same interface ensures consistent behaviour in both modes

**Alternatives Considered**:
- Direct API calls: Rejected as makes testing dependent on external service
- Mock server (LocalStack): Overkill for this use case; simple in-memory adapter sufficient

### Data Storage for Attendance Records

**Decision**: DynamoDB single-table design

**Rationale**:
- Attendance records are write-heavy (recording) with read patterns (viewing)
- DynamoDB provides serverless scaling and pay-per-use pricing
- Single-table design with composite keys enables efficient queries
- Encryption at rest by default satisfies GDPR requirements

**Alternatives Considered**:
- Aurora Serverless: More expensive for this use case; relational model unnecessary
- S3 with JSON files: Too slow for real-time updates; lacks query capability

### Pagination Strategy

**Decision**: Server-side pagination with 25 attendees per page

**Rationale**:
- 30-100 attendees per session requires pagination for usability
- 25 per page balances screen real estate with page load performance
- Server-side pagination reduces frontend complexity
- Simple previous/next navigation with page numbers

**Alternatives Considered**:
- Infinite scroll: Poor accessibility; harder to navigate
- Load all + client filter: Performance issues with 100 attendees
- Virtual scrolling: Over-engineered for this use case

### Local Development Approach

**Decision**: Flask development server with in-memory data stores

**Rationale**:
- Flask provides simple local HTTP server for Lambda handler testing
- In-memory dictionary can simulate DynamoDB for test data
- LOCAL_MODE=true bypasses AWS dependencies entirely
- Developers can run and test without AWS credentials

**Alternatives Considered**:
- Docker + LocalStack: Heavy setup; not needed for initial development
- SAM Local: Good option but requires Docker; may add later
- DynamoDB Local: Adds Java dependency; in-memory dict simpler initially

## Best Practices Applied

### Accessibility (WCAG 2.1 AA)

- Semantic HTML5 elements (nav, main, article, button)
- Visible focus states with 3:1 contrast ratio
- Form labels associated with inputs via `for` attribute
- Error messages linked to inputs via `aria-describedby`
- Skip-to-main-content link for keyboard users
- Status announcements via `aria-live` regions
- Colour not sole indicator of status (icons + text labels)

### Plain Language

- Button labels: "Mark as attended", "Mark as late", "Save"
- Status labels: "Here", "Not here", "Late"
- Error messages: "Please tell us why [name] was late"
- Empty states: "No sessions today. Check back tomorrow!"

### Security

- HTTPS only (API Gateway default)
- DynamoDB encryption at rest
- No PII beyond name in frontend; IDs in data attributes only
- CORS configured for known origins only
- Input validation on all form submissions
- XSS prevention via Jinja2 auto-escaping

### Performance

- Tailwind CSS purged for minimal bundle size
- Static assets served with cache headers
- Lambda cold start mitigation via provisioned concurrency (if needed)
- DynamoDB on-demand capacity for cost optimisation

## Open Questions Resolved

| Question | Resolution |
|----------|------------|
| How to handle external API failures? | Fall back to local test data with user notification |
| Session date range for "upcoming"? | Today + next 7 days by default |
| Attendance record immutability? | Past sessions are read-only; current sessions editable |
| Search implementation? | Client-side filter on loaded page (within pagination) |
