"""
User preferences management
"""

from typing import Dict, Optional
from ..models.base import DatabaseManager


class UserPreferences:
    """Manage user preferences and settings"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
        self._init_preferences_table()
    
    def _init_preferences_table(self):
        """Create preferences table if it doesn't exist"""
        with self.db.get_cursor() as c:
            c.execute('''CREATE TABLE IF NOT EXISTS user_preferences
                         (user_id INTEGER PRIMARY KEY,
                          units TEXT DEFAULT 'imperial',
                          timezone TEXT DEFAULT 'UTC',
                          language TEXT DEFAULT 'en',
                          privacy_mode TEXT DEFAULT 'public',
                          notifications_enabled INTEGER DEFAULT 1,
                          rest_timer_enabled INTEGER DEFAULT 1,
                          auto_pr_check INTEGER DEFAULT 1,
                          default_increment_lbs REAL DEFAULT 5,
                          default_increment_kg REAL DEFAULT 2.5,
                          theme TEXT DEFAULT 'default',
                          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                          updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
    def get_preferences(self, user_id: int) -> Dict:
        """Get all user preferences"""
        with self.db.get_cursor() as c:
            c.execute("SELECT * FROM user_preferences WHERE user_id = ?", (user_id,))
            row = c.fetchone()
            
            if not row:
                # Return defaults
                return self._get_defaults()
            
            columns = [col[0] for col in c.description]
            prefs = dict(zip(columns, row))
            
            # Convert integer booleans
            bool_fields = ['notifications_enabled', 'rest_timer_enabled', 'auto_pr_check']
            for field in bool_fields:
                if field in prefs:
                    prefs[field] = bool(prefs[field])
            
            return prefs
    
    def _get_defaults(self) -> Dict:
        """Get default preferences"""
        return {
            'units': 'imperial',
            'timezone': 'UTC',
            'language': 'en',
            'privacy_mode': 'public',
            'notifications_enabled': True,
            'rest_timer_enabled': True,
            'auto_pr_check': True,
            'default_increment_lbs': 5.0,
            'default_increment_kg': 2.5,
            'theme': 'default'
        }
    
    def get_user_units(self, user_id: int) -> str:
        """Get user's preferred unit system"""
        with self.db.get_cursor() as c:
            c.execute("SELECT units FROM user_preferences WHERE user_id = ?", (user_id,))
            result = c.fetchone()
            return result[0] if result else 'imperial'
    
    def set_user_units(self, user_id: int, units: str) -> bool:
        """Set user's preferred unit system"""
        if units not in ['imperial', 'metric']:
            return False
        
        return self.update_preference(user_id, 'units', units)
    
    def get_user_timezone(self, user_id: int) -> str:
        """Get user's timezone"""
        with self.db.get_cursor() as c:
            c.execute("SELECT timezone FROM user_preferences WHERE user_id = ?", (user_id,))
            result = c.fetchone()
            return result[0] if result else 'UTC'
    
    def set_user_timezone(self, user_id: int, timezone: str) -> bool:
        """Set user's timezone"""
        # You could add timezone validation here
        return self.update_preference(user_id, 'timezone', timezone)
    
    def get_privacy_mode(self, user_id: int) -> str:
        """Get user's privacy mode"""
        with self.db.get_cursor() as c:
            c.execute("SELECT privacy_mode FROM user_preferences WHERE user_id = ?", (user_id,))
            result = c.fetchone()
            return result[0] if result else 'public'
    
    def set_privacy_mode(self, user_id: int, mode: str) -> bool:
        """Set user's privacy mode"""
        if mode not in ['public', 'friends', 'private']:
            return False
        
        return self.update_preference(user_id, 'privacy_mode', mode)
    
    def is_rest_timer_enabled(self, user_id: int) -> bool:
        """Check if rest timer is enabled"""
        with self.db.get_cursor() as c:
            c.execute("SELECT rest_timer_enabled FROM user_preferences WHERE user_id = ?", (user_id,))
            result = c.fetchone()
            return bool(result[0]) if result else True
    
    def is_auto_pr_enabled(self, user_id: int) -> bool:
        """Check if automatic PR checking is enabled"""
        with self.db.get_cursor() as c:
            c.execute("SELECT auto_pr_check FROM user_preferences WHERE user_id = ?", (user_id,))
            result = c.fetchone()
            return bool(result[0]) if result else True
    
    def get_default_increment(self, user_id: int) -> float:
        """Get default weight increment for user's unit system"""
        units = self.get_user_units(user_id)
        field = 'default_increment_kg' if units == 'metric' else 'default_increment_lbs'
        
        with self.db.get_cursor() as c:
            c.execute(f"SELECT {field} FROM user_preferences WHERE user_id = ?", (user_id,))
            result = c.fetchone()
            
            if result:
                return result[0]
            
            # Return default
            return 2.5 if units == 'metric' else 5.0
    
    def update_preference(self, user_id: int, key: str, value) -> bool:
        """Update a single preference"""
        allowed_keys = [
            'units', 'timezone', 'language', 'privacy_mode',
            'notifications_enabled', 'rest_timer_enabled', 'auto_pr_check',
            'default_increment_lbs', 'default_increment_kg', 'theme'
        ]
        
        if key not in allowed_keys:
            return False
        
        with self.db.get_cursor() as c:
            # Check if user exists
            c.execute("SELECT 1 FROM user_preferences WHERE user_id = ?", (user_id,))
            exists = c.fetchone() is not None
            
            if exists:
                # Update existing
                c.execute(f'''UPDATE user_preferences 
                              SET {key} = ?, updated_at = CURRENT_TIMESTAMP
                              WHERE user_id = ?''',
                          (value, user_id))
            else:
                # Insert new with this preference
                c.execute(f'''INSERT INTO user_preferences (user_id, {key})
                              VALUES (?, ?)''',
                          (user_id, value))
            
            return True
    
    def update_preferences(self, user_id: int, **kwargs) -> bool:
        """Update multiple preferences at once"""
        for key, value in kwargs.items():
            if not self.update_preference(user_id, key, value):
                return False
        
        return True
    
    def reset_preferences(self, user_id: int) -> bool:
        """Reset user preferences to defaults"""
        with self.db.get_cursor() as c:
            c.execute("DELETE FROM user_preferences WHERE user_id = ?", (user_id,))
            return c.rowcount > 0
    
    def can_view_profile(self, viewer_id: int, profile_user_id: int) -> bool:
        """Check if viewer can see profile based on privacy settings"""
        if viewer_id == profile_user_id:
            return True
        
        privacy_mode = self.get_privacy_mode(profile_user_id)
        
        if privacy_mode == 'public':
            return True
        elif privacy_mode == 'private':
            return False
        elif privacy_mode == 'friends':
            # TODO: Implement friends system
            # For now, return False
            return False
        
        return False