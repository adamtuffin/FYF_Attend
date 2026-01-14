# Data Model: Course Attendance Registration

**Feature**: 001-course-attendance  
**Date**: 2026-01-13

## Entities

### Course

Represents a course offering. Sourced from external API.

| Attribute | Type | Description | Source |
|-----------|------|-------------|--------|
| course_id | string | Unique identifier | External API |
| name | string | Course name (e.g., "First Aid Training") | External API |
| instructor_name | string | Name of the instructor | External API |

**Notes**:
- Read-only; not stored locally
- Retrieved via external API or test configuration

### CourseSession

A specific scheduled instance of a course. Sourced from external API.

| Attribute | Type | Description | Source |
|-----------|------|-------------|--------|
| session_id | string | Unique identifier | External API |
| course_id | string | Reference to parent course | External API |
| course_name | string | Denormalised for display | External API |
| instructor_name | string | Denormalised for display | External API |
| session_date | date (ISO 8601) | Date of session (YYYY-MM-DD) | External API |
| session_time | time (HH:MM) | Start time of session | External API |
| is_past | boolean | Computed: session_date < today | Derived |

**Notes**:
- Read-only; not stored locally
- `is_past` computed at query time for read-only determination

### Attendee

A person registered for a course session. Sourced from external API.

| Attribute | Type | Description | Source |
|-----------|------|-------------|--------|
| attendee_id | string | Unique identifier (not displayed) | External API |
| name | string | Full name (displayed to users) | External API |
| session_id | string | Reference to course session | External API |

**Notes**:
- Read-only; not stored locally
- Only `name` displayed in UI; `attendee_id` used for API integration

### AttendanceRecord

Records attendance status for an attendee at a session. Stored in DynamoDB.

| Attribute | Type | Description | Constraints |
|-----------|------|-------------|-------------|
| pk | string | Partition key: `SESSION#{session_id}` | Required |
| sk | string | Sort key: `ATTENDEE#{attendee_id}` | Required |
| session_id | string | Reference to course session | Required |
| attendee_id | string | Reference to attendee | Required |
| attendee_name | string | Denormalised for display | Required |
| status | enum | ATTENDED, NOT_ATTENDED, LATE | Required |
| late_reason | string | Reason for lateness (max 500 chars) | Required if status=LATE |
| recorded_at | datetime (ISO 8601) | When status was recorded | Auto-set |
| recorded_by | string | ID of admin who recorded | Future use |

**Notes**:
- Primary storage in DynamoDB
- Single-table design with composite key
- `recorded_at` updated on each status change
- `late_reason` required only when status is LATE

## DynamoDB Table Design

### Table: FYFAttendance

**Partition Key (pk)**: String - `SESSION#{session_id}`  
**Sort Key (sk)**: String - `ATTENDEE#{attendee_id}`

#### Access Patterns

| Pattern | Key Condition | Use Case |
|---------|---------------|----------|
| Get all attendance for session | pk = `SESSION#{id}` | Loading attendance page |
| Get single attendee record | pk = `SESSION#{id}`, sk = `ATTENDEE#{id}` | Updating attendance |
| Query by session date | GSI on session_date | Finding past sessions (future) |

#### Example Item

```json
{
  "pk": "SESSION#sess-2026-01-13-001",
  "sk": "ATTENDEE#att-12345",
  "session_id": "sess-2026-01-13-001",
  "attendee_id": "att-12345",
  "attendee_name": "Jane Smith",
  "status": "LATE",
  "late_reason": "Bus was delayed",
  "recorded_at": "2026-01-13T10:15:00Z"
}
```

## State Transitions

### AttendanceRecord Status

```
[No Record] → ATTENDED
[No Record] → NOT_ATTENDED
[No Record] → LATE (requires late_reason)

ATTENDED → NOT_ATTENDED
ATTENDED → LATE (requires late_reason)

NOT_ATTENDED → ATTENDED
NOT_ATTENDED → LATE (requires late_reason)

LATE → ATTENDED (clears late_reason)
LATE → NOT_ATTENDED (clears late_reason)
LATE → LATE (can update late_reason)
```

**Constraints**:
- Status changes blocked for past sessions (session_date < today)
- late_reason required before saving LATE status
- late_reason max length: 500 characters

## Validation Rules

| Entity | Field | Rule |
|--------|-------|------|
| AttendanceRecord | status | Must be one of: ATTENDED, NOT_ATTENDED, LATE |
| AttendanceRecord | late_reason | Required if status=LATE; max 500 chars |
| AttendanceRecord | session_id | Must reference valid session |
| AttendanceRecord | attendee_id | Must reference valid attendee for session |

## Test Data Structure

For LOCAL_MODE, test data follows the same structure:

```python
TEST_COURSES = [
    {"course_id": "test-001", "name": "First Aid Basics", "instructor_name": "Dr. Smith"}
]

TEST_SESSIONS = [
    {
        "session_id": "test-sess-001",
        "course_id": "test-001",
        "course_name": "First Aid Basics",
        "instructor_name": "Dr. Smith",
        "session_date": "2026-01-13",
        "session_time": "10:00"
    }
]

TEST_ATTENDEES = [
    {"attendee_id": "test-att-001", "name": "Jane Doe", "session_id": "test-sess-001"},
    {"attendee_id": "test-att-002", "name": "John Smith", "session_id": "test-sess-001"}
]
```
