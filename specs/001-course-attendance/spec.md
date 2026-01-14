# Feature Specification: Course Attendance Registration

**Feature Branch**: `001-course-attendance`  
**Created**: 2026-01-13  
**Status**: Draft  
**Input**: User description: "I want to create a registration application for courses so that I can track attendance. Attendee may attend or not, or possible attend late lateness should have a recorded reason, course name should be displayed including the instructor. The data will be populated by API but a basic configuration screen should be configurable for the purpose of testing."

## Clarifications

### Session 2026-01-13

- Q: How does the administrator select which course session to record attendance for? → A: List of upcoming sessions - Admin picks from sessions scheduled today or in the near future
- Q: What information should be shown for each attendee? → A: Name only displayed; ID exists in page data for integration but not shown to users
- Q: How many attendees would a typical course session have? → A: Large (30-100 attendees), requiring pagination or search functionality
- Q: Can administrators view or edit attendance records for past sessions? → A: View only - Can view past records but not edit them
- Q: What information should identify each session in the list? → A: Course name + date + time (e.g., "First Aid - 13 Jan 2026, 10:00 AM")

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Select Course Session (Priority: P1)

As a course administrator, I want to see a list of upcoming course sessions (today and near future) and select one to record attendance for, so that I can quickly find the relevant session.

**Why this priority**: This is the entry point to all attendance recording. Without session selection, no attendance can be recorded.

**Independent Test**: Can be tested by loading the application and verifying a list of upcoming sessions is displayed and selectable.

**Acceptance Scenarios**:

1. **Given** I open the attendance application, **When** the home screen loads, **Then** I see a list of course sessions scheduled for today and upcoming days
2. **Given** I see the list of upcoming sessions, **When** I select a session, **Then** I am taken to the attendance recording screen for that session
3. **Given** there are no upcoming sessions, **When** I view the home screen, **Then** I see a clear message indicating no sessions are scheduled

---

### User Story 2 - Record Attendee Attendance (Priority: P1)

As a course administrator, I want to record whether each attendee has attended, not attended, or arrived late to a course session, so that I have an accurate record of participation.

**Why this priority**: This is the core purpose of the application. Without the ability to record attendance, the system provides no value.

**Independent Test**: Can be fully tested by opening a course session and marking attendees as present, absent, or late. Delivers immediate value by creating an attendance record.

**Acceptance Scenarios**:

1. **Given** a course session with registered attendees is displayed, **When** I mark an attendee as "Attended", **Then** their status is saved and shown as attended with a visual indicator
2. **Given** a course session with registered attendees is displayed, **When** I mark an attendee as "Not Attended", **Then** their status is saved and shown as absent with a visual indicator
3. **Given** a course session with registered attendees is displayed, **When** I mark an attendee as "Late", **Then** I am prompted to enter a reason and both the status and reason are saved
4. **Given** I have marked an attendee as "Late", **When** I try to save without entering a reason, **Then** the system prompts me to provide a reason before saving

---

### User Story 3 - View Course Information (Priority: P2)

As a course administrator, I want to see the course name and instructor clearly displayed when recording attendance, so that I am confident I am recording attendance for the correct session.

**Why this priority**: Essential context for accurate attendance recording. Without this, administrators could accidentally record attendance for the wrong course.

**Independent Test**: Can be tested by loading any course session and verifying the course name and instructor are prominently displayed.

**Acceptance Scenarios**:

1. **Given** a course session is loaded, **When** the attendance screen is displayed, **Then** the course name is shown prominently at the top
2. **Given** a course session is loaded, **When** the attendance screen is displayed, **Then** the instructor name is clearly visible
3. **Given** a course with a long name, **When** the attendance screen is displayed, **Then** the full course name is readable (not truncated in a confusing way)

---

### User Story 4 - Configure Test Data (Priority: P3)

As a developer or tester, I want to access a configuration screen where I can set up test course and attendee data, so that I can verify the application works correctly without needing live API data.

**Why this priority**: Enables testing and development without requiring the external API. Important for quality assurance but not needed for end-user functionality.

**Independent Test**: Can be tested by opening the configuration screen, adding test courses and attendees, then verifying they appear in the main attendance view.

**Acceptance Scenarios**:

1. **Given** I am in test mode, **When** I access the configuration screen, **Then** I can add a new course with name and instructor
2. **Given** I have created a test course, **When** I add attendees to the course, **Then** they appear in the attendee list for that course
3. **Given** I have configured test data, **When** I switch to the attendance view, **Then** I can see and use the test courses and attendees
4. **Given** I have test data configured, **When** I want to reset, **Then** I can clear all test data and start fresh

---

### User Story 5 - View Attendance Summary (Priority: P4)

As a course administrator, I want to see a summary of attendance for a course session, so that I can quickly understand overall participation levels.

**Why this priority**: Provides valuable insights but is not essential for the core attendance recording function.

**Independent Test**: Can be tested by recording attendance for several attendees and verifying the summary counts match.

**Acceptance Scenarios**:

1. **Given** a course session with recorded attendance, **When** I view the session, **Then** I see counts of attended, not attended, and late attendees
2. **Given** a course session with mixed attendance, **When** I view the summary, **Then** the numbers accurately reflect the recorded statuses

---

### Edge Cases

- What happens when the API is unavailable? System should fall back to local test data mode with a clear notification
- What happens when an attendee's status is changed after initial recording? The new status should replace the old one, and for "Late" status, a new reason can be entered
- What happens when a course has no registered attendees? Display an empty state with a clear message
- What happens when the late reason is very long? Allow reasonable text length (up to 500 characters) with visible character count
- What happens when searching/filtering attendees? Search should match on attendee name; filter should allow showing only unmarked attendees
- What happens when viewing a past session? Display attendance records as read-only with clear visual indication that editing is disabled

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST display a list of upcoming course sessions showing course name, date, and time for each session
- **FR-002**: System MUST display a list of registered attendees showing their name only (attendee ID available in page data for integration but not displayed)
- **FR-015**: System MUST support sessions with 30-100 attendees using pagination or search/filter to manage the list
- **FR-016**: System MUST allow viewing past session attendance records (read-only)
- **FR-017**: System MUST prevent editing of attendance records for past sessions
- **FR-003**: System MUST allow marking each attendee with one of three statuses: Attended, Not Attended, or Late
- **FR-004**: System MUST require a reason to be entered when marking an attendee as Late
- **FR-005**: System MUST display the course name prominently on the attendance screen
- **FR-006**: System MUST display the instructor name on the attendance screen
- **FR-007**: System MUST persist attendance records so they are not lost on page refresh
- **FR-008**: System MUST provide a configuration screen for entering test course and attendee data
- **FR-009**: System MUST support receiving course and attendee data from an external API
- **FR-010**: System MUST display attendance summary counts (attended, not attended, late)
- **FR-011**: System MUST allow changing an attendee's status after initial recording
- **FR-012**: System MUST visually distinguish between the three attendance statuses
- **FR-013**: System MUST be accessible and usable by people with disabilities (per constitution requirements)
- **FR-014**: System MUST use plain language throughout the interface

### Key Entities

- **Course**: Represents a course offering with a name, instructor, and scheduled sessions. A course has many registered attendees.
- **Attendee**: A person registered for a course. Has a name (displayed to users) and a unique ID (for API integration, not displayed). Can be registered for multiple courses.
- **Attendance Record**: Captures a single attendee's attendance for a specific course session. Includes status (Attended/Not Attended/Late) and optional late reason.
- **Course Session**: A specific instance of a course with a scheduled date and time (e.g., "First Aid - 13 Jan 2026, 10:00 AM"). Attendance is recorded per session.

## Assumptions

- Attendees are pre-registered for courses (registration is handled elsewhere or via the test configuration)
- One administrator records attendance at a time (no concurrent editing conflicts to handle initially)
- Late reasons are free-text (not predefined categories)
- The external API will provide course, session, instructor, and attendee data in a compatible format
- Test configuration is only available in development/testing mode, not in production

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Administrators can record attendance status for an attendee in under 5 seconds
- **SC-002**: 95% of users can successfully record attendance for all attendees without assistance on first use
- **SC-003**: Course name and instructor are visible without scrolling when the attendance screen loads
- **SC-004**: Test data configuration takes less than 2 minutes to set up a course with 10 attendees
- **SC-005**: Attendance records persist correctly across browser sessions (no data loss)
- **SC-006**: All attendance statuses are distinguishable by colour and icon/text for accessibility
- **SC-007**: The application meets WCAG 2.1 Level AA accessibility standards
