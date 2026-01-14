"""
Find Your Feet CIC - Course Attendance Registration
AWS Lambda Handler

Wraps the Flask application for AWS Lambda + API Gateway.
Uses aws-wsgi for WSGI to Lambda event translation.
"""

import os
import sys
from pathlib import Path

# Add src to path for imports
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

# Set environment for Lambda
os.environ.setdefault('LOCAL_MODE', 'false')

import awsgi
from app import create_app

# Create Flask application instance
flask_app = create_app()


def handler(event, context):
    """
    AWS Lambda handler function.
    
    Translates API Gateway events to WSGI requests and back.
    
    Args:
        event: API Gateway event dictionary
        context: Lambda context object
        
    Returns:
        API Gateway response dictionary
    """
    # Handle warmup events (if using provisioned concurrency warmup)
    if event.get('source') == 'serverless-plugin-warmup':
        return {'statusCode': 200, 'body': 'Warmed up'}
    
    # Handle scheduled events (if using keep-warm pings)
    if event.get('source') == 'aws.events':
        return {'statusCode': 200, 'body': 'Ping received'}
    
    # Process API Gateway request through Flask
    return awsgi.response(flask_app, event, context, base64_content_types={'image/png', 'image/webp', 'image/jpeg'})
