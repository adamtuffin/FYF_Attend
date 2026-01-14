"""
Find Your Feet CIC - Course Attendance Registration
Courses Handler

Updated: Multi-day courses with register view
"""

from flask import Blueprint, render_template, abort

from src.config.settings import settings
from src.services.test_data import get_test_data_service
from src.services.attendance_repository import get_attendance_repository

bp = Blueprint('sessions', __name__, url_prefix='/sessions')


@bp.route('/')
def list_sessions():
    """
    Display list of upcoming courses.
    
    Shows courses with their date ranges.
    """
    test_data = get_test_data_service()
    courses = test_data.get_courses(include_past=False)
    
    return render_template(
        'sessions/list.html',
        courses=courses,
        page_title='Select a Course'
    )


@bp.route('/<course_id>')
def session_detail(course_id: str):
    """
    Display course register view with all dates.
    
    Shows grid: attendees (rows) × dates (columns)
    """
    test_data = get_test_data_service()
    repository = get_attendance_repository()
    
    course = test_data.get_course(course_id)
    if not course:
        abort(404)
    
    # Get attendees
    attendees, total = test_data.get_attendees(course_id)
    
    # Get session dates sorted
    session_dates = sorted(course.session_dates, key=lambda x: x.date)
    
    # Get attendance matrix
    attendee_ids = [a.attendee_id for a in attendees]
    date_strings = [sd.date for sd in session_dates]
    attendance_matrix = repository.get_attendance_matrix(course_id, date_strings, attendee_ids)
    
    # Check if any sessions are in the past
    has_past_sessions = any(sd.is_past for sd in session_dates)
    
    return render_template(
        'sessions/register.html',
        course=course,
        attendees=attendees,
        session_dates=session_dates,
        attendance_matrix=attendance_matrix,
        has_past_sessions=has_past_sessions,
        local_mode=settings.LOCAL_MODE,
        page_title=f'{course.name} - Register'
    )


@bp.route('/history')
def session_history():
    """
    Display list of past courses (read-only view).
    """
    test_data = get_test_data_service()
    courses = test_data.get_courses(include_past=True)
    past_courses = [c for c in courses if c.is_past]
    
    return render_template(
        'sessions/history.html',
        courses=past_courses,
        page_title='Course History'
    )
