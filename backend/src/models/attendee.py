"""
Find Your Feet CIC - Course Attendance Registration
Attendee Model

Updated: Attendees are linked to courses (not individual sessions)
Includes master attendee list for known attendees
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Person:
    """
    A known person in the system (master list).
    
    These are people who have attended courses before or are pre-registered.
    Used to populate attendee dropdowns.
    """
    person_id: str
    name: str
    email: Optional[str] = None
    
    def to_dict(self) -> dict:
        return {
            'person_id': self.person_id,
            'name': self.name,
            'email': self.email,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Person':
        return cls(
            person_id=data['person_id'],
            name=data['name'],
            email=data.get('email'),
        )


@dataclass
class Attendee:
    """
    A person registered for a course (all dates).
    
    Attendees are registered for the entire course, not individual sessions.
    Attendance is then tracked per date within the course.
    
    Attributes:
        attendee_id: Unique identifier (for integration, not displayed to users)
        person_id: Reference to the Person in master list
        name: Full name (denormalised for display)
        course_id: Reference to the course they're registered for
    """
    attendee_id: str
    person_id: str
    name: str
    course_id: str
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            'attendee_id': self.attendee_id,
            'person_id': self.person_id,
            'name': self.name,
            'course_id': self.course_id,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Attendee':
        """Create an Attendee from dictionary data."""
        return cls(
            attendee_id=data['attendee_id'],
            person_id=data.get('person_id', data['attendee_id']),
            name=data['name'],
            course_id=data.get('course_id', data.get('session_id', '')),
        )
