"""
Find Your Feet CIC - Course Attendance Registration
Attendance Repository

Updated: Tracks attendance per course + date + attendee
"""

from typing import Optional
import boto3
from botocore.exceptions import ClientError

from src.config.settings import settings
from src.models.attendance import AttendanceRecord, AttendanceStatus


class AttendanceRepository:
    """
    Repository for storing and retrieving attendance records.
    
    Uses DynamoDB in production/staging, in-memory storage in LOCAL_MODE.
    
    Key structure:
    - pk: COURSE#{course_id}#DATE#{session_date}
    - sk: ATTENDEE#{attendee_id}
    """
    
    def __init__(self):
        """Initialize repository based on LOCAL_MODE setting."""
        self._local_store: dict[str, AttendanceRecord] = {}
        self._dynamodb_table = None
        
        if not settings.is_local_mode():
            self._init_dynamodb()
    
    def _init_dynamodb(self):
        """Initialize DynamoDB connection."""
        config = settings.get_dynamodb_config()
        dynamodb = boto3.resource('dynamodb', **config)
        self._dynamodb_table = dynamodb.Table(settings.DYNAMODB_TABLE_NAME)
    
    def _get_key(self, course_id: str, session_date: str, attendee_id: str) -> str:
        """Generate a key for local storage."""
        return f"COURSE#{course_id}#DATE#{session_date}|ATTENDEE#{attendee_id}"
    
    def save(self, record: AttendanceRecord) -> AttendanceRecord:
        """Save an attendance record."""
        if settings.is_local_mode():
            key = self._get_key(record.course_id, record.session_date, record.attendee_id)
            self._local_store[key] = record
            return record
        
        # DynamoDB save
        item = record.to_dynamodb_item()
        self._dynamodb_table.put_item(Item=item)
        return record
    
    def get(self, course_id: str, session_date: str, attendee_id: str) -> Optional[AttendanceRecord]:
        """Get an attendance record by course, date, and attendee."""
        if settings.is_local_mode():
            key = self._get_key(course_id, session_date, attendee_id)
            return self._local_store.get(key)
        
        # DynamoDB get
        try:
            response = self._dynamodb_table.get_item(
                Key={
                    'pk': f"COURSE#{course_id}#DATE#{session_date}",
                    'sk': f"ATTENDEE#{attendee_id}"
                }
            )
            item = response.get('Item')
            if item:
                return AttendanceRecord.from_dynamodb_item(item)
            return None
        except ClientError:
            return None
    
    def get_by_course_date(self, course_id: str, session_date: str) -> list[AttendanceRecord]:
        """Get all attendance records for a specific course date."""
        if settings.is_local_mode():
            prefix = f"COURSE#{course_id}#DATE#{session_date}|"
            return [
                record for key, record in self._local_store.items()
                if key.startswith(prefix)
            ]
        
        # DynamoDB query
        try:
            response = self._dynamodb_table.query(
                KeyConditionExpression='pk = :pk',
                ExpressionAttributeValues={
                    ':pk': f"COURSE#{course_id}#DATE#{session_date}"
                }
            )
            items = response.get('Items', [])
            return [AttendanceRecord.from_dynamodb_item(item) for item in items]
        except ClientError:
            return []
    
    def get_by_course(self, course_id: str) -> list[AttendanceRecord]:
        """Get all attendance records for a course (all dates)."""
        if settings.is_local_mode():
            prefix = f"COURSE#{course_id}#DATE#"
            return [
                record for key, record in self._local_store.items()
                if key.startswith(prefix)
            ]
        
        # DynamoDB scan with filter (not efficient, but works)
        try:
            response = self._dynamodb_table.scan(
                FilterExpression='course_id = :cid',
                ExpressionAttributeValues={':cid': course_id}
            )
            items = response.get('Items', [])
            return [AttendanceRecord.from_dynamodb_item(item) for item in items]
        except ClientError:
            return []
    
    def get_attendance_matrix(self, course_id: str, session_dates: list[str], attendee_ids: list[str]) -> dict:
        """
        Get attendance as a matrix for the register view.
        
        Returns:
            Dict mapping attendee_id -> date -> AttendanceRecord
        """
        all_records = self.get_by_course(course_id)
        
        # Build matrix
        matrix = {}
        for att_id in attendee_ids:
            matrix[att_id] = {}
            for dt in session_dates:
                matrix[att_id][dt] = None
        
        # Fill in records
        for record in all_records:
            if record.attendee_id in matrix and record.session_date in matrix[record.attendee_id]:
                matrix[record.attendee_id][record.session_date] = record
        
        return matrix
    
    def get_summary_by_date(self, course_id: str, session_date: str) -> dict:
        """Get attendance summary for a specific course date."""
        records = self.get_by_course_date(course_id, session_date)
        
        summary = {
            'total': len(records),
            'attended': 0,
            'late': 0,
            'not_attended': 0,
            'unmarked': 0,
        }
        
        for record in records:
            if record.status == AttendanceStatus.ATTENDED:
                summary['attended'] += 1
            elif record.status == AttendanceStatus.LATE:
                summary['late'] += 1
            elif record.status == AttendanceStatus.NOT_ATTENDED:
                summary['not_attended'] += 1
            else:
                summary['unmarked'] += 1
        
        return summary
    
    def clear_course(self, course_id: str) -> int:
        """Clear all attendance records for a course."""
        if settings.is_local_mode():
            prefix = f"COURSE#{course_id}#DATE#"
            keys_to_delete = [k for k in self._local_store if k.startswith(prefix)]
            for key in keys_to_delete:
                del self._local_store[key]
            return len(keys_to_delete)
        
        # DynamoDB batch delete
        records = self.get_by_course(course_id)
        for record in records:
            self._dynamodb_table.delete_item(
                Key={'pk': record.pk, 'sk': record.sk}
            )
        return len(records)
    
    def clear_all(self) -> None:
        """Clear all records (LOCAL_MODE only, for testing)."""
        if settings.is_local_mode():
            self._local_store.clear()


# Singleton instance
_repository: Optional[AttendanceRepository] = None


def get_attendance_repository() -> AttendanceRepository:
    """Get the singleton attendance repository instance."""
    global _repository
    if _repository is None:
        _repository = AttendanceRepository()
    return _repository
