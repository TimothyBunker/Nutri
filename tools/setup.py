#!/usr/bin/env python3
"""
Setup script for Health & Fitness Discord Bot System
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path


class Colors:
    """Terminal colors"""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def print_header(text):
    """Print colored header"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{text}{Colors.ENDC}")


def print_success(text):
    """Print success message"""
    print(f"{Colors.OKGREEN}✓ {text}{Colors.ENDC}")


def print_error(text):
    """Print error message"""
    print(f"{Colors.FAIL}✗ {text}{Colors.ENDC}")


def print_info(text):
    """Print info message"""
    print(f"{Colors.OKBLUE}ℹ {text}{Colors.ENDC}")


def print_warning(text):
    """Print warning message"""
    print(f"{Colors.WARNING}⚠ {text}{Colors.ENDC}")


def check_python_version():
    """Check if Python version is 3.8+"""
    if sys.version_info < (3, 8):
        print_error("Python 3.8 or higher is required")
        print_info(f"Current version: {sys.version}")
        return False
    
    print_success(f"Python {sys.version.split()[0]} detected")
    return True


def check_pip():
    """Check if pip is available"""
    try:
        subprocess.run([sys.executable, '-m', 'pip', '--version'], 
                      capture_output=True, check=True)
        print_success("pip is available")
        return True
    except:
        print_error("pip is not available")
        return False


def install_requirements():
    """Install Python requirements"""
    print_header("Installing Python dependencies...")
    
    requirements_file = Path("requirements.txt")
    if not requirements_file.exists():
        print_error("requirements.txt not found")
        return False
    
    try:
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'],
                      check=True)
        print_success("Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError:
        print_error("Failed to install dependencies")
        return False


def setup_environment():
    """Set up environment file"""
    print_header("Setting up environment...")
    
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    if env_file.exists():
        print_info(".env file already exists")
        response = input("Do you want to overwrite it? (y/N): ")
        if response.lower() != 'y':
            print_info("Keeping existing .env file")
            return True
    
    if env_example.exists():
        shutil.copy(env_example, env_file)
        print_success("Created .env file from template")
        print_warning("Please edit .env and add your bot tokens!")
        return True
    else:
        print_info("Creating new .env file...")
        
        # Create .env with prompts
        tokens = {}
        
        print("\nPlease enter your bot tokens (or press Enter to skip):")
        tokens['NUTRITION_BOT_TOKEN'] = input("Nutrition Bot Token: ").strip()
        tokens['WORKOUT_BOT_TOKEN'] = input("Workout Bot Token: ").strip()
        
        # Write .env file
        with open(env_file, 'w') as f:
            f.write("# Health and Fitness Discord Bot Configuration\n\n")
            f.write("# Discord Bot Tokens (Required)\n")
            f.write(f"NUTRITION_BOT_TOKEN={tokens['NUTRITION_BOT_TOKEN']}\n")
            f.write(f"WORKOUT_BOT_TOKEN={tokens['WORKOUT_BOT_TOKEN']}\n\n")
            
            # Add defaults from example
            f.write("# Bot Settings\n")
            f.write("BOT_PREFIX=!\n")
            f.write("DEFAULT_TIMEZONE=America/New_York\n")
            f.write("DEFAULT_UNIT_SYSTEM=imperial\n\n")
            
            f.write("# Database Settings\n")
            f.write("NUTRITION_DB_PATH=nutrition.db\n")
            f.write("WORKOUT_DB_PATH=workout.db\n\n")
            
            f.write("# Feature Flags\n")
            f.write("ENABLE_ACHIEVEMENTS=true\n")
            f.write("ENABLE_LEADERBOARDS=true\n")
            f.write("ENABLE_AUTO_BACKUP=true\n")
            f.write("BACKUP_INTERVAL_HOURS=24\n\n")
            
            f.write("# Rate Limiting\n")
            f.write("COMMANDS_PER_MINUTE=30\n")
            f.write("GRAPH_CACHE_MINUTES=5\n\n")
            
            f.write("# Limits\n")
            f.write("MAX_GRAPH_DAYS=365\n")
            f.write("MAX_EXPORT_ROWS=10000\n\n")
            
            f.write("# Logging\n")
            f.write("LOG_LEVEL=INFO\n")
            f.write("LOG_FILE=bot.log\n")
            f.write("DEBUG_MODE=false\n")
        
        print_success("Created .env file")
        
        if not tokens['NUTRITION_BOT_TOKEN'] or not tokens['WORKOUT_BOT_TOKEN']:
            print_warning("Bot tokens not provided. Please edit .env before running the bots.")
        
        return True


def check_existing_data():
    """Check for existing databases and offer migration"""
    print_header("Checking for existing data...")
    
    old_nutrition_db = Path("nutrition.db")
    old_workout_db = Path("workout.db")
    
    if old_nutrition_db.exists() or old_workout_db.exists():
        print_info("Found existing database files")
        response = input("Do you want to migrate existing data? (Y/n): ")
        
        if response.lower() != 'n':
            # Create data directory
            data_dir = Path("data")
            data_dir.mkdir(exist_ok=True)
            
            # Move databases
            if old_nutrition_db.exists():
                shutil.move(old_nutrition_db, data_dir / "nutrition.db")
                print_success("Moved nutrition.db to data/")
            
            if old_workout_db.exists():
                shutil.move(old_workout_db, data_dir / "workout.db")
                print_success("Moved workout.db to data/")
            
            return True
    
    print_info("No existing data found")
    return True


def create_shortcuts():
    """Create convenient shortcuts for running bots"""
    print_header("Creating shortcuts...")
    
    # Unix-like systems
    if sys.platform != 'win32':
        # Create start script
        start_script = Path("start")
        with open(start_script, 'w') as f:
            f.write("#!/bin/bash\n")
            f.write(f'"{sys.executable}" run_bots.py "$@"\n')
        
        # Make executable
        os.chmod(start_script, 0o755)
        print_success("Created 'start' script")
    
    # Windows
    else:
        # Create batch file
        start_script = Path("start.cmd")
        with open(start_script, 'w') as f:
            f.write("@echo off\n")
            f.write(f'"{sys.executable}" run_bots.py %*\n')
        
        print_success("Created 'start.cmd' script")
    
    return True


def cleanup_old_files():
    """Clean up old files from previous structure"""
    print_header("Cleaning up old files...")
    
    old_files = [
        "nutri.py",
        "worko.py",
        "nutri_improved.py",
        "worko_improved.py",
        "utils.py",
        "config.py",
        "migrate.py",
        "bot_manager.log"
    ]
    
    removed = 0
    for file in old_files:
        file_path = Path(file)
        if file_path.exists():
            response = input(f"Remove old file '{file}'? (y/N): ")
            if response.lower() == 'y':
                file_path.unlink()
                removed += 1
    
    if removed > 0:
        print_success(f"Removed {removed} old files")
    else:
        print_info("No old files to remove")
    
    return True


def main():
    """Main setup process"""
    print(f"{Colors.HEADER}{Colors.BOLD}")
    print("╔═══════════════════════════════════════════╗")
    print("║   Health & Fitness Discord Bot Setup      ║")
    print("╚═══════════════════════════════════════════╝")
    print(Colors.ENDC)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Check pip
    if not check_pip():
        sys.exit(1)
    
    # Install requirements
    if not install_requirements():
        sys.exit(1)
    
    # Set up environment
    if not setup_environment():
        sys.exit(1)
    
    # Check for existing data
    check_existing_data()
    
    # Create shortcuts
    create_shortcuts()
    
    # Cleanup old files
    cleanup_old_files()
    
    # Success!
    print_header("Setup Complete! 🎉")
    print("\nNext steps:")
    print("1. Edit .env file and add your Discord bot tokens")
    print("2. Run the bots:")
    
    if sys.platform != 'win32':
        print("   ./start")
    else:
        print("   start.cmd")
    
    print("\nOr use Python directly:")
    print(f"   {sys.executable} run_bots.py")
    
    print("\nFor help, check the README.md file")
    print("\nHappy tracking! 💪")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nSetup cancelled by user")
        sys.exit(0)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        sys.exit(1)