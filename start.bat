@echo off
REM Quick start script for Health & Fitness Discord Bots (Windows)

echo Health and Fitness Bot Launcher
echo ================================

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed. Please install Python 3.8 or higher.
    pause
    exit /b 1
)

REM Check if .env file exists
if not exist ".env" (
    echo WARNING: No .env file found. Creating from template...
    if exist ".env.example" (
        copy ".env.example" ".env"
        echo Created .env file. Please edit it and add your bot tokens.
        echo Edit .env and add:
        echo - NUTRITION_BOT_TOKEN=your_token_here
        echo - WORKOUT_BOT_TOKEN=your_token_here
        pause
        exit /b 1
    ) else (
        echo ERROR: No .env.example file found.
        pause
        exit /b 1
    )
)

REM Install requirements
echo Checking dependencies...
python -m pip install -q -r requirements.txt

REM Run migration if databases exist
if exist "nutrition.db" (
    echo Found existing databases. Running migration check...
    python migrate.py --auto
)

REM Start the bot manager
echo.
echo Starting bots...
echo Press Ctrl+C to stop
echo Type 'help' for commands
echo.

python run_bots.py %*

pause