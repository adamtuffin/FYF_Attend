"""
Find Your Feet CIC - Course Attendance Registration
Course Model

Updated: Multi-day course support with session dates
"""

from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Optional


@dataclass
class SessionDate:
    """A single session date within a multi-day course."""
    date: str  # ISO format: YYYY-MM-DD
    time: str  # Format: HH:MM
    
    @property
    def is_past(self) -> bool:
        """Check if this session date has passed."""
        try:
            session_date = datetime.strptime(self.date, '%Y-%m-%d').date()
            return session_date < date.today()
        except ValueError:
            return False
    
    @property
    def display(self) -> str:
        """Format for display (e.g., 'Mon 13 Jan')."""
        try:
            dt = datetime.strptime(self.date, '%Y-%m-%d')
            return dt.strftime('%a %d %b')
        except ValueError:
            return self.date
    
    def to_dict(self) -> dict:
        return {'date': self.date, 'time': self.time}
    
    @classmethod
    def from_dict(cls, data: dict) -> 'SessionDate':
        return cls(date=data['date'], time=data['time'])


@dataclass
class Course:
    """
    Represents a course offering that can span multiple days.
    
    Attributes:
        course_id: Unique identifier for the course
        name: Course name (e.g., "First Aid Training")
        instructor_name: Name of the instructor
        session_dates: List of dates when this course runs
    """
    course_id: str
    name: str
    instructor_name: str
    session_dates: list[SessionDate] = field(default_factory=list)
    
    @property
    def start_date(self) -> Optional[str]:
        """Get the first session date."""
        if self.session_dates:
            sorted_dates = sorted(self.session_dates, key=lambda x: x.date)
            return sorted_dates[0].date
        return None
    
    @property
    def end_date(self) -> Optional[str]:
        """Get the last session date."""
        if self.session_dates:
            sorted_dates = sorted(self.session_dates, key=lambda x: x.date)
            return sorted_dates[-1].date
        return None
    
    @property
    def is_multi_day(self) -> bool:
        """Check if course spans multiple days."""
        return len(self.session_dates) > 1
    
    @property
    def is_past(self) -> bool:
        """Check if all session dates have passed."""
        if not self.session_dates:
            return False
        return all(sd.is_past for sd in self.session_dates)
    
    @property
    def has_upcoming(self) -> bool:
        """Check if any session dates are upcoming."""
        return any(not sd.is_past for sd in self.session_dates)
    
    @property
    def date_range_display(self) -> str:
        """Display date range (e.g., '13-15 Jan 2026' or '13 Jan 2026')."""
        if not self.session_dates:
            return 'No dates'
        
        sorted_dates = sorted(self.session_dates, key=lambda x: x.date)
        first = datetime.strptime(sorted_dates[0].date, '%Y-%m-%d')
        
        if len(sorted_dates) == 1:
            return first.strftime('%d %b %Y')
        
        last = datetime.strptime(sorted_dates[-1].date, '%Y-%m-%d')
        if first.month == last.month and first.year == last.year:
            return f"{first.strftime('%d')}-{last.strftime('%d %b %Y')}"
        elif first.year == last.year:
            return f"{first.strftime('%d %b')} - {last.strftime('%d %b %Y')}"
        else:
            return f"{first.strftime('%d %b %Y')} - {last.strftime('%d %b %Y')}"
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            'course_id': self.course_id,
            'name': self.name,
            'instructor_name': self.instructor_name,
            'session_dates': [sd.to_dict() for sd in self.session_dates],
            'is_multi_day': self.is_multi_day,
            'is_past': self.is_past,
            'date_range': self.date_range_display,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Course':
        """Create a Course from dictionary data."""
        session_dates = []
        if 'session_dates' in data:
            session_dates = [SessionDate.from_dict(sd) for sd in data['session_dates']]
        
        return cls(
            course_id=data['course_id'],
            name=data['name'],
            instructor_name=data['instructor_name'],
            session_dates=session_dates,
        )
