"""
Configuration management for Health & Fitness Discord bots
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Get project root directory
PROJECT_ROOT = Path(__file__).parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data"
LOGS_DIR = PROJECT_ROOT / "logs"
BACKUPS_DIR = PROJECT_ROOT / "backups"

# Create directories if they don't exist
for directory in [DATA_DIR, LOGS_DIR, BACKUPS_DIR]:
    directory.mkdir(exist_ok=True)

# Load environment variables
load_dotenv(PROJECT_ROOT / ".env")

# Bot tokens
NUTRITION_BOT_TOKEN = os.getenv('NUTRITION_BOT_TOKEN', '')
WORKOUT_BOT_TOKEN = os.getenv('WORKOUT_BOT_TOKEN', '')

# Bot settings
BOT_PREFIX = os.getenv('BOT_PREFIX', '!')
EMBED_FOOTER = "Health & Fitness Tracker"

# Database paths - now in data directory
NUTRITION_DB_PATH = DATA_DIR / os.getenv('NUTRITION_DB_PATH', 'nutrition.db')
WORKOUT_DB_PATH = DATA_DIR / os.getenv('WORKOUT_DB_PATH', 'workout.db')

# Feature flags
ENABLE_ACHIEVEMENTS = os.getenv('ENABLE_ACHIEVEMENTS', 'true').lower() == 'true'
ENABLE_LEADERBOARDS = os.getenv('ENABLE_LEADERBOARDS', 'true').lower() == 'true'
ENABLE_AUTO_BACKUP = os.getenv('ENABLE_AUTO_BACKUP', 'true').lower() == 'true'
BACKUP_INTERVAL_HOURS = int(os.getenv('BACKUP_INTERVAL_HOURS', '24'))

# Rate limiting
COMMANDS_PER_MINUTE = int(os.getenv('COMMANDS_PER_MINUTE', '30'))
GRAPH_CACHE_MINUTES = int(os.getenv('GRAPH_CACHE_MINUTES', '5'))

# Default values
DEFAULT_TIMEZONE = os.getenv('DEFAULT_TIMEZONE', 'UTC')
DEFAULT_UNIT_SYSTEM = os.getenv('DEFAULT_UNIT_SYSTEM', 'imperial')

# Limits
MAX_GRAPH_DAYS = int(os.getenv('MAX_GRAPH_DAYS', '365'))
MAX_EXPORT_ROWS = int(os.getenv('MAX_EXPORT_ROWS', '10000'))

# Discord settings
MAX_EMBED_FIELDS = 25
MAX_EMBED_DESCRIPTION = 4096
MAX_MESSAGE_LENGTH = 2000

# Logging configuration
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FILE_NUTRITION = LOGS_DIR / 'nutrition_bot.log'
LOG_FILE_WORKOUT = LOGS_DIR / 'workout_bot.log'
LOG_FILE_MANAGER = LOGS_DIR / 'bot_manager.log'

# Development mode
DEBUG_MODE = os.getenv('DEBUG_MODE', 'false').lower() == 'true'


def validate_config():
    """Validate that required configuration is present"""
    errors = []
    
    if not NUTRITION_BOT_TOKEN:
        errors.append("NUTRITION_BOT_TOKEN not set in environment")
    
    if not WORKOUT_BOT_TOKEN:
        errors.append("WORKOUT_BOT_TOKEN not set in environment")
    
    if errors:
        print("Configuration errors:")
        for error in errors:
            print(f"  - {error}")
        print(f"\nPlease create a .env file in {PROJECT_ROOT}")
        print("Example .env file:")
        print("NUTRITION_BOT_TOKEN=your_nutrition_bot_token_here")
        print("WORKOUT_BOT_TOKEN=your_workout_bot_token_here")
        return False
    
    return True