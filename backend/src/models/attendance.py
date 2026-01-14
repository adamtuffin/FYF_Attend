"""
Find Your Feet CIC - Course Attendance Registration
Attendance Record Model

Updated: Tracks attendance per course + date + attendee
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional


class AttendanceStatus(Enum):
    """Attendance status options."""
    ATTENDED = 'attended'
    LATE = 'late'
    NOT_ATTENDED = 'not_attended'
    UNMARKED = 'unmarked'  # Default state before recording


@dataclass
class AttendanceRecord:
    """
    Records attendance status for an attendee on a specific date of a course.
    
    Stored in DynamoDB with single-table design.
    
    Attributes:
        course_id: Reference to course
        session_date: The specific date (YYYY-MM-DD) within the course
        attendee_id: Reference to attendee
        attendee_name: Denormalised for display
        status: Attendance status (ATTENDED, LATE, NOT_ATTENDED)
        late_arrival_time: Time attendee arrived (HH:MM format, for LATE status)
        late_reason: Notes about lateness (optional, max 500 chars)
        recorded_at: ISO timestamp when status was recorded
        pk: DynamoDB partition key (COURSE#{course_id}#DATE#{session_date})
        sk: DynamoDB sort key (ATTENDEE#{attendee_id})
    """
    course_id: str
    session_date: str  # YYYY-MM-DD format
    attendee_id: str
    attendee_name: str
    status: AttendanceStatus = field(default=AttendanceStatus.UNMARKED)
    late_arrival_time: Optional[str] = None
    late_reason: Optional[str] = None
    recorded_at: Optional[str] = None
    
    @property
    def pk(self) -> str:
        """DynamoDB partition key."""
        return f"COURSE#{self.course_id}#DATE#{self.session_date}"
    
    @property
    def sk(self) -> str:
        """DynamoDB sort key."""
        return f"ATTENDEE#{self.attendee_id}"
    
    def record(
        self, 
        status: AttendanceStatus, 
        late_arrival_time: Optional[str] = None,
        late_reason: Optional[str] = None
    ) -> None:
        """
        Record or update attendance status.
        
        Args:
            status: The attendance status to record
            late_arrival_time: Time attendee arrived (HH:MM format, required if LATE)
            late_reason: Notes about lateness (optional, max 500 chars)
            
        Raises:
            ValueError: If status is LATE but no arrival time provided
            ValueError: If late_reason exceeds 500 characters
        """
        if status == AttendanceStatus.LATE:
            if not late_arrival_time or not late_arrival_time.strip():
                raise ValueError("Please tell us when the attendee arrived.")
            # Validate time format (HH:MM)
            time_parts = late_arrival_time.strip().split(':')
            if len(time_parts) != 2:
                raise ValueError("Please enter a valid time (e.g., 10:30).")
            try:
                hour = int(time_parts[0])
                minute = int(time_parts[1])
                if not (0 <= hour <= 23 and 0 <= minute <= 59):
                    raise ValueError("Please enter a valid time (e.g., 10:30).")
            except ValueError:
                raise ValueError("Please enter a valid time (e.g., 10:30).")
            
            self.late_arrival_time = late_arrival_time.strip()
            
            if late_reason and len(late_reason) > 500:
                raise ValueError("The notes are too long. Please keep them under 500 characters.")
            self.late_reason = late_reason.strip() if late_reason else None
        else:
            self.late_arrival_time = None
            self.late_reason = None
        
        self.status = status
        self.recorded_at = datetime.utcnow().isoformat() + 'Z'
    
    def unmark(self) -> None:
        """Reset attendance status to unmarked."""
        self.status = AttendanceStatus.UNMARKED
        self.late_arrival_time = None
        self.late_reason = None
        self.recorded_at = datetime.utcnow().isoformat() + 'Z'
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            'course_id': self.course_id,
            'session_date': self.session_date,
            'attendee_id': self.attendee_id,
            'attendee_name': self.attendee_name,
            'status': self.status.value,
            'late_arrival_time': self.late_arrival_time,
            'late_reason': self.late_reason,
            'recorded_at': self.recorded_at,
        }
    
    def to_dynamodb_item(self) -> dict:
        """Convert to DynamoDB item format."""
        item = {
            'pk': self.pk,
            'sk': self.sk,
            'course_id': self.course_id,
            'session_date': self.session_date,
            'attendee_id': self.attendee_id,
            'attendee_name': self.attendee_name,
            'status': self.status.value,
            'recorded_at': self.recorded_at,
        }
        if self.late_arrival_time:
            item['late_arrival_time'] = self.late_arrival_time
        if self.late_reason:
            item['late_reason'] = self.late_reason
        return item
    
    @classmethod
    def from_dict(cls, data: dict) -> 'AttendanceRecord':
        """Create an AttendanceRecord from dictionary data."""
        status_str = data.get('status', 'unmarked')
        try:
            status = AttendanceStatus(status_str)
        except ValueError:
            status = AttendanceStatus.UNMARKED
        
        return cls(
            course_id=data.get('course_id', data.get('session_id', '')),
            session_date=data.get('session_date', ''),
            attendee_id=data['attendee_id'],
            attendee_name=data.get('attendee_name', ''),
            status=status,
            late_arrival_time=data.get('late_arrival_time'),
            late_reason=data.get('late_reason'),
            recorded_at=data.get('recorded_at'),
        )
    
    @classmethod
    def from_dynamodb_item(cls, item: dict) -> 'AttendanceRecord':
        """Create an AttendanceRecord from DynamoDB item."""
        return cls.from_dict(item)
