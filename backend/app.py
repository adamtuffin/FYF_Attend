"""
Find Your Feet CIC - Course Attendance Registration
Flask Application (Local Development)

T015: Flask app factory with Jinja2 configuration
"""

import os
import sys
from pathlib import Path

from flask import Flask
from dotenv import load_dotenv

# Add src to path for imports
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

# Load environment variables
load_dotenv(backend_dir.parent / '.env.local')


def create_app(test_config: dict = None) -> Flask:
    """
    Application factory for Flask app.
    
    Args:
        test_config: Optional test configuration to override settings
        
    Returns:
        Configured Flask application
    """
    # Determine if running in Lambda or local
    is_lambda = os.getenv('AWS_LAMBDA_FUNCTION_NAME') is not None
    
    if is_lambda:
        # In Lambda, templates are bundled with the backend code
        template_folder = str(backend_dir / 'templates')
        static_folder = str(backend_dir / 'static')
    else:
        # Local development - use frontend folder
        template_folder = str(backend_dir.parent / 'frontend' / 'templates')
        static_folder = str(backend_dir.parent / 'frontend' / 'static')
    
    app = Flask(
        __name__,
        template_folder=template_folder,
        static_folder=static_folder
    )
    
    # Default configuration
    app.config.from_mapping(
        SECRET_KEY=os.getenv('FLASK_SECRET_KEY', 'dev-secret-key'),
        LOCAL_MODE=os.getenv('LOCAL_MODE', 'true').lower() == 'true',
    )
    
    # Override with test config if provided
    if test_config:
        app.config.update(test_config)
    
    # Register Jinja2 template context
    @app.context_processor
    def inject_globals():
        """Inject global variables into templates."""
        return {
            'local_mode': app.config['LOCAL_MODE'],
            'app_name': 'Find Your Feet',
        }
    
    # Register blueprints
    from src.handlers import sessions, attendance, config
    app.register_blueprint(sessions.bp)
    app.register_blueprint(attendance.bp)
    app.register_blueprint(config.bp)
    
    # Root route redirects to sessions
    @app.route('/')
    def index():
        from flask import redirect, url_for
        return redirect(url_for('sessions.list_sessions'))
    
    return app


def run_app():
    """Run the Flask application for local development."""
    app = create_app()
    port = int(os.getenv('FLASK_PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', '1') == '1'
    app.run(host='0.0.0.0', port=port, debug=debug)


if __name__ == '__main__':
    run_app()
