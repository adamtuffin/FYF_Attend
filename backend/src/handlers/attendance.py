"""
Find Your Feet CIC - Course Attendance Registration
Attendance Handler

Updated: Multi-day courses with per-date attendance
"""

import logging
from datetime import datetime
from flask import Blueprint, request, jsonify, abort, session

from src.config.settings import settings
from src.services.test_data import get_test_data_service
from src.services.attendance_repository import get_attendance_repository
from src.models.attendance import AttendanceRecord, AttendanceStatus

logger = logging.getLogger(__name__)

bp = Blueprint('attendance', __name__, url_prefix='/api/attendance')

# Session key for tracking unlock state per course
UNLOCK_SESSION_KEY = 'unlocked_courses'


@bp.route('/courses/<course_id>/attendees')
def get_attendees(course_id: str):
    """
    Get attendees for a course with their attendance across all dates.
    """
    test_data = get_test_data_service()
    repository = get_attendance_repository()
    
    course = test_data.get_course(course_id)
    if not course:
        abort(404)
    
    # Parse query params
    search = request.args.get('search', '')
    
    # Get attendees
    attendees, total = test_data.get_attendees(
        course_id=course_id,
        search=search if search else None
    )
    
    # Get session dates
    session_dates = sorted(course.session_dates, key=lambda x: x.date)
    date_strings = [sd.date for sd in session_dates]
    
    # Get attendance matrix
    attendee_ids = [a.attendee_id for a in attendees]
    matrix = repository.get_attendance_matrix(course_id, date_strings, attendee_ids)
    
    # Build result
    result = []
    for attendee in attendees:
        att_data = {
            'attendee_id': attendee.attendee_id,
            'name': attendee.name,
            'attendance': {}
        }
        
        for dt in date_strings:
            record = matrix.get(attendee.attendee_id, {}).get(dt)
            if record:
                att_data['attendance'][dt] = {
                    'status': record.status.value,
                    'late_arrival_time': record.late_arrival_time,
                    'late_reason': record.late_reason,
                }
            else:
                att_data['attendance'][dt] = {'status': 'unmarked'}
        
        result.append(att_data)
    
    return jsonify({
        'course_id': course_id,
        'course_name': course.name,
        'dates': [{'date': sd.date, 'display': sd.display, 'is_past': sd.is_past} for sd in session_dates],
        'attendees': result,
        'total': total,
    })


@bp.route('/courses/<course_id>/attendance', methods=['POST'])
def record_attendance(course_id: str):
    """
    Record attendance for an attendee on a specific date.
    
    Toggle behavior: If clicking same status, unmark the attendance.
    """
    test_data = get_test_data_service()
    repository = get_attendance_repository()
    
    course = test_data.get_course(course_id)
    if not course:
        return jsonify({'error': 'Course not found'}), 404
    
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    attendee_id = data.get('attendee_id')
    session_date = data.get('session_date')
    status_str = data.get('status')
    late_arrival_time = data.get('late_arrival_time')
    late_reason = data.get('late_reason')
    
    if not attendee_id:
        return jsonify({'error': 'Attendee ID is required'}), 400
    
    if not session_date:
        return jsonify({'error': 'Session date is required'}), 400
    
    if not status_str:
        return jsonify({'error': 'Status is required'}), 400
    
    # Check if date is valid for this course
    valid_dates = [sd.date for sd in course.session_dates]
    if session_date not in valid_dates:
        return jsonify({'error': 'Invalid session date for this course'}), 400
    
    # Check if date is past (block editing unless unlocked)
    session_date_obj = next((sd for sd in course.session_dates if sd.date == session_date), None)
    if session_date_obj and session_date_obj.is_past:
        # Check if course is unlocked for editing
        unlocked_courses = session.get(UNLOCK_SESSION_KEY, {})
        if course_id not in unlocked_courses:
            return jsonify({'error': 'You cannot change attendance for past dates. Use "Unlock Past Days" first.'}), 400
    
    # Validate status
    try:
        status = AttendanceStatus(status_str)
    except ValueError:
        return jsonify({'error': 'Invalid status. Use: attended, late, not_attended, or unmarked'}), 400
    
    # Get attendee info
    attendee = test_data.get_attendee(attendee_id)
    if not attendee or attendee.course_id != course_id:
        return jsonify({'error': 'Attendee not found in this course'}), 404
    
    # Create or update attendance record
    record = repository.get(course_id, session_date, attendee_id)
    if not record:
        record = AttendanceRecord(
            course_id=course_id,
            session_date=session_date,
            attendee_id=attendee_id,
            attendee_name=attendee.name
        )
    
    # Toggle behavior: if clicking same status, unmark
    if record.status == status and status != AttendanceStatus.UNMARKED:
        record.unmark()
    elif status == AttendanceStatus.UNMARKED:
        record.unmark()
    else:
        # Record the attendance
        try:
            record.record(status, late_arrival_time, late_reason)
        except ValueError as e:
            return jsonify({'error': str(e)}), 400
    
    # Save
    repository.save(record)
    
    return jsonify({
        'success': True,
        'record': record.to_dict()
    })


@bp.route('/courses/<course_id>/summary')
def attendance_summary(course_id: str):
    """
    Get attendance summary for a course across all dates.
    """
    test_data = get_test_data_service()
    repository = get_attendance_repository()
    
    course = test_data.get_course(course_id)
    if not course:
        abort(404)
    
    # Get total expected attendees
    _, total_attendees = test_data.get_attendees(course_id)
    
    # Get summary per date
    summaries = []
    for sd in sorted(course.session_dates, key=lambda x: x.date):
        summary = repository.get_summary_by_date(course_id, sd.date)
        summary['date'] = sd.date
        summary['display'] = sd.display
        summary['is_past'] = sd.is_past
        summary['expected'] = total_attendees
        summary['unmarked'] = total_attendees - summary['total']
        
        if total_attendees > 0:
            summary['attendance_rate'] = round(
                ((summary['attended'] + summary['late']) / total_attendees) * 100, 1
            )
        else:
            summary['attendance_rate'] = 0
        
        summaries.append(summary)
    
    return jsonify({
        'course_id': course_id,
        'course_name': course.name,
        'total_attendees': total_attendees,
        'dates': summaries,
    })


@bp.route('/courses/<course_id>/unlock-past', methods=['POST'])
def unlock_past_days(course_id: str):
    """
    Unlock past days for editing.
    
    Requires notes explaining why editing is needed.
    Logs the action for audit purposes.
    """
    test_data = get_test_data_service()
    
    course = test_data.get_course(course_id)
    if not course:
        return jsonify({'error': 'Course not found'}), 404
    
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    notes = data.get('notes', '').strip()
    
    if not notes:
        return jsonify({'error': 'Please explain why you need to edit past attendance records.'}), 400
    
    if len(notes) < 10:
        return jsonify({'error': 'Please provide more detail about why you need to edit past records.'}), 400
    
    if len(notes) > 500:
        return jsonify({'error': 'Notes must be 500 characters or less.'}), 400
    
    # Log the unlock action for audit
    logger.info(
        'Past attendance unlocked',
        extra={
            'course_id': course_id,
            'course_name': course.name,
            'unlock_notes': notes,
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'ip_address': request.remote_addr,
            'user_agent': request.headers.get('User-Agent', 'Unknown'),
        }
    )
    
    # Store unlock state in session
    if UNLOCK_SESSION_KEY not in session:
        session[UNLOCK_SESSION_KEY] = {}
    
    session[UNLOCK_SESSION_KEY][course_id] = {
        'notes': notes,
        'unlocked_at': datetime.utcnow().isoformat() + 'Z',
    }
    session.modified = True
    
    return jsonify({
        'success': True,
        'message': 'Past days unlocked for editing.',
    })


@bp.route('/courses/<course_id>/lock-past', methods=['POST'])
def lock_past_days(course_id: str):
    """
    Lock past days again after editing.
    """
    # Remove unlock state from session
    if UNLOCK_SESSION_KEY in session and course_id in session[UNLOCK_SESSION_KEY]:
        del session[UNLOCK_SESSION_KEY][course_id]
        session.modified = True
    
    return jsonify({
        'success': True,
        'message': 'Past days locked.',
    })
