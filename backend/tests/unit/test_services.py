"""
Find Your Feet CIC - Course Attendance Registration
Unit Tests for Services
"""

import pytest
from datetime import date

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.services.test_data import TestDataService
from src.services.attendance_repository import AttendanceRepository
from src.models.attendance import AttendanceRecord, AttendanceStatus


class TestTestDataServicePeople:
    """Tests for TestDataService - People management."""
    
    def test_default_people_loaded(self):
        """Default people are loaded on initialization."""
        service = TestDataService()
        people = service.get_people()
        assert len(people) > 0
    
    def test_get_people_with_search(self):
        """get_people filters by search term."""
        service = TestDataService()
        people = service.get_people(search='alice')
        assert len(people) >= 1
        assert all('alice' in p.name.lower() for p in people)
    
    def test_add_person(self):
        """add_person adds to master list."""
        service = TestDataService()
        initial_count = len(service.get_people())
        person = service.add_person('New Person', 'new@example.com')
        assert person.name == 'New Person'
        assert len(service.get_people()) == initial_count + 1


class TestTestDataServiceCourses:
    """Tests for TestDataService - Course management."""
    
    def test_default_courses_loaded(self):
        """Default courses are loaded on initialization."""
        service = TestDataService()
        courses = service.get_courses(include_past=True)
        assert len(courses) > 0
    
    def test_get_courses_excludes_past(self):
        """get_courses excludes past courses by default."""
        service = TestDataService()
        courses = service.get_courses(include_past=False)
        for course in courses:
            assert course.has_upcoming
    
    def test_get_course_by_id(self):
        """get_course returns course by ID."""
        service = TestDataService()
        course = service.get_course('CRS001')
        assert course is not None
        assert course.course_id == 'CRS001'
    
    def test_courses_have_session_dates(self):
        """Courses have session dates."""
        service = TestDataService()
        course = service.get_course('CRS001')
        assert len(course.session_dates) > 0


class TestTestDataServiceAttendees:
    """Tests for TestDataService - Attendee management."""
    
    def test_get_attendees_for_course(self):
        """get_attendees returns attendees for a course."""
        service = TestDataService()
        attendees, total = service.get_attendees('CRS001')
        assert len(attendees) > 0
        assert total > 0
        for att in attendees:
            assert att.course_id == 'CRS001'
    
    def test_get_attendees_with_search(self):
        """get_attendees filters by search."""
        service = TestDataService()
        attendees, total = service.get_attendees('CRS001', search='alice')
        for att in attendees:
            assert 'alice' in att.name.lower()
    
    def test_add_attendee_to_course(self):
        """add_attendee_to_course registers person for course."""
        service = TestDataService()
        # Get a person not already in course
        people = service.get_people()
        attendees, _ = service.get_attendees('CRS003')
        existing_person_ids = {a.person_id for a in attendees}
        
        new_person = None
        for p in people:
            if p.person_id not in existing_person_ids:
                new_person = p
                break
        
        if new_person:
            attendee = service.add_attendee_to_course(new_person.person_id, 'CRS003')
            assert attendee is not None
            assert attendee.course_id == 'CRS003'


class TestAttendanceRepository:
    """Tests for AttendanceRepository (LOCAL_MODE)."""
    
    def test_save_and_get(self):
        """Record can be saved and retrieved."""
        repo = AttendanceRepository()
        repo.clear_all()
        
        record = AttendanceRecord(
            course_id='CRS001',
            session_date='2026-01-15',
            attendee_id='ATT001',
            attendee_name='Alice Thompson'
        )
        record.record(AttendanceStatus.ATTENDED)
        
        repo.save(record)
        retrieved = repo.get('CRS001', '2026-01-15', 'ATT001')
        
        assert retrieved is not None
        assert retrieved.status == AttendanceStatus.ATTENDED
    
    def test_get_not_found(self):
        """get returns None for unknown record."""
        repo = AttendanceRepository()
        repo.clear_all()
        result = repo.get('UNKNOWN', '2026-01-01', 'UNKNOWN')
        assert result is None
    
    def test_get_by_course_date(self):
        """get_by_course_date returns records for specific date."""
        repo = AttendanceRepository()
        repo.clear_all()
        
        # Save records for same course, different dates
        for i in range(3):
            record = AttendanceRecord(
                course_id='CRS001',
                session_date='2026-01-15',
                attendee_id=f'ATT00{i+1}',
                attendee_name=f'Attendee {i+1}'
            )
            record.record(AttendanceStatus.ATTENDED)
            repo.save(record)
        
        # Save for different date
        other = AttendanceRecord(
            course_id='CRS001',
            session_date='2026-01-16',
            attendee_id='ATT010',
            attendee_name='Other'
        )
        other.record(AttendanceStatus.ATTENDED)
        repo.save(other)
        
        records = repo.get_by_course_date('CRS001', '2026-01-15')
        assert len(records) == 3
    
    def test_get_by_course(self):
        """get_by_course returns all records for a course."""
        repo = AttendanceRepository()
        repo.clear_all()
        
        # Save records for multiple dates
        for dt in ['2026-01-15', '2026-01-16']:
            record = AttendanceRecord(
                course_id='CRS001',
                session_date=dt,
                attendee_id='ATT001',
                attendee_name='Alice'
            )
            record.record(AttendanceStatus.ATTENDED)
            repo.save(record)
        
        records = repo.get_by_course('CRS001')
        assert len(records) == 2
    
    def test_attendance_matrix(self):
        """get_attendance_matrix returns proper matrix."""
        repo = AttendanceRepository()
        repo.clear_all()
        
        # Save some records
        record = AttendanceRecord(
            course_id='CRS001',
            session_date='2026-01-15',
            attendee_id='ATT001',
            attendee_name='Alice'
        )
        record.record(AttendanceStatus.ATTENDED)
        repo.save(record)
        
        matrix = repo.get_attendance_matrix(
            'CRS001',
            ['2026-01-15', '2026-01-16'],
            ['ATT001', 'ATT002']
        )
        
        assert 'ATT001' in matrix
        assert 'ATT002' in matrix
        assert matrix['ATT001']['2026-01-15'] is not None
        assert matrix['ATT001']['2026-01-16'] is None
    
    def test_get_summary_by_date(self):
        """get_summary_by_date returns correct counts."""
        repo = AttendanceRepository()
        repo.clear_all()
        
        statuses = [
            AttendanceStatus.ATTENDED,
            AttendanceStatus.ATTENDED,
            AttendanceStatus.NOT_ATTENDED,
            AttendanceStatus.LATE,
        ]
        
        for i, status in enumerate(statuses):
            record = AttendanceRecord(
                course_id='CRS001',
                session_date='2026-01-15',
                attendee_id=f'ATT00{i+1}',
                attendee_name=f'Attendee {i+1}'
            )
            if status == AttendanceStatus.LATE:
                record.record(status, '10:30', 'Bus late')
            else:
                record.record(status)
            repo.save(record)
        
        summary = repo.get_summary_by_date('CRS001', '2026-01-15')
        
        assert summary['total'] == 4
        assert summary['attended'] == 2
        assert summary['not_attended'] == 1
        assert summary['late'] == 1
