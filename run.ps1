# Find Your Feet CIC - Course Attendance Registration
# Local Development Run Script

param(
    [switch]$Install,
    [switch]$Build,
    [switch]$Help
)

if ($Help) {
    Write-Host @"
Find Your Feet - Course Attendance Registration
================================================

Usage: .\run.ps1 [options]

Options:
    -Install    Install Python and Node.js dependencies
    -Build      Rebuild Tailwind CSS
    -Help       Show this help message

Examples:
    .\run.ps1           # Start the Flask development server
    .\run.ps1 -Install  # Install dependencies first, then start server
    .\run.ps1 -Build    # Rebuild CSS first, then start server
"@
    exit 0
}

Set-Location $PSScriptRoot

# Create virtual environment if it doesn't exist
if (-not (Test-Path ".venv")) {
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    python -m venv .venv
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Green
. .\.venv\Scripts\Activate.ps1

# Install dependencies if requested
if ($Install) {
    Write-Host "Installing Python dependencies..." -ForegroundColor Yellow
    pip install -r backend/requirements.txt
    
    Write-Host "Installing Node.js dependencies..." -ForegroundColor Yellow
    Set-Location frontend
    npm install
    Set-Location ..
}

# Build CSS if requested
if ($Build) {
    Write-Host "Building Tailwind CSS..." -ForegroundColor Yellow
    Set-Location frontend
    npx tailwindcss -i ./src/input.css -o ./static/css/output.css --minify
    Set-Location ..
}

# Start Flask server
Write-Host ""
Write-Host "Starting Flask development server..." -ForegroundColor Green
Write-Host "Application: http://localhost:5000" -ForegroundColor Cyan
Write-Host "Press Ctrl+C to stop" -ForegroundColor Gray
Write-Host ""

Set-Location backend
python app.py
