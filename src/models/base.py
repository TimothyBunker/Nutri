"""
Base database management functionality
"""

import sqlite3
import os
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Base database manager with common functionality"""
    
    def __init__(self, db_path: Path):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
    
    @contextmanager
    def get_cursor(self):
        """Context manager for database operations"""
        conn = sqlite3.connect(str(self.db_path))
        # Enable foreign keys
        conn.execute("PRAGMA foreign_keys = ON")
        cursor = conn.cursor()
        try:
            yield cursor
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"Database error: {e}")
            raise e
        finally:
            conn.close()
    
    def backup(self, backup_dir: Path = None):
        """Create timestamped backup of database"""
        if backup_dir is None:
            from ..core.config import BACKUPS_DIR
            backup_dir = BACKUPS_DIR
        
        backup_dir = Path(backup_dir)
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = backup_dir / f"{self.db_path.stem}_{timestamp}.db"
        
        # Use SQLite backup API
        source = sqlite3.connect(str(self.db_path))
        dest = sqlite3.connect(str(backup_path))
        
        with dest:
            source.backup(dest)
        
        source.close()
        dest.close()
        
        logger.info(f"Database backed up to: {backup_path}")
        return backup_path
    
    def execute_script(self, script_path: Path):
        """Execute SQL script file"""
        with open(script_path, 'r') as f:
            script = f.read()
        
        with self.get_cursor() as cursor:
            cursor.executescript(script)
        
        logger.info(f"Executed SQL script: {script_path}")
    
    def table_exists(self, table_name: str) -> bool:
        """Check if a table exists"""
        with self.get_cursor() as cursor:
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
                (table_name,)
            )
            return cursor.fetchone() is not None
    
    def get_table_info(self, table_name: str) -> list:
        """Get information about table columns"""
        with self.get_cursor() as cursor:
            cursor.execute(f"PRAGMA table_info({table_name})")
            return cursor.fetchall()
    
    def vacuum(self):
        """Optimize database file size"""
        conn = sqlite3.connect(str(self.db_path))
        conn.execute("VACUUM")
        conn.close()
        logger.info(f"Database vacuumed: {self.db_path}")
    
    def get_size(self) -> int:
        """Get database file size in bytes"""
        return self.db_path.stat().st_size if self.db_path.exists() else 0
    
    def get_size_mb(self) -> float:
        """Get database file size in MB"""
        return self.get_size() / (1024 * 1024)