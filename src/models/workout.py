"""
Workout database models and operations
"""

from datetime import datetime, date
from typing import Optional, List, Dict, Tuple
import json
from .base import DatabaseManager


class WorkoutDatabase(DatabaseManager):
    """Database operations for workout tracking"""
    
    def init_db(self):
        """Initialize all workout tables"""
        with self.get_cursor() as c:
            # Core tables
            c.execute('''CREATE TABLE IF NOT EXISTS exercises
                         (id INTEGER PRIMARY KEY AUTOINCREMENT,
                          name TEXT UNIQUE NOT NULL,
                          muscle_group TEXT NOT NULL,
                          equipment TEXT,
                          is_compound INTEGER DEFAULT 0,
                          description TEXT,
                          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
            
            c.execute('''CREATE TABLE IF NOT EXISTS workout_templates
                         (id INTEGER PRIMARY KEY AUTOINCREMENT,
                          user_id INTEGER NOT NULL,
                          name TEXT NOT NULL,
                          day_type TEXT,
                          exercises TEXT NOT NULL,
                          notes TEXT,
                          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                          last_used TIMESTAMP,
                          times_completed INTEGER DEFAULT 0,
                          UNIQUE(user_id, name))''')
            
            c.execute('''CREATE TABLE IF NOT EXISTS workout_logs
                         (id INTEGER PRIMARY KEY AUTOINCREMENT,
                          user_id INTEGER NOT NULL,
                          date TEXT NOT NULL,
                          template_name TEXT,
                          template_id INTEGER,
                          start_time TEXT NOT NULL,
                          end_time TEXT,
                          notes TEXT,
                          total_volume REAL,
                          total_sets INTEGER,
                          session_rpe REAL,
                          calories_burned INTEGER,
                          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                          FOREIGN KEY (template_id) REFERENCES workout_templates(id))''')
            
            c.execute('''CREATE TABLE IF NOT EXISTS set_logs
                         (id INTEGER PRIMARY KEY AUTOINCREMENT,
                          workout_log_id INTEGER NOT NULL,
                          exercise_name TEXT NOT NULL,
                          set_number INTEGER NOT NULL,
                          weight REAL NOT NULL,
                          reps INTEGER NOT NULL,
                          rpe REAL,
                          rest_seconds INTEGER,
                          notes TEXT,
                          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                          FOREIGN KEY (workout_log_id) REFERENCES workout_logs(id) ON DELETE CASCADE)''')
            
            c.execute('''CREATE TABLE IF NOT EXISTS personal_records
                         (id INTEGER PRIMARY KEY AUTOINCREMENT,
                          user_id INTEGER NOT NULL,
                          exercise_name TEXT NOT NULL,
                          weight REAL NOT NULL,
                          reps INTEGER NOT NULL,
                          date TEXT NOT NULL,
                          estimated_1rm REAL NOT NULL,
                          bodyweight REAL,
                          notes TEXT,
                          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
            
            c.execute('''CREATE TABLE IF NOT EXISTS active_sessions
                         (user_id INTEGER PRIMARY KEY,
                          workout_id INTEGER NOT NULL,
                          workout_name TEXT NOT NULL,
                          exercises TEXT NOT NULL,
                          current_exercise_index INTEGER DEFAULT 0,
                          sets_completed TEXT NOT NULL,
                          start_time TIMESTAMP NOT NULL,
                          last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                          notes TEXT,
                          FOREIGN KEY (workout_id) REFERENCES workout_logs(id))''')
            
            c.execute('''CREATE TABLE IF NOT EXISTS exercise_history
                         (id INTEGER PRIMARY KEY AUTOINCREMENT,
                          user_id INTEGER NOT NULL,
                          exercise_name TEXT NOT NULL,
                          date TEXT NOT NULL,
                          avg_weight REAL,
                          total_sets INTEGER,
                          total_reps INTEGER,
                          total_volume REAL,
                          best_set_weight REAL,
                          best_set_reps INTEGER,
                          avg_rpe REAL,
                          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
            
            c.execute('''CREATE TABLE IF NOT EXISTS workout_programs
                         (id INTEGER PRIMARY KEY AUTOINCREMENT,
                          user_id INTEGER NOT NULL,
                          name TEXT NOT NULL,
                          description TEXT,
                          duration_weeks INTEGER,
                          workout_schedule TEXT,
                          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                          UNIQUE(user_id, name))''')
            
            c.execute('''CREATE TABLE IF NOT EXISTS periodization_blocks
                         (id INTEGER PRIMARY KEY AUTOINCREMENT,
                          user_id INTEGER NOT NULL,
                          name TEXT NOT NULL,
                          block_type TEXT NOT NULL,
                          start_date TEXT NOT NULL,
                          end_date TEXT NOT NULL,
                          current_week INTEGER DEFAULT 1,
                          total_weeks INTEGER NOT NULL,
                          notes TEXT,
                          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
            
            # Create indexes
            c.execute("CREATE INDEX IF NOT EXISTS idx_workout_logs_user_date ON workout_logs(user_id, date)")
            c.execute("CREATE INDEX IF NOT EXISTS idx_set_logs_workout_exercise ON set_logs(workout_log_id, exercise_name)")
            c.execute("CREATE INDEX IF NOT EXISTS idx_personal_records_user_exercise ON personal_records(user_id, exercise_name)")
            c.execute("CREATE INDEX IF NOT EXISTS idx_exercise_history_user_exercise_date ON exercise_history(user_id, exercise_name, date)")
            
            # Initialize default exercises
            self._init_default_exercises()
    
    def _init_default_exercises(self):
        """Initialize database with common exercises"""
        exercises = [
            # Push
            ('bench press', 'chest', 'barbell', 1),
            ('incline bench press', 'chest', 'barbell', 1),
            ('dumbbell press', 'chest', 'dumbbell', 1),
            ('dumbbell fly', 'chest', 'dumbbell', 0),
            ('cable fly', 'chest', 'cable', 0),
            ('push up', 'chest', 'bodyweight', 1),
            
            ('overhead press', 'shoulders', 'barbell', 1),
            ('dumbbell shoulder press', 'shoulders', 'dumbbell', 1),
            ('lateral raise', 'shoulders', 'dumbbell', 0),
            ('front raise', 'shoulders', 'dumbbell', 0),
            ('rear delt fly', 'shoulders', 'dumbbell', 0),
            
            ('close grip bench press', 'triceps', 'barbell', 1),
            ('tricep dip', 'triceps', 'bodyweight', 1),
            ('tricep extension', 'triceps', 'dumbbell', 0),
            ('cable tricep pushdown', 'triceps', 'cable', 0),
            
            # Pull
            ('deadlift', 'back', 'barbell', 1),
            ('pull up', 'back', 'bodyweight', 1),
            ('chin up', 'back', 'bodyweight', 1),
            ('barbell row', 'back', 'barbell', 1),
            ('dumbbell row', 'back', 'dumbbell', 1),
            ('cable row', 'back', 'cable', 0),
            ('lat pulldown', 'back', 'cable', 1),
            
            ('barbell curl', 'biceps', 'barbell', 0),
            ('dumbbell curl', 'biceps', 'dumbbell', 0),
            ('hammer curl', 'biceps', 'dumbbell', 0),
            ('preacher curl', 'biceps', 'barbell', 0),
            ('cable curl', 'biceps', 'cable', 0),
            
            # Legs
            ('squat', 'quads', 'barbell', 1),
            ('front squat', 'quads', 'barbell', 1),
            ('leg press', 'quads', 'machine', 1),
            ('lunge', 'quads', 'dumbbell', 1),
            ('leg extension', 'quads', 'machine', 0),
            
            ('romanian deadlift', 'hamstrings', 'barbell', 1),
            ('leg curl', 'hamstrings', 'machine', 0),
            ('good morning', 'hamstrings', 'barbell', 1),
            
            ('calf raise', 'calves', 'machine', 0),
            ('seated calf raise', 'calves', 'machine', 0),
            
            # Core
            ('plank', 'core', 'bodyweight', 0),
            ('crunch', 'core', 'bodyweight', 0),
            ('russian twist', 'core', 'bodyweight', 0),
            ('leg raise', 'core', 'bodyweight', 0),
        ]
        
        with self.get_cursor() as c:
            c.executemany(
                'INSERT OR IGNORE INTO exercises (name, muscle_group, equipment, is_compound) VALUES (?, ?, ?, ?)',
                exercises
            )
    
    # Exercise operations
    def get_exercise(self, name: str) -> Optional[Dict]:
        """Get exercise details"""
        with self.get_cursor() as c:
            c.execute("SELECT * FROM exercises WHERE name = ?", (name.lower(),))
            row = c.fetchone()
            
            if row:
                columns = [col[0] for col in c.description]
                return dict(zip(columns, row))
            return None
    
    def search_exercises(self, query: str, muscle_group: Optional[str] = None) -> List[Dict]:
        """Search exercises by name or muscle group"""
        with self.get_cursor() as c:
            if muscle_group:
                c.execute('''SELECT * FROM exercises 
                             WHERE name LIKE ? AND muscle_group = ?
                             ORDER BY name''',
                          (f"%{query}%", muscle_group))
            else:
                c.execute('''SELECT * FROM exercises 
                             WHERE name LIKE ? OR muscle_group LIKE ?
                             ORDER BY name''',
                          (f"%{query}%", f"%{query}%"))
            
            columns = [col[0] for col in c.description]
            return [dict(zip(columns, row)) for row in c.fetchall()]
    
    # Template operations
    def create_template(self, user_id: int, name: str, day_type: str,
                       exercises: List[Dict], notes: Optional[str] = None) -> int:
        """Create a workout template"""
        with self.get_cursor() as c:
            c.execute('''INSERT INTO workout_templates 
                         (user_id, name, day_type, exercises, notes)
                         VALUES (?, ?, ?, ?, ?)''',
                      (user_id, name, day_type, json.dumps(exercises), notes))
            return c.lastrowid
    
    def get_template(self, user_id: int, name: str) -> Optional[Dict]:
        """Get a workout template by name"""
        with self.get_cursor() as c:
            c.execute('''SELECT * FROM workout_templates 
                         WHERE user_id = ? AND name = ?''',
                      (user_id, name))
            row = c.fetchone()
            
            if row:
                columns = [col[0] for col in c.description]
                template = dict(zip(columns, row))
                template['exercises'] = json.loads(template['exercises'])
                return template
            return None
    
    def get_all_templates(self, user_id: int) -> List[Dict]:
        """Get all templates for a user"""
        with self.get_cursor() as c:
            c.execute('''SELECT * FROM workout_templates 
                         WHERE user_id = ?
                         ORDER BY last_used DESC NULLS LAST, name''',
                      (user_id,))
            
            columns = [col[0] for col in c.description]
            templates = []
            for row in c.fetchall():
                template = dict(zip(columns, row))
                template['exercises'] = json.loads(template['exercises'])
                templates.append(template)
            
            return templates
    
    def update_template(self, user_id: int, template_id: int, **kwargs) -> bool:
        """Update template fields"""
        allowed_fields = ['name', 'day_type', 'exercises', 'notes']
        updates = {k: v for k, v in kwargs.items() if k in allowed_fields}
        
        if not updates:
            return False
        
        # Handle exercises JSON encoding
        if 'exercises' in updates:
            updates['exercises'] = json.dumps(updates['exercises'])
        
        set_clause = ", ".join([f"{k} = ?" for k in updates.keys()])
        values = list(updates.values())
        values.extend([template_id, user_id])
        
        with self.get_cursor() as c:
            c.execute(f'''UPDATE workout_templates 
                          SET {set_clause}
                          WHERE id = ? AND user_id = ?''',
                      values)
            return c.rowcount > 0
    
    def delete_template(self, user_id: int, template_id: int) -> bool:
        """Delete a workout template"""
        with self.get_cursor() as c:
            c.execute("DELETE FROM workout_templates WHERE id = ? AND user_id = ?",
                      (template_id, user_id))
            return c.rowcount > 0
    
    # Workout logging
    def start_workout(self, user_id: int, template_name: str, 
                     template_id: Optional[int] = None) -> int:
        """Start a new workout session"""
        now = datetime.now()
        with self.get_cursor() as c:
            c.execute('''INSERT INTO workout_logs 
                         (user_id, date, template_name, template_id, start_time)
                         VALUES (?, ?, ?, ?, ?)''',
                      (user_id, now.date().isoformat(), template_name,
                       template_id, now.time().strftime("%H:%M")))
            
            # Update template usage
            if template_id:
                c.execute('''UPDATE workout_templates 
                             SET last_used = CURRENT_TIMESTAMP,
                                 times_completed = times_completed + 1
                             WHERE id = ?''',
                          (template_id,))
            
            return c.lastrowid
    
    def end_workout(self, workout_id: int, notes: Optional[str] = None,
                   session_rpe: Optional[float] = None) -> bool:
        """End a workout session"""
        with self.get_cursor() as c:
            # Calculate totals
            c.execute('''SELECT 
                            SUM(weight * reps) as total_volume,
                            COUNT(*) as total_sets
                         FROM set_logs 
                         WHERE workout_log_id = ?''',
                      (workout_id,))
            
            volume, sets = c.fetchone()
            
            # Estimate calories (rough calculation)
            c.execute('''SELECT start_time FROM workout_logs WHERE id = ?''',
                      (workout_id,))
            start_time = c.fetchone()[0]
            
            end_time = datetime.now().time().strftime("%H:%M")
            
            # Calculate duration in minutes
            start_dt = datetime.strptime(start_time, "%H:%M")
            end_dt = datetime.strptime(end_time, "%H:%M")
            duration = (end_dt - start_dt).seconds // 60
            calories = duration * 5  # ~5 cal/min for weight training
            
            c.execute('''UPDATE workout_logs 
                         SET end_time = ?, notes = ?, total_volume = ?,
                             total_sets = ?, session_rpe = ?, calories_burned = ?
                         WHERE id = ?''',
                      (end_time, notes, volume, sets, session_rpe, 
                       calories, workout_id))
            
            return c.rowcount > 0
    
    def log_set(self, workout_id: int, exercise_name: str, set_number: int,
                weight: float, reps: int, rpe: Optional[float] = None,
                rest_seconds: Optional[int] = None, notes: Optional[str] = None) -> int:
        """Log a single set"""
        with self.get_cursor() as c:
            c.execute('''INSERT INTO set_logs 
                         (workout_log_id, exercise_name, set_number, weight, 
                          reps, rpe, rest_seconds, notes)
                         VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                      (workout_id, exercise_name.lower(), set_number, weight,
                       reps, rpe, rest_seconds, notes))
            return c.lastrowid
    
    def get_workout_sets(self, workout_id: int) -> List[Dict]:
        """Get all sets for a workout"""
        with self.get_cursor() as c:
            c.execute('''SELECT * FROM set_logs 
                         WHERE workout_log_id = ?
                         ORDER BY id''',
                      (workout_id,))
            
            columns = [col[0] for col in c.description]
            return [dict(zip(columns, row)) for row in c.fetchall()]
    
    # Personal records
    def check_and_save_pr(self, user_id: int, exercise_name: str, 
                         weight: float, reps: int, bodyweight: Optional[float] = None,
                         notes: Optional[str] = None) -> Optional[int]:
        """Check if this is a PR and save if it is"""
        from ..utils.calculations import calculate_1rm
        
        estimated_1rm = calculate_1rm(weight, reps)
        
        with self.get_cursor() as c:
            # Get current PR
            c.execute('''SELECT MAX(estimated_1rm) FROM personal_records 
                         WHERE user_id = ? AND exercise_name = ?''',
                      (user_id, exercise_name.lower()))
            
            current_pr = c.fetchone()[0]
            
            if current_pr is None or estimated_1rm > current_pr:
                # New PR!
                c.execute('''INSERT INTO personal_records 
                             (user_id, exercise_name, weight, reps, date, 
                              estimated_1rm, bodyweight, notes)
                             VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                          (user_id, exercise_name.lower(), weight, reps,
                           date.today().isoformat(), estimated_1rm, 
                           bodyweight, notes))
                return c.lastrowid
            
            return None
    
    def get_personal_records(self, user_id: int, limit: int = 20) -> List[Dict]:
        """Get all personal records for a user"""
        with self.get_cursor() as c:
            c.execute('''SELECT * FROM personal_records 
                         WHERE user_id = ?
                         ORDER BY estimated_1rm DESC
                         LIMIT ?''',
                      (user_id, limit))
            
            columns = [col[0] for col in c.description]
            return [dict(zip(columns, row)) for row in c.fetchall()]
    
    def get_exercise_pr(self, user_id: int, exercise_name: str) -> Optional[Dict]:
        """Get PR for a specific exercise"""
        with self.get_cursor() as c:
            c.execute('''SELECT * FROM personal_records 
                         WHERE user_id = ? AND exercise_name = ?
                         ORDER BY estimated_1rm DESC
                         LIMIT 1''',
                      (user_id, exercise_name.lower()))
            
            row = c.fetchone()
            if row:
                columns = [col[0] for col in c.description]
                return dict(zip(columns, row))
            return None
    
    # Session management
    def save_session(self, user_id: int, workout_id: int, workout_name: str,
                    exercises: List[Dict], current_index: int, 
                    sets_completed: Dict, start_time: datetime, notes: str = "") -> bool:
        """Save active workout session"""
        with self.get_cursor() as c:
            c.execute('''INSERT OR REPLACE INTO active_sessions 
                         (user_id, workout_id, workout_name, exercises, 
                          current_exercise_index, sets_completed, start_time, notes)
                         VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                      (user_id, workout_id, workout_name, json.dumps(exercises),
                       current_index, json.dumps(sets_completed), 
                       start_time.isoformat(), notes))
            return True
    
    def get_session(self, user_id: int) -> Optional[Dict]:
        """Get active session for user"""
        with self.get_cursor() as c:
            c.execute("SELECT * FROM active_sessions WHERE user_id = ?", (user_id,))
            row = c.fetchone()
            
            if row:
                columns = [col[0] for col in c.description]
                session = dict(zip(columns, row))
                session['exercises'] = json.loads(session['exercises'])
                session['sets_completed'] = json.loads(session['sets_completed'])
                session['start_time'] = datetime.fromisoformat(session['start_time'])
                return session
            return None
    
    def delete_session(self, user_id: int) -> bool:
        """Delete active session"""
        with self.get_cursor() as c:
            c.execute("DELETE FROM active_sessions WHERE user_id = ?", (user_id,))
            return c.rowcount > 0
    
    # Analytics
    def get_exercise_history(self, user_id: int, exercise_name: str, 
                           days: int = 30) -> List[Dict]:
        """Get exercise performance history"""
        with self.get_cursor() as c:
            c.execute('''SELECT 
                            wl.date,
                            AVG(sl.weight) as avg_weight,
                            MAX(sl.weight) as max_weight,
                            SUM(sl.reps) as total_reps,
                            COUNT(*) as total_sets,
                            AVG(sl.rpe) as avg_rpe
                         FROM set_logs sl
                         JOIN workout_logs wl ON sl.workout_log_id = wl.id
                         WHERE wl.user_id = ? 
                         AND sl.exercise_name = ?
                         AND wl.date >= date('now', '-' || ? || ' days')
                         GROUP BY wl.date
                         ORDER BY wl.date''',
                      (user_id, exercise_name.lower(), days))
            
            columns = [col[0] for col in c.description]
            return [dict(zip(columns, row)) for row in c.fetchall()]
    
    def get_workout_history(self, user_id: int, days: int = 30) -> List[Dict]:
        """Get workout history"""
        with self.get_cursor() as c:
            c.execute('''SELECT * FROM workout_logs 
                         WHERE user_id = ? 
                         AND date >= date('now', '-' || ? || ' days')
                         AND end_time IS NOT NULL
                         ORDER BY date DESC, start_time DESC''',
                      (user_id, days))
            
            columns = [col[0] for col in c.description]
            return [dict(zip(columns, row)) for row in c.fetchall()]
    
    def get_volume_by_muscle_group(self, user_id: int, days: int = 7) -> Dict[str, int]:
        """Get training volume by muscle group"""
        with self.get_cursor() as c:
            c.execute('''SELECT 
                            e.muscle_group,
                            COUNT(*) as total_sets,
                            SUM(sl.weight * sl.reps) as total_volume
                         FROM set_logs sl
                         JOIN workout_logs wl ON sl.workout_log_id = wl.id
                         JOIN exercises e ON sl.exercise_name = e.name
                         WHERE wl.user_id = ? 
                         AND wl.date >= date('now', '-' || ? || ' days')
                         GROUP BY e.muscle_group
                         ORDER BY total_sets DESC''',
                      (user_id, days))
            
            return {row[0]: {'sets': row[1], 'volume': row[2]} 
                    for row in c.fetchall()}