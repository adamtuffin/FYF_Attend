# Quickstart: Course Attendance Registration

**Feature**: 001-course-attendance  
**Date**: 2026-01-13

## Prerequisites

- Python 3.11+
- Node.js 18+ (for Tailwind CSS build)
- Git

## Quick Start (Recommended)

```powershell
cd C:\Development\FYF_Attend

# Run with all setup steps
.\run.ps1 -Install

# Or if dependencies are already installed
.\run.ps1
```

Open your browser to http://localhost:5000

## Manual Setup

### 1. Clone and Setup

```powershell
cd C:\Development\FYF_Attend

# Create Python virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install Python dependencies
pip install -r backend/requirements.txt

# Install Node dependencies for Tailwind
cd frontend
npm install
cd ..
```

### 2. Environment Configuration

Create a `.env.local` file in the project root (optional - defaults work):

```env
# Local development mode - bypasses AWS
LOCAL_MODE=true

# Flask development settings
FLASK_ENV=development
FLASK_DEBUG=1
FLASK_PORT=5000
```

**Important**: Never commit `.env.local` to version control.

### 3. Build Frontend Assets

```powershell
cd frontend

# Build Tailwind CSS
npm run build

cd ..
```

### 4. Run Local Server

```powershell
# From project root with venv activated
cd backend
python app.py

# Server starts at http://localhost:5000
```

### 5. Access the Application

Open your browser to:
- **Session List**: http://localhost:5000/
- **Session Details**: http://localhost:5000/sessions/SES001
- **Past Sessions**: http://localhost:5000/sessions/history
- **Test Config** (LOCAL_MODE only): http://localhost:5000/config/test-data

## Local Mode Features

When `LOCAL_MODE=true` (default):

1. **Sample Test Data**: Pre-loaded with sample courses, sessions, and attendees
2. **No AWS Required**: Attendance stored in-memory
3. **Config Screen**: View and reset test data at `/config/test-data`
4. **Reset Data**: Clear all recorded attendance

## Project Structure

```
FYF_Attend/
├── backend/
│   ├── app.py                  # Flask application entry point
│   ├── src/
│   │   ├── handlers/           # Route handlers
│   │   ├── models/             # Data models
│   │   ├── services/           # Business logic
│   │   └── config/             # Settings
│   ├── tests/
│   ├── template.yaml           # CloudFormation template
│   └── requirements.txt
├── frontend/
│   ├── templates/              # Jinja2 HTML templates
│   │   ├── base.html
│   │   ├── sessions/
│   │   └── config/
│   ├── static/
│   │   ├── css/
│   │   ├── js/
│   │   └── images/
│   ├── src/input.css           # Tailwind source
│   ├── tailwind.config.js
│   └── package.json
├── specs/                      # Feature specifications
├── .env.local                  # Local environment (git-ignored)
└── run.ps1                     # Quick start script
```

## API Endpoints

### Sessions

- `GET /sessions/` - List upcoming sessions
- `GET /sessions/<session_id>` - Session detail page
- `GET /sessions/history` - Past sessions

### Attendance (API)

- `GET /api/attendance/sessions/<session_id>/attendees` - Get attendees with pagination
- `POST /api/attendance/sessions/<session_id>/attendance` - Record attendance
- `GET /api/attendance/sessions/<session_id>/summary` - Get attendance summary

### Configuration (LOCAL_MODE only)

- `GET /config/test-data` - View test data configuration
- `POST /config/test-data/reset` - Reset test data
- `GET /config/api/test-data` - Get test data as JSON
- `POST /config/api/test-data` - Set test data
- `DELETE /config/api/test-data` - Reset test data via API

## Running Tests

```powershell
# From project root with venv activated
cd backend

# Run all tests
pytest

# Run with coverage
pytest --cov=src

# Run specific test file
pytest tests/unit/test_attendance_service.py
```

## Example API Usage

### Record Attendance

```powershell
# Mark as attended
Invoke-RestMethod -Uri "http://localhost:5000/api/attendance/sessions/SES001/attendance" `
  -Method POST -ContentType "application/json" `
  -Body '{"attendee_id": "ATT001001", "status": "attended"}'

# Mark as late with reason
Invoke-RestMethod -Uri "http://localhost:5000/api/attendance/sessions/SES001/attendance" `
  -Method POST -ContentType "application/json" `
  -Body '{"attendee_id": "ATT001002", "status": "late", "late_reason": "Bus was delayed"}'
```

### Get Attendees with Search

```powershell
Invoke-RestMethod -Uri "http://localhost:5000/api/attendance/sessions/SES001/attendees?search=alice&page=1"
```

## Troubleshooting

### "Module not found" errors

Ensure your virtual environment is activated:
```powershell
.\.venv\Scripts\Activate.ps1
```

### Tailwind styles not applying

Rebuild the CSS:
```powershell
cd frontend
npm run build
cd ..
```

### Test data not persisting

In LOCAL_MODE, data is stored in-memory and resets when the server restarts. This is intentional for development.

### Port already in use

Change the port in `.env.local`:
```env
FLASK_PORT=5001
```

## Next Steps

1. Review remaining tasks in `specs/001-course-attendance/tasks.md`
2. Write unit tests (T020-T032)
3. Run accessibility tests (T070, T074)
4. Deploy to AWS using CloudFormation template
