"""
Find Your Feet CIC - Course Attendance Registration
Course Session Model

DEPRECATED: Sessions are now part of Course model as session_dates.
This file is kept for backwards compatibility during migration.
"""

from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Optional


@dataclass
class CourseSession:
    """
    DEPRECATED: Use Course.session_dates instead.
    
    A specific scheduled instance of a course.
    """
    session_id: str
    course_id: str
    course_name: str
    instructor_name: str
    session_date: str  # ISO format: YYYY-MM-DD
    session_time: str  # Format: HH:MM
    is_past: bool = field(default=False)
    attendee_count: Optional[int] = None
    
    def __post_init__(self):
        """Compute is_past based on session_date."""
        if not self.is_past:
            try:
                session_date = datetime.strptime(self.session_date, '%Y-%m-%d').date()
                self.is_past = session_date < date.today()
            except ValueError:
                self.is_past = False
    
    @property
    def display_datetime(self) -> str:
        """Format session for display."""
        try:
            session_date = datetime.strptime(self.session_date, '%Y-%m-%d')
            formatted_date = session_date.strftime('%d %b %Y')
            
            time_parts = self.session_time.split(':')
            hour = int(time_parts[0])
            minute = time_parts[1] if len(time_parts) > 1 else '00'
            period = 'AM' if hour < 12 else 'PM'
            display_hour = hour if hour <= 12 else hour - 12
            if display_hour == 0:
                display_hour = 12
            formatted_time = f"{display_hour}:{minute} {period}"
            
            return f"{self.course_name} - {formatted_date}, {formatted_time}"
        except (ValueError, IndexError):
            return f"{self.course_name} - {self.session_date}, {self.session_time}"
    
    def to_dict(self) -> dict:
        return {
            'session_id': self.session_id,
            'course_id': self.course_id,
            'course_name': self.course_name,
            'instructor_name': self.instructor_name,
            'session_date': self.session_date,
            'session_time': self.session_time,
            'is_past': self.is_past,
            'attendee_count': self.attendee_count,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'CourseSession':
        return cls(
            session_id=data['session_id'],
            course_id=data.get('course_id', ''),
            course_name=data['course_name'],
            instructor_name=data['instructor_name'],
            session_date=data['session_date'],
            session_time=data['session_time'],
            is_past=data.get('is_past', False),
            attendee_count=data.get('attendee_count'),
        )
