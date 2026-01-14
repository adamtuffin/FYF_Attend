# Implementation Plan: Course Attendance Registration

**Branch**: `001-course-attendance` | **Date**: 2026-01-13 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-course-attendance/spec.md`

## Summary

Build a course attendance registration application that allows administrators to view upcoming course sessions, select a session, and record attendance for each attendee (Attended, Not Attended, or Late with reason). The application will be an AWS serverless web application using Lambda, API Gateway, and DynamoDB, with a Tailwind CSS frontend. Data is primarily sourced from an external API, with a test configuration screen for local development.

## Technical Context

**Language/Version**: Python 3.11+  
**Primary Dependencies**: Flask (local dev), AWS Lambda, Jinja2, Tailwind CSS  
**Storage**: DynamoDB (attendance records), external API (courses, sessions, attendees)  
**Testing**: pytest with moto for AWS mocking, axe-core for accessibility  
**Target Platform**: AWS Lambda + API Gateway (web application)  
**Project Type**: Web application (serverless backend + static frontend)  
**Performance Goals**: < 3 second page load, < 5 second attendance recording  
**Constraints**: 30-100 attendees per session, WCAG 2.1 AA compliance, UK GDPR  
**Scale/Scope**: Single administrator at a time, development environment only initially

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Requirement | Status |
|-----------|-------------|--------|
| I. Accessibility First | WCAG 2.1 AA compliance planned? Keyboard navigation? Screen reader tested? | ✅ FR-013 requires accessibility; SC-006, SC-007 define measurable criteria |
| II. Plain Language | User-facing content at Year 5-6 reading level? Error messages clear? | ✅ FR-014 requires plain language; spec explicitly addresses this |
| III. Serverless & Well-Architected | AWS Lambda + API Gateway? DynamoDB/S3? CloudFormation? Well-Architected pillars reviewed? LOCAL_MODE switch for local development with substitutes (DynamoDB Local, local file storage)? | ✅ Using Lambda, API Gateway, DynamoDB; CloudFormation for IaC; LOCAL_MODE for test config |
| IV. Brand Consistency | Using brand colours (#F36F21, #D8D9D1, #333333)? Tailwind configured? Futura/Avenir fonts? | ✅ Will configure Tailwind with FYF brand colours and fonts |
| V. Data Protection | GDPR compliant? Only necessary data collected? Encryption in place? Secrets managed? | ✅ Only name displayed; IDs for integration; DynamoDB encryption at rest; no secrets in code |
| VI. Test-Driven Quality | Unit, integration, and accessibility tests planned? | ✅ pytest for unit/integration; axe-core/pa11y for accessibility |

## Project Structure

### Documentation (this feature)

```text
specs/001-course-attendance/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output (API contracts)
│   └── api.yaml         # OpenAPI specification
└── tasks.md             # Phase 2 output (/speckit.tasks command)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── handlers/           # Lambda function handlers
│   │   ├── sessions.py     # GET /sessions
│   │   ├── attendees.py    # GET /sessions/{id}/attendees
│   │   └── attendance.py   # POST/PUT /attendance
│   ├── models/
│   │   ├── course.py       # Course entity
│   │   ├── session.py      # CourseSession entity
│   │   ├── attendee.py     # Attendee entity
│   │   └── attendance.py   # AttendanceRecord entity
│   ├── services/
│   │   ├── session_service.py
│   │   ├── attendance_service.py
│   │   └── external_api.py # External API integration
│   └── config/
│       ├── settings.py     # Environment config with LOCAL_MODE
│       └── local_data.py   # Test data for local development
├── tests/
│   ├── unit/
│   ├── integration/
│   └── contract/
├── template.yaml           # CloudFormation SAM template
└── requirements.txt

frontend/
├── templates/
│   ├── base.html           # Base layout with brand styling
│   ├── sessions.html       # Session list page
│   ├── attendance.html     # Attendance recording page
│   └── config.html         # Test configuration page (local only)
├── static/
│   ├── css/
│   │   └── output.css      # Compiled Tailwind CSS
│   ├── js/
│   │   └── attendance.js   # Frontend interactivity
│   └── images/
│       └── LOGO.webp       # Brand logo
├── tailwind.config.js
└── package.json

tests/
├── accessibility/          # axe-core/pa11y tests
└── e2e/                    # End-to-end tests
```

**Structure Decision**: Web application structure with separate backend (Lambda handlers) and frontend (Jinja2 templates + Tailwind). Backend serves API endpoints; frontend is server-rendered HTML with progressive enhancement for fast accessibility compliance.

## Complexity Tracking

> No constitution violations requiring justification. All principles are satisfied by the design.
