"""
Find Your Feet CIC - Course Attendance Registration
Settings and Environment Configuration

T008: Settings module with LOCAL_MODE toggle and environment config
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env.local if it exists
env_path = Path(__file__).parent.parent.parent.parent / '.env.local'
if env_path.exists():
    load_dotenv(env_path)


class Settings:
    """Application settings loaded from environment variables."""
    
    # Local Development Mode
    # When True, uses in-memory data instead of AWS services
    LOCAL_MODE: bool = os.getenv('LOCAL_MODE', 'true').lower() == 'true'
    
    # Flask Settings
    FLASK_ENV: str = os.getenv('FLASK_ENV', 'development')
    FLASK_DEBUG: bool = os.getenv('FLASK_DEBUG', '1') == '1'
    FLASK_PORT: int = int(os.getenv('FLASK_PORT', '5000'))
    FLASK_SECRET_KEY: str = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # AWS Settings
    AWS_REGION: str = os.getenv('AWS_REGION', 'eu-west-2')
    DYNAMODB_TABLE_NAME: str = os.getenv('DYNAMODB_TABLE_NAME', 'FYFAttendance')
    DYNAMODB_ENDPOINT: str | None = os.getenv('DYNAMODB_ENDPOINT')
    
    # External API Settings
    EXTERNAL_API_URL: str | None = os.getenv('EXTERNAL_API_URL')
    EXTERNAL_API_KEY: str | None = os.getenv('EXTERNAL_API_KEY')
    
    # Logging
    LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'DEBUG')
    
    # Session configuration
    UPCOMING_DAYS: int = 7  # Show sessions for today + next 7 days
    PAGE_SIZE: int = 25  # Attendees per page
    LATE_REASON_MAX_LENGTH: int = 500
    
    @classmethod
    def is_local_mode(cls) -> bool:
        """Check if running in local development mode."""
        return cls.LOCAL_MODE
    
    @classmethod
    def get_dynamodb_config(cls) -> dict:
        """Get DynamoDB connection configuration."""
        config = {
            'region_name': cls.AWS_REGION,
        }
        if cls.DYNAMODB_ENDPOINT:
            config['endpoint_url'] = cls.DYNAMODB_ENDPOINT
        return config


# Create a singleton instance
settings = Settings()
