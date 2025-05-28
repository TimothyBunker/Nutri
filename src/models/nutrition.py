"""
Nutrition database models and operations
"""

from datetime import datetime, date
from typing import Optional, List, Dict, Tuple
import json
from .base import DatabaseManager


class NutritionDatabase(DatabaseManager):
    """Database operations for nutrition tracking"""
    
    def init_db(self):
        """Initialize all nutrition tables"""
        with self.get_cursor() as c:
            # Core tables
            c.execute('''CREATE TABLE IF NOT EXISTS meals
                         (id INTEGER PRIMARY KEY AUTOINCREMENT,
                          user_id INTEGER NOT NULL,
                          date TEXT NOT NULL,
                          time TEXT NOT NULL,
                          food_item TEXT NOT NULL,
                          calories INTEGER NOT NULL,
                          protein REAL DEFAULT 0,
                          carbs REAL DEFAULT 0,
                          fats REAL DEFAULT 0,
                          fiber REAL DEFAULT 0,
                          sodium REAL DEFAULT 0,
                          edited INTEGER DEFAULT 0,
                          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                          updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
            
            c.execute('''CREATE TABLE IF NOT EXISTS meal_schedule
                         (id INTEGER PRIMARY KEY AUTOINCREMENT,
                          user_id INTEGER NOT NULL,
                          meal_name TEXT NOT NULL,
                          time TEXT NOT NULL,
                          enabled INTEGER DEFAULT 1,
                          days_of_week TEXT DEFAULT '0,1,2,3,4,5,6',
                          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
            
            c.execute('''CREATE TABLE IF NOT EXISTS user_stats
                         (user_id INTEGER PRIMARY KEY,
                          height_inches INTEGER,
                          current_weight REAL,
                          goal_weight REAL,
                          activity_level TEXT DEFAULT 'moderate',
                          daily_calorie_target INTEGER,
                          daily_protein_target INTEGER,
                          daily_carb_target INTEGER,
                          daily_fat_target INTEGER,
                          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                          updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
            
            c.execute('''CREATE TABLE IF NOT EXISTS weight_log
                         (id INTEGER PRIMARY KEY AUTOINCREMENT,
                          user_id INTEGER NOT NULL,
                          date TEXT NOT NULL,
                          weight REAL NOT NULL,
                          body_fat REAL,
                          muscle_mass REAL,
                          water_percentage REAL,
                          notes TEXT,
                          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
            
            c.execute('''CREATE TABLE IF NOT EXISTS meal_presets
                         (id INTEGER PRIMARY KEY AUTOINCREMENT,
                          user_id INTEGER NOT NULL,
                          name TEXT NOT NULL,
                          food_item TEXT NOT NULL,
                          calories INTEGER NOT NULL,
                          protein REAL DEFAULT 0,
                          carbs REAL DEFAULT 0,
                          fats REAL DEFAULT 0,
                          is_recipe INTEGER DEFAULT 0,
                          ingredients TEXT,
                          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                          UNIQUE(user_id, name))''')
            
            c.execute('''CREATE TABLE IF NOT EXISTS food_database
                         (id INTEGER PRIMARY KEY AUTOINCREMENT,
                          name TEXT UNIQUE NOT NULL,
                          brand TEXT,
                          serving_size TEXT,
                          calories_per_serving INTEGER,
                          protein_per_serving REAL,
                          carbs_per_serving REAL,
                          fats_per_serving REAL,
                          barcode TEXT,
                          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
            
            # Create indexes
            c.execute("CREATE INDEX IF NOT EXISTS idx_meals_user_date ON meals(user_id, date)")
            c.execute("CREATE INDEX IF NOT EXISTS idx_weight_log_user_date ON weight_log(user_id, date)")
            c.execute("CREATE INDEX IF NOT EXISTS idx_meal_presets_user ON meal_presets(user_id)")
    
    # Meal operations
    def log_meal(self, user_id: int, food_item: str, calories: int,
                 protein: float = 0, carbs: float = 0, fats: float = 0,
                 fiber: float = 0, sodium: float = 0) -> int:
        """Log a meal and return the meal ID"""
        now = datetime.now()
        with self.get_cursor() as c:
            c.execute('''INSERT INTO meals 
                         (user_id, date, time, food_item, calories, 
                          protein, carbs, fats, fiber, sodium)
                         VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                      (user_id, now.date().isoformat(), now.time().strftime("%H:%M"),
                       food_item, calories, protein, carbs, fats, fiber, sodium))
            return c.lastrowid
    
    def get_meal(self, meal_id: int, user_id: int) -> Optional[Dict]:
        """Get a specific meal"""
        with self.get_cursor() as c:
            c.execute('''SELECT * FROM meals 
                         WHERE id = ? AND user_id = ?''',
                      (meal_id, user_id))
            row = c.fetchone()
            
            if row:
                columns = [col[0] for col in c.description]
                return dict(zip(columns, row))
            return None
    
    def update_meal(self, meal_id: int, user_id: int, **kwargs) -> bool:
        """Update meal fields"""
        allowed_fields = ['food_item', 'calories', 'protein', 'carbs', 'fats', 
                         'fiber', 'sodium']
        
        # Filter to allowed fields only
        updates = {k: v for k, v in kwargs.items() if k in allowed_fields}
        if not updates:
            return False
        
        # Build update query
        set_clause = ", ".join([f"{k} = ?" for k in updates.keys()])
        values = list(updates.values())
        values.extend([meal_id, user_id])
        
        with self.get_cursor() as c:
            c.execute(f'''UPDATE meals 
                          SET {set_clause}, edited = 1, 
                              updated_at = CURRENT_TIMESTAMP
                          WHERE id = ? AND user_id = ?''',
                      values)
            return c.rowcount > 0
    
    def delete_meal(self, meal_id: int, user_id: int) -> bool:
        """Delete a meal"""
        with self.get_cursor() as c:
            c.execute("DELETE FROM meals WHERE id = ? AND user_id = ?",
                      (meal_id, user_id))
            return c.rowcount > 0
    
    def get_meals_for_date(self, user_id: int, date_str: str) -> List[Dict]:
        """Get all meals for a specific date"""
        with self.get_cursor() as c:
            c.execute('''SELECT * FROM meals 
                         WHERE user_id = ? AND date = ?
                         ORDER BY time''',
                      (user_id, date_str))
            
            columns = [col[0] for col in c.description]
            return [dict(zip(columns, row)) for row in c.fetchall()]
    
    def get_daily_totals(self, user_id: int, date_str: str) -> Dict:
        """Get daily nutrition totals"""
        with self.get_cursor() as c:
            c.execute('''SELECT 
                            SUM(calories) as total_calories,
                            SUM(protein) as total_protein,
                            SUM(carbs) as total_carbs,
                            SUM(fats) as total_fats,
                            SUM(fiber) as total_fiber,
                            SUM(sodium) as total_sodium,
                            COUNT(*) as meal_count
                         FROM meals 
                         WHERE user_id = ? AND date = ?''',
                      (user_id, date_str))
            
            row = c.fetchone()
            return {
                'calories': row[0] or 0,
                'protein': row[1] or 0,
                'carbs': row[2] or 0,
                'fats': row[3] or 0,
                'fiber': row[4] or 0,
                'sodium': row[5] or 0,
                'meal_count': row[6] or 0
            }
    
    # User stats operations
    def get_user_stats(self, user_id: int) -> Optional[Dict]:
        """Get user statistics"""
        with self.get_cursor() as c:
            c.execute("SELECT * FROM user_stats WHERE user_id = ?", (user_id,))
            row = c.fetchone()
            
            if row:
                columns = [col[0] for col in c.description]
                return dict(zip(columns, row))
            return None
    
    def update_user_stats(self, user_id: int, **kwargs) -> bool:
        """Update or create user stats"""
        allowed_fields = ['height_inches', 'current_weight', 'goal_weight',
                         'activity_level', 'daily_calorie_target', 
                         'daily_protein_target', 'daily_carb_target',
                         'daily_fat_target']
        
        updates = {k: v for k, v in kwargs.items() if k in allowed_fields}
        if not updates:
            return False
        
        # Check if user exists
        with self.get_cursor() as c:
            c.execute("SELECT 1 FROM user_stats WHERE user_id = ?", (user_id,))
            exists = c.fetchone() is not None
            
            if exists:
                # Update existing
                set_clause = ", ".join([f"{k} = ?" for k in updates.keys()])
                values = list(updates.values())
                values.append(user_id)
                
                c.execute(f'''UPDATE user_stats 
                              SET {set_clause}, updated_at = CURRENT_TIMESTAMP
                              WHERE user_id = ?''',
                          values)
            else:
                # Insert new
                updates['user_id'] = user_id
                columns = ", ".join(updates.keys())
                placeholders = ", ".join(["?" for _ in updates])
                
                c.execute(f'''INSERT INTO user_stats ({columns})
                              VALUES ({placeholders})''',
                          list(updates.values()))
            
            return True
    
    # Weight tracking
    def log_weight(self, user_id: int, weight: float, body_fat: Optional[float] = None,
                   muscle_mass: Optional[float] = None, water_percentage: Optional[float] = None,
                   notes: Optional[str] = None) -> int:
        """Log weight measurement"""
        with self.get_cursor() as c:
            c.execute('''INSERT INTO weight_log 
                         (user_id, date, weight, body_fat, muscle_mass, 
                          water_percentage, notes)
                         VALUES (?, ?, ?, ?, ?, ?, ?)''',
                      (user_id, date.today().isoformat(), weight, body_fat,
                       muscle_mass, water_percentage, notes))
            
            # Update current weight in user stats
            c.execute("UPDATE user_stats SET current_weight = ? WHERE user_id = ?",
                      (weight, user_id))
            
            return c.lastrowid
    
    def get_weight_history(self, user_id: int, days: int = 30) -> List[Dict]:
        """Get weight history for the last N days"""
        with self.get_cursor() as c:
            c.execute('''SELECT * FROM weight_log 
                         WHERE user_id = ? 
                         AND date >= date('now', '-' || ? || ' days')
                         ORDER BY date DESC''',
                      (user_id, days))
            
            columns = [col[0] for col in c.description]
            return [dict(zip(columns, row)) for row in c.fetchall()]
    
    # Meal presets
    def save_preset(self, user_id: int, name: str, food_item: str,
                    calories: int, protein: float = 0, carbs: float = 0,
                    fats: float = 0, is_recipe: bool = False,
                    ingredients: Optional[List[Dict]] = None) -> bool:
        """Save a meal preset"""
        with self.get_cursor() as c:
            ingredients_json = json.dumps(ingredients) if ingredients else None
            
            c.execute('''INSERT OR REPLACE INTO meal_presets 
                         (user_id, name, food_item, calories, protein, 
                          carbs, fats, is_recipe, ingredients)
                         VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                      (user_id, name.lower(), food_item, calories, protein,
                       carbs, fats, int(is_recipe), ingredients_json))
            return True
    
    def get_preset(self, user_id: int, name: str) -> Optional[Dict]:
        """Get a meal preset by name"""
        with self.get_cursor() as c:
            c.execute('''SELECT * FROM meal_presets 
                         WHERE user_id = ? AND name = ?''',
                      (user_id, name.lower()))
            row = c.fetchone()
            
            if row:
                columns = [col[0] for col in c.description]
                preset = dict(zip(columns, row))
                if preset.get('ingredients'):
                    preset['ingredients'] = json.loads(preset['ingredients'])
                return preset
            return None
    
    def get_all_presets(self, user_id: int) -> List[Dict]:
        """Get all presets for a user"""
        with self.get_cursor() as c:
            c.execute('''SELECT * FROM meal_presets 
                         WHERE user_id = ?
                         ORDER BY name''',
                      (user_id,))
            
            columns = [col[0] for col in c.description]
            presets = []
            for row in c.fetchall():
                preset = dict(zip(columns, row))
                if preset.get('ingredients'):
                    preset['ingredients'] = json.loads(preset['ingredients'])
                presets.append(preset)
            
            return presets
    
    def delete_preset(self, user_id: int, name: str) -> bool:
        """Delete a meal preset"""
        with self.get_cursor() as c:
            c.execute("DELETE FROM meal_presets WHERE user_id = ? AND name = ?",
                      (user_id, name.lower()))
            return c.rowcount > 0
    
    # Analytics
    def get_nutrition_trends(self, user_id: int, days: int = 7) -> List[Dict]:
        """Get daily nutrition averages for trending"""
        with self.get_cursor() as c:
            c.execute('''SELECT 
                            date,
                            SUM(calories) as daily_calories,
                            SUM(protein) as daily_protein,
                            SUM(carbs) as daily_carbs,
                            SUM(fats) as daily_fats,
                            COUNT(*) as meal_count
                         FROM meals 
                         WHERE user_id = ? 
                         AND date >= date('now', '-' || ? || ' days')
                         GROUP BY date
                         ORDER BY date''',
                      (user_id, days))
            
            columns = [col[0] for col in c.description]
            return [dict(zip(columns, row)) for row in c.fetchall()]
    
    def get_meal_frequency(self, user_id: int, days: int = 30) -> Dict[str, int]:
        """Get most frequently logged foods"""
        with self.get_cursor() as c:
            c.execute('''SELECT food_item, COUNT(*) as frequency
                         FROM meals 
                         WHERE user_id = ? 
                         AND date >= date('now', '-' || ? || ' days')
                         GROUP BY LOWER(food_item)
                         ORDER BY frequency DESC
                         LIMIT 20''',
                      (user_id, days))
            
            return {row[0]: row[1] for row in c.fetchall()}