"""
Find Your Feet CIC - Course Attendance Registration
Unit Tests for Models
"""

import pytest
from datetime import date, timedelta

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.models import Course, SessionDate, Attendee, Person, AttendanceRecord, AttendanceStatus


class TestSessionDate:
    """Tests for SessionDate model."""
    
    def test_create_session_date(self):
        """SessionDate can be created with date and time."""
        sd = SessionDate(date='2026-01-15', time='10:00')
        assert sd.date == '2026-01-15'
        assert sd.time == '10:00'
    
    def test_session_date_is_past_future(self):
        """Future session date is not past."""
        future = (date.today() + timedelta(days=7)).isoformat()
        sd = SessionDate(date=future, time='10:00')
        assert sd.is_past is False
    
    def test_session_date_is_past_yesterday(self):
        """Yesterday's session date is past."""
        yesterday = (date.today() - timedelta(days=1)).isoformat()
        sd = SessionDate(date=yesterday, time='10:00')
        assert sd.is_past is True
    
    def test_session_date_display(self):
        """SessionDate formats display correctly."""
        sd = SessionDate(date='2026-01-15', time='10:00')
        assert 'Jan' in sd.display


class TestCourse:
    """Tests for Course model."""
    
    def test_create_course(self):
        """Course can be created with required fields."""
        course = Course(
            course_id='CRS001',
            name='First Aid Training',
            instructor_name='Sarah Johnson'
        )
        assert course.course_id == 'CRS001'
        assert course.name == 'First Aid Training'
    
    def test_course_with_multiple_dates(self):
        """Course can have multiple session dates."""
        course = Course(
            course_id='CRS001',
            name='First Aid Training',
            instructor_name='Sarah Johnson',
            session_dates=[
                SessionDate(date='2026-01-15', time='09:00'),
                SessionDate(date='2026-01-16', time='09:00'),
                SessionDate(date='2026-01-17', time='09:00'),
            ]
        )
        assert len(course.session_dates) == 3
        assert course.is_multi_day is True
    
    def test_course_single_day(self):
        """Single day course is not multi-day."""
        course = Course(
            course_id='CRS001',
            name='Fire Safety',
            instructor_name='Emily Williams',
            session_dates=[
                SessionDate(date='2026-01-15', time='14:00'),
            ]
        )
        assert course.is_multi_day is False
    
    def test_course_date_range_display(self):
        """Course displays date range correctly."""
        course = Course(
            course_id='CRS001',
            name='First Aid',
            instructor_name='Sarah',
            session_dates=[
                SessionDate(date='2026-01-15', time='09:00'),
                SessionDate(date='2026-01-17', time='09:00'),
            ]
        )
        assert '15' in course.date_range_display
        assert '17' in course.date_range_display


class TestPerson:
    """Tests for Person model (master list)."""
    
    def test_create_person(self):
        """Person can be created with required fields."""
        person = Person(
            person_id='PER001',
            name='Alice Thompson',
            email='alice@example.com'
        )
        assert person.person_id == 'PER001'
        assert person.name == 'Alice Thompson'
        assert person.email == 'alice@example.com'


class TestAttendee:
    """Tests for Attendee model."""
    
    def test_create_attendee(self):
        """Attendee can be created linked to course."""
        attendee = Attendee(
            attendee_id='ATT001',
            person_id='PER001',
            name='Alice Thompson',
            course_id='CRS001'
        )
        assert attendee.attendee_id == 'ATT001'
        assert attendee.course_id == 'CRS001'


class TestAttendanceRecord:
    """Tests for AttendanceRecord model."""
    
    def test_create_record(self):
        """AttendanceRecord can be created with required fields."""
        record = AttendanceRecord(
            course_id='CRS001',
            session_date='2026-01-15',
            attendee_id='ATT001',
            attendee_name='Alice Thompson'
        )
        assert record.course_id == 'CRS001'
        assert record.session_date == '2026-01-15'
        assert record.status == AttendanceStatus.UNMARKED
    
    def test_record_attended(self):
        """Record can be marked as attended."""
        record = AttendanceRecord(
            course_id='CRS001',
            session_date='2026-01-15',
            attendee_id='ATT001',
            attendee_name='Alice Thompson'
        )
        record.record(AttendanceStatus.ATTENDED)
        assert record.status == AttendanceStatus.ATTENDED
        assert record.recorded_at is not None
    
    def test_record_not_attended(self):
        """Record can be marked as not attended."""
        record = AttendanceRecord(
            course_id='CRS001',
            session_date='2026-01-15',
            attendee_id='ATT001',
            attendee_name='Alice Thompson'
        )
        record.record(AttendanceStatus.NOT_ATTENDED)
        assert record.status == AttendanceStatus.NOT_ATTENDED
    
    def test_record_late_with_time(self):
        """Record can be marked as late with arrival time."""
        record = AttendanceRecord(
            course_id='CRS001',
            session_date='2026-01-15',
            attendee_id='ATT001',
            attendee_name='Alice Thompson'
        )
        record.record(AttendanceStatus.LATE, '10:30', 'Bus delayed')
        assert record.status == AttendanceStatus.LATE
        assert record.late_arrival_time == '10:30'
        assert record.late_reason == 'Bus delayed'
    
    def test_record_late_without_time_fails(self):
        """Recording late without arrival time raises ValueError."""
        record = AttendanceRecord(
            course_id='CRS001',
            session_date='2026-01-15',
            attendee_id='ATT001',
            attendee_name='Alice Thompson'
        )
        with pytest.raises(ValueError):
            record.record(AttendanceStatus.LATE)
    
    def test_unmark_attendance(self):
        """Record can be unmarked."""
        record = AttendanceRecord(
            course_id='CRS001',
            session_date='2026-01-15',
            attendee_id='ATT001',
            attendee_name='Alice Thompson'
        )
        record.record(AttendanceStatus.ATTENDED)
        record.unmark()
        assert record.status == AttendanceStatus.UNMARKED
    
    def test_dynamodb_keys(self):
        """DynamoDB keys are generated correctly."""
        record = AttendanceRecord(
            course_id='CRS001',
            session_date='2026-01-15',
            attendee_id='ATT001',
            attendee_name='Alice Thompson'
        )
        assert record.pk == 'COURSE#CRS001#DATE#2026-01-15'
        assert record.sk == 'ATTENDEE#ATT001'
