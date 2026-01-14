"""
Find Your Feet CIC - Course Attendance Registration
Test Data Service

Updated: Multi-day courses, master attendee list, course-based attendance
"""

from datetime import date, timedelta
from typing import Optional

from src.models import Course, SessionDate, Attendee, Person


class TestDataService:
    """
    Provides sample test data when running in LOCAL_MODE.
    
    Supports:
    - Master list of known people
    - Multi-day courses with session dates
    - Attendees registered to courses (not individual sessions)
    """
    
    def __init__(self):
        """Initialize with default test data."""
        self._people: list[Person] = []
        self._courses: list[Course] = []
        self._attendees: list[Attendee] = []
        self._load_default_data()
    
    def _load_default_data(self):
        """Load default test data."""
        # Master list of known people
        self._people = [
            Person(person_id='PER001', name='Alice Thompson', email='alice@example.com'),
            Person(person_id='PER002', name='Bob Williams', email='bob@example.com'),
            Person(person_id='PER003', name='Charlie Brown', email='charlie@example.com'),
            Person(person_id='PER004', name='Diana Ross', email='diana@example.com'),
            Person(person_id='PER005', name='Edward Norton', email='edward@example.com'),
            Person(person_id='PER006', name='Fiona Green', email='fiona@example.com'),
            Person(person_id='PER007', name='George Harris', email='george@example.com'),
            Person(person_id='PER008', name='Hannah White', email='hannah@example.com'),
            Person(person_id='PER009', name='Ian Black', email='ian@example.com'),
            Person(person_id='PER010', name='Julia Roberts', email='julia@example.com'),
            Person(person_id='PER011', name='Kevin Smith', email='kevin@example.com'),
            Person(person_id='PER012', name='Laura Wilson', email='laura@example.com'),
            Person(person_id='PER013', name='Mark Taylor', email='mark@example.com'),
            Person(person_id='PER014', name='Nancy Drew', email='nancy@example.com'),
            Person(person_id='PER015', name='Oscar Martinez', email='oscar@example.com'),
            Person(person_id='PER016', name='Patricia Clark', email='patricia@example.com'),
            Person(person_id='PER017', name='Quentin Blake', email='quentin@example.com'),
            Person(person_id='PER018', name='Rachel Adams', email='rachel@example.com'),
            Person(person_id='PER019', name='Steven King', email='steven@example.com'),
            Person(person_id='PER020', name='Tina Turner', email='tina@example.com'),
        ]
        
        today = date.today()
        
        # Multi-day courses
        self._courses = [
            # 3-day First Aid course starting today
            Course(
                course_id='CRS001',
                name='First Aid Training',
                instructor_name='Sarah Johnson',
                session_dates=[
                    SessionDate(date=today.isoformat(), time='09:00'),
                    SessionDate(date=(today + timedelta(days=1)).isoformat(), time='09:00'),
                    SessionDate(date=(today + timedelta(days=2)).isoformat(), time='09:00'),
                ]
            ),
            # 2-day Health & Safety course next week
            Course(
                course_id='CRS002',
                name='Health and Safety Basics',
                instructor_name='Michael Chen',
                session_dates=[
                    SessionDate(date=(today + timedelta(days=7)).isoformat(), time='10:00'),
                    SessionDate(date=(today + timedelta(days=8)).isoformat(), time='10:00'),
                ]
            ),
            # Single-day Fire Safety course
            Course(
                course_id='CRS003',
                name='Fire Safety Awareness',
                instructor_name='Emily Williams',
                session_dates=[
                    SessionDate(date=(today + timedelta(days=3)).isoformat(), time='14:00'),
                ]
            ),
            # Past course (already completed)
            Course(
                course_id='CRS004',
                name='Manual Handling',
                instructor_name='David Brown',
                session_dates=[
                    SessionDate(date=(today - timedelta(days=3)).isoformat(), time='09:00'),
                    SessionDate(date=(today - timedelta(days=2)).isoformat(), time='09:00'),
                ]
            ),
        ]
        
        # Attendees registered to courses (using people from master list)
        self._attendees = []
        
        # Register first 12 people to First Aid course
        for i, person in enumerate(self._people[:12]):
            self._attendees.append(Attendee(
                attendee_id=f"ATT001{i+1:03d}",
                person_id=person.person_id,
                name=person.name,
                course_id='CRS001'
            ))
        
        # Register people 5-15 to Health & Safety course
        for i, person in enumerate(self._people[4:15]):
            self._attendees.append(Attendee(
                attendee_id=f"ATT002{i+1:03d}",
                person_id=person.person_id,
                name=person.name,
                course_id='CRS002'
            ))
        
        # Register people 10-18 to Fire Safety course
        for i, person in enumerate(self._people[9:18]):
            self._attendees.append(Attendee(
                attendee_id=f"ATT003{i+1:03d}",
                person_id=person.person_id,
                name=person.name,
                course_id='CRS003'
            ))
        
        # Register people 1-8 to past Manual Handling course
        for i, person in enumerate(self._people[:8]):
            self._attendees.append(Attendee(
                attendee_id=f"ATT004{i+1:03d}",
                person_id=person.person_id,
                name=person.name,
                course_id='CRS004'
            ))
    
    # ========== PEOPLE (Master List) ==========
    
    def get_people(self, search: Optional[str] = None) -> list[Person]:
        """Get all known people, optionally filtered by search."""
        if search:
            search_lower = search.lower()
            return [p for p in self._people if search_lower in p.name.lower()]
        return self._people.copy()
    
    def get_person(self, person_id: str) -> Optional[Person]:
        """Get a person by ID."""
        for person in self._people:
            if person.person_id == person_id:
                return person
        return None
    
    def add_person(self, name: str, email: Optional[str] = None) -> Person:
        """Add a new person to the master list."""
        person_id = f"PER{len(self._people) + 1:03d}"
        person = Person(person_id=person_id, name=name, email=email)
        self._people.append(person)
        return person
    
    def set_people(self, people: list[dict]) -> None:
        """Set people from configuration data."""
        self._people = [Person.from_dict(p) for p in people]
    
    # ========== COURSES ==========
    
    def get_courses(self, include_past: bool = False) -> list[Course]:
        """Get courses, optionally including past courses."""
        if include_past:
            return self._courses.copy()
        return [c for c in self._courses if c.has_upcoming]
    
    def get_course(self, course_id: str) -> Optional[Course]:
        """Get a specific course by ID."""
        for course in self._courses:
            if course.course_id == course_id:
                return course
        return None
    
    def set_courses(self, courses: list[dict]) -> None:
        """Set courses from configuration data."""
        self._courses = [Course.from_dict(c) for c in courses]
    
    # ========== ATTENDEES ==========
    
    def get_attendees(
        self,
        course_id: str,
        search: Optional[str] = None,
        page: int = 1,
        page_size: int = 100
    ) -> tuple[list[Attendee], int]:
        """
        Get attendees for a course with optional pagination and search.
        
        Returns:
            Tuple of (attendees, total_count)
        """
        # Filter by course
        attendees = [a for a in self._attendees if a.course_id == course_id]
        
        # Filter by search term
        if search:
            search_lower = search.lower()
            attendees = [a for a in attendees if search_lower in a.name.lower()]
        
        # Sort by name
        attendees = sorted(attendees, key=lambda a: a.name)
        
        total_count = len(attendees)
        
        # Paginate
        start = (page - 1) * page_size
        end = start + page_size
        paginated = attendees[start:end]
        
        return paginated, total_count
    
    def get_attendee(self, attendee_id: str) -> Optional[Attendee]:
        """Get a specific attendee by ID."""
        for attendee in self._attendees:
            if attendee.attendee_id == attendee_id:
                return attendee
        return None
    
    def add_attendee_to_course(self, person_id: str, course_id: str) -> Optional[Attendee]:
        """Add a person to a course as an attendee."""
        person = self.get_person(person_id)
        course = self.get_course(course_id)
        
        if not person or not course:
            return None
        
        # Check if already registered
        for att in self._attendees:
            if att.person_id == person_id and att.course_id == course_id:
                return att  # Already registered
        
        attendee_id = f"ATT{course_id[-3:]}{len(self._attendees) + 1:03d}"
        attendee = Attendee(
            attendee_id=attendee_id,
            person_id=person_id,
            name=person.name,
            course_id=course_id
        )
        self._attendees.append(attendee)
        return attendee
    
    def remove_attendee(self, attendee_id: str) -> bool:
        """Remove an attendee from a course."""
        for i, att in enumerate(self._attendees):
            if att.attendee_id == attendee_id:
                self._attendees.pop(i)
                return True
        return False
    
    def set_attendees(self, attendees: list[dict]) -> None:
        """Set attendees from configuration data."""
        self._attendees = [Attendee.from_dict(a) for a in attendees]
    
    # ========== UTILITY ==========
    
    def reset_to_defaults(self) -> None:
        """Reset to default test data."""
        self._load_default_data()
    
    def get_config(self) -> dict:
        """Get current test data configuration."""
        return {
            'people': [p.to_dict() for p in self._people],
            'courses': [c.to_dict() for c in self._courses],
            'attendees': [a.to_dict() for a in self._attendees],
        }


# Singleton instance
_test_data_service: Optional[TestDataService] = None


def get_test_data_service() -> TestDataService:
    """Get the singleton test data service instance."""
    global _test_data_service
    if _test_data_service is None:
        _test_data_service = TestDataService()
    return _test_data_service
