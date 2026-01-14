# Tasks: Course Attendance Registration

**Input**: Design documents from `/specs/001-course-attendance/`  
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, contracts/ ✅

**Tests**: Tests included as constitution requires test-driven quality (Principle VI).

**Organization**: Tasks are grouped by user story to enable independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3, US4, US5)
- Include exact file paths in descriptions

## Path Conventions

- **Backend**: `backend/src/` for Python handlers, models, services
- **Frontend**: `frontend/templates/` for Jinja2, `frontend/static/` for CSS/JS
- **Tests**: `backend/tests/` for unit/integration, `tests/` for accessibility/e2e

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Create project directory structure per implementation plan in backend/, frontend/, tests/
- [x] T002 [P] Initialize Python project with requirements.txt in backend/requirements.txt
- [x] T003 [P] Initialize Node.js project for Tailwind in frontend/package.json
- [x] T004 [P] Create .gitignore with Python, Node, .env patterns in .gitignore
- [x] T005 [P] Create .env.example with LOCAL_MODE and configuration variables in .env.example
- [x] T006 [P] Configure Tailwind with FYF brand colours (#F36F21, #D8D9D1, #333333) and fonts (Futura, Avenir) in frontend/tailwind.config.js
- [x] T007 Copy LOGO.webp to frontend/static/images/LOGO.webp

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T008 Create settings module with LOCAL_MODE toggle and environment config in backend/src/config/settings.py
- [x] T009 [P] Create Course model (course_id, name, instructor_name) in backend/src/models/course.py
- [x] T010 [P] Create CourseSession model (session_id, course_name, instructor_name, session_date, session_time, is_past) in backend/src/models/session.py
- [x] T011 [P] Create Attendee model (attendee_id, name, session_id) in backend/src/models/attendee.py
- [x] T012 [P] Create AttendanceRecord model with DynamoDB keys (pk, sk, status, late_reason, recorded_at) in backend/src/models/attendance.py
- [x] T013 Create DynamoDB attendance repository with LOCAL_MODE in-memory fallback in backend/src/services/attendance_repository.py
- [x] T014 Create test data service with LOCAL_MODE sample data in backend/src/services/test_data.py
- [x] T015 Create Flask app entry point with route registration in backend/app.py
- [x] T016 [P] Create base HTML template with FYF branding, skip-to-content link, and accessibility features in frontend/templates/base.html
- [x] T017 [P] Build initial Tailwind CSS output in frontend/static/css/output.css
- [x] T018 Create CloudFormation template for DynamoDB table FYFAttendance in backend/template.yaml

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Select Course Session (Priority: P1) 🎯 MVP

**Goal**: Display list of upcoming sessions and allow selection to navigate to attendance recording

**Independent Test**: Load application, verify session list displays with course name + date + time, click session to navigate

### Tests for User Story 1

- [x] T020 [P] [US1] Unit test for test_data_service.get_sessions() in backend/tests/unit/test_services.py
- [ ] T021 [P] [US1] Integration test for GET /sessions endpoint in backend/tests/integration/test_sessions_api.py

### Implementation for User Story 1

- [x] T022 [US1] Implement TestDataService.get_sessions() (today + 7 days) in backend/src/services/test_data.py
- [x] T023 [US1] Implement GET /sessions handler returning session list in backend/src/handlers/sessions.py
- [x] T024 [US1] Create sessions list template with course name, date, time display in frontend/templates/sessions/list.html
- [x] T025 [US1] Add session card component with clickable navigation to attendance page in frontend/templates/sessions/list.html
- [x] T026 [US1] Add empty state message "No sessions scheduled" when list is empty in frontend/templates/sessions/list.html
- [x] T027 [US1] Register /sessions route in Flask app in backend/app.py
- [x] T028 [US1] Add keyboard navigation and focus states to session cards in frontend/templates/sessions/list.html

**Checkpoint**: User can view upcoming sessions and click to navigate (attendance page not yet functional)

---

## Phase 4: User Story 2 - Record Attendee Attendance (Priority: P1) 🎯 MVP

**Goal**: Display attendee list for a session with pagination, allow marking Attended/Not Attended/Late with reason

**Independent Test**: Navigate to session, see attendee list, mark attendees with each status, verify persistence

### Tests for User Story 2

- [x] T029 [P] [US2] Unit test for attendance_repository.save() in backend/tests/unit/test_services.py
- [x] T030 [P] [US2] Unit test for test_data_service.get_attendees() with pagination in backend/tests/unit/test_services.py
- [ ] T031 [P] [US2] Integration test for POST /api/attendance/sessions/{id}/attendance endpoint in backend/tests/integration/test_attendance_api.py
- [ ] T032 [P] [US2] Integration test for GET /api/attendance/sessions/{id}/attendees endpoint in backend/tests/integration/test_attendees_api.py

### Implementation for User Story 2

- [x] T033 [US2] Implement TestDataService.get_attendees() with pagination (25 per page) in backend/src/services/test_data.py
- [x] T034 [US2] Implement AttendanceRepository.save() with status validation in backend/src/services/attendance_repository.py
- [x] T035 [US2] Implement late_reason validation (required for LATE, max 500 chars) in backend/src/models/attendance.py
- [x] T036 [US2] Implement GET /api/attendance/sessions/{id}/attendees handler with pagination params in backend/src/handlers/attendance.py
- [x] T037 [US2] Implement POST /api/attendance/sessions/{id}/attendance handler in backend/src/handlers/attendance.py
- [x] T038 [US2] Create attendance page template with attendee list in frontend/templates/sessions/detail.html
- [x] T039 [US2] Add attendance status buttons (Attended, Not Attended, Late) with visual distinction in frontend/templates/sessions/detail.html
- [x] T040 [US2] Add late reason modal/form with character counter (max 500) in frontend/templates/sessions/detail.html
- [x] T041 [US2] Add pagination controls (Previous, Next, page numbers) in frontend/templates/sessions/detail.html
- [x] T042 [US2] Create attendance.js for status button clicks and late reason submission in frontend/static/js/attendance.js
- [x] T043 [US2] Add search/filter input for attendee name filtering in frontend/templates/sessions/detail.html
- [x] T044 [US2] Implement read-only mode for past sessions (is_past=true) in frontend/templates/sessions/detail.html
- [x] T045 [US2] Add ARIA live region for status update announcements in frontend/templates/sessions/detail.html
- [x] T046 [US2] Register /api/attendance routes in Flask app in backend/app.py

**Checkpoint**: Core MVP complete - user can select session and record attendance

---

## Phase 5: User Story 3 - View Course Information (Priority: P2)

**Goal**: Display course name and instructor prominently on attendance screen

**Independent Test**: Navigate to any session, verify course name at top, instructor name visible without scrolling

### Implementation for User Story 3

- [x] T047 [US3] Implement GET /sessions/{id} handler for session details in backend/src/handlers/sessions.py
- [x] T048 [US3] Add course header section with prominent course name (h1) in frontend/templates/sessions/detail.html
- [x] T049 [US3] Add instructor name display below course name in frontend/templates/sessions/detail.html
- [x] T050 [US3] Ensure course name handles long text without truncation in frontend/templates/sessions/detail.html
- [x] T051 [US3] Add breadcrumb navigation (Sessions > Course Name) in frontend/templates/sessions/detail.html

**Checkpoint**: Attendance page shows clear course context

---

## Phase 6: User Story 4 - Configure Test Data (Priority: P3)

**Goal**: Provide configuration screen to add test courses, sessions, and attendees (LOCAL_MODE only)

**Independent Test**: Access /config, add course with instructor, add session, add attendees, verify in main view

### Tests for User Story 4

- [x] T052 [P] [US4] Unit test for test data CRUD operations in backend/tests/unit/test_services.py
- [ ] T053 [P] [US4] Integration test for /config/test-data endpoints in backend/tests/integration/test_config_api.py

### Implementation for User Story 4

- [x] T054 [US4] Implement GET /config/test-data handler in backend/src/handlers/config.py
- [x] T055 [US4] Implement POST /config/api/test-data handler in backend/src/handlers/config.py
- [x] T056 [US4] Implement DELETE /config/api/test-data handler in backend/src/handlers/config.py
- [x] T057 [US4] Add LOCAL_MODE guard to config endpoints (403 if not LOCAL_MODE) in backend/src/handlers/config.py
- [x] T058 [US4] Create config page template displaying courses, sessions, attendees in frontend/templates/config/test_data.html
- [ ] T059 [US4] Add course form (name, instructor) with add/remove functionality in frontend/templates/config/test_data.html
- [ ] T060 [US4] Add session form (course, date, time) with add/remove functionality in frontend/templates/config/test_data.html
- [ ] T061 [US4] Add attendee form (name, session) with add/remove functionality in frontend/templates/config/test_data.html
- [x] T062 [US4] Add "Reset to Defaults" button with confirmation in frontend/templates/config/test_data.html
- [x] T063 [US4] Register /config routes in Flask app in backend/app.py
- [x] T064 [US4] Add config link in navigation (only visible in LOCAL_MODE) in frontend/templates/base.html

**Checkpoint**: Developers can configure test data without external API

---

## Phase 7: User Story 5 - View Attendance Summary (Priority: P4)

**Goal**: Display summary counts of attendance statuses on the attendance page

**Independent Test**: Record various attendance statuses, verify summary shows correct counts for attended/not attended/late

### Implementation for User Story 5

- [x] T065 [US5] Add summary calculation in AttendanceRepository.get_summary() in backend/src/services/attendance_repository.py
- [x] T066 [US5] Add GET /api/attendance/sessions/{id}/summary endpoint in backend/src/handlers/attendance.py
- [x] T067 [US5] Add summary display component (attended: X, not here: X, late: X) in frontend/templates/sessions/detail.html
- [x] T068 [US5] Update summary display dynamically when attendance is recorded in frontend/static/js/attendance.js
- [x] T069 [US5] Style summary with colour-coded badges matching status colours in frontend/templates/sessions/detail.html

**Checkpoint**: All user stories complete

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T070 [P] Add accessibility tests using axe-core/pa11y in tests/accessibility/test_wcag.py
- [ ] T071 [P] Add error handling middleware with plain language messages in backend/src/app.py
- [ ] T072 [P] Add structured JSON logging to all handlers in backend/src/config/logging.py
- [ ] T073 Verify all colour contrast meets WCAG 2.1 AA (4.5:1 text, 3:1 large) in frontend/static/css/output.css
- [ ] T074 Run pa11y against all pages and fix any issues
- [ ] T075 Add loading states for async operations in frontend/static/js/attendance.js
- [ ] T076 [P] Add API error fallback to test data mode with user notification in backend/src/services/external_api.py
- [ ] T077 Validate quickstart.md instructions work end-to-end
- [ ] T078 Final review of plain language in all UI text

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-7)**: All depend on Foundational phase completion
  - US1 + US2 form the MVP and should be completed first
  - US3 enhances the attendance page (depends on US2 template)
  - US4 is independent (test configuration)
  - US5 enhances the attendance page (depends on US2)
- **Polish (Phase 8)**: Depends on all user stories being complete

### User Story Dependencies

- **US1 (P1)**: Can start after Foundational - No dependencies on other stories
- **US2 (P1)**: Can start after Foundational - Shares attendance.html with US1 navigation target
- **US3 (P2)**: Depends on US2 (enhances attendance.html)
- **US4 (P3)**: Can start after Foundational - Independent of other stories
- **US5 (P4)**: Depends on US2 (enhances attendance.html)

### Within Each User Story

- Tests MUST be written and FAIL before implementation
- Models before services
- Services before handlers
- Handlers before templates
- Core implementation before enhancements

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational model tasks (T009-T012) can run in parallel
- Once Foundational completes:
  - US1 and US4 can run in parallel (different pages)
  - US2 depends on US1 navigation target
  - US3 and US5 depend on US2 attendance page

---

## Parallel Example: Phase 2 Foundational

```bash
# Launch all model tasks together:
Task T009: "Create Course model in backend/src/models/course.py"
Task T010: "Create CourseSession model in backend/src/models/session.py"
Task T011: "Create Attendee model in backend/src/models/attendee.py"
Task T012: "Create AttendanceRecord model in backend/src/models/attendance.py"
```

---

## Implementation Strategy

### MVP First (User Stories 1 + 2)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 (Session Selection)
4. Complete Phase 4: User Story 2 (Record Attendance)
5. **STOP and VALIDATE**: Test MVP independently
6. Demo: Admin can select session and record attendance

### Incremental Delivery

1. Setup + Foundational → Foundation ready
2. Add US1 + US2 → MVP! Can record attendance
3. Add US3 → Course info visible
4. Add US4 → Test configuration available
5. Add US5 → Summary counts shown
6. Polish → Accessibility verified, errors handled

### Suggested MVP Scope

**Minimum Viable Product = Phase 1 + Phase 2 + Phase 3 + Phase 4**

This delivers:
- Session list with upcoming courses
- Attendee list with pagination
- Attendance recording (Attended, Not Attended, Late with reason)
- Persistence to DynamoDB (or in-memory in LOCAL_MODE)

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify tests fail before implementing
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- All UI text must use plain language (Year 5-6 reading level)
- All interactive elements must be keyboard accessible
