"""
Find Your Feet CIC - Course Attendance Registration
Configuration Handler (LOCAL_MODE only)

Updated: Multi-day courses, master attendee list
"""

from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash

from src.config.settings import settings
from src.services.test_data import get_test_data_service
from src.services.attendance_repository import get_attendance_repository

bp = Blueprint('config', __name__, url_prefix='/config')


@bp.before_request
def check_local_mode():
    """Ensure configuration is only available in LOCAL_MODE."""
    if not settings.is_local_mode():
        return jsonify({'error': 'Configuration not available in production mode'}), 403


@bp.route('/test-data')
def test_data():
    """Display test data configuration screen."""
    test_data_service = get_test_data_service()
    config = test_data_service.get_config()
    
    return render_template(
        'config/test_data.html',
        people=config['people'],
        courses=config['courses'],
        attendees=config['attendees'],
        page_title='Test Data Configuration'
    )


@bp.route('/test-data/reset', methods=['POST'])
def reset_test_data():
    """Reset test data to defaults."""
    test_data_service = get_test_data_service()
    repository = get_attendance_repository()
    
    test_data_service.reset_to_defaults()
    repository.clear_all()
    
    flash('Test data has been reset to defaults.', 'success')
    return redirect(url_for('config.test_data'))


@bp.route('/api/test-data', methods=['GET'])
def get_test_data_api():
    """Get current test data configuration as JSON."""
    test_data_service = get_test_data_service()
    return jsonify(test_data_service.get_config())


@bp.route('/api/test-data', methods=['POST'])
def set_test_data_api():
    """Set test data configuration from JSON."""
    test_data_service = get_test_data_service()
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    if 'people' in data:
        test_data_service.set_people(data['people'])
    
    if 'courses' in data:
        test_data_service.set_courses(data['courses'])
    
    if 'attendees' in data:
        test_data_service.set_attendees(data['attendees'])
    
    return jsonify({
        'success': True,
        'config': test_data_service.get_config()
    })


@bp.route('/api/test-data', methods=['DELETE'])
def delete_test_data_api():
    """Reset test data to defaults via API."""
    test_data_service = get_test_data_service()
    repository = get_attendance_repository()
    
    test_data_service.reset_to_defaults()
    repository.clear_all()
    
    return jsonify({
        'success': True,
        'message': 'Test data reset to defaults'
    })


@bp.route('/api/people', methods=['GET'])
def get_people_api():
    """Get master list of people."""
    test_data_service = get_test_data_service()
    search = request.args.get('search', '')
    people = test_data_service.get_people(search if search else None)
    return jsonify({'people': [p.to_dict() for p in people]})


@bp.route('/api/people', methods=['POST'])
def add_person_api():
    """Add a new person to master list."""
    test_data_service = get_test_data_service()
    data = request.get_json()
    
    if not data or not data.get('name'):
        return jsonify({'error': 'Name is required'}), 400
    
    person = test_data_service.add_person(
        name=data['name'],
        email=data.get('email')
    )
    
    return jsonify({
        'success': True,
        'person': person.to_dict()
    })


@bp.route('/api/courses/<course_id>/attendees', methods=['POST'])
def add_attendee_to_course_api(course_id: str):
    """Add a person to a course as an attendee."""
    test_data_service = get_test_data_service()
    data = request.get_json()
    
    if not data or not data.get('person_id'):
        return jsonify({'error': 'Person ID is required'}), 400
    
    attendee = test_data_service.add_attendee_to_course(
        person_id=data['person_id'],
        course_id=course_id
    )
    
    if not attendee:
        return jsonify({'error': 'Person or course not found'}), 404
    
    return jsonify({
        'success': True,
        'attendee': attendee.to_dict()
    })


@bp.route('/api/attendees/<attendee_id>', methods=['DELETE'])
def remove_attendee_api(attendee_id: str):
    """Remove an attendee from a course."""
    test_data_service = get_test_data_service()
    
    if test_data_service.remove_attendee(attendee_id):
        return jsonify({'success': True})
    else:
        return jsonify({'error': 'Attendee not found'}), 404
