"""
Food inventory and meal planning database models
"""

from datetime import datetime, date, timedelta
from typing import Optional, List, Dict, Tuple
import json
from .base import DatabaseManager


class InventoryDatabase(DatabaseManager):
    """Database operations for food inventory and meal planning"""
    
    def init_db(self):
        """Initialize inventory and meal planning tables"""
        with self.get_cursor() as c:
            # Food inventory
            c.execute('''CREATE TABLE IF NOT EXISTS food_inventory
                         (id INTEGER PRIMARY KEY AUTOINCREMENT,
                          user_id INTEGER NOT NULL,
                          food_name TEXT NOT NULL,
                          quantity REAL NOT NULL,
                          unit TEXT NOT NULL,
                          location TEXT DEFAULT 'pantry',
                          expiration_date TEXT,
                          purchase_date TEXT,
                          cost REAL,
                          notes TEXT,
                          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                          updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
            
            # Recipes
            c.execute('''CREATE TABLE IF NOT EXISTS recipes
                         (id INTEGER PRIMARY KEY AUTOINCREMENT,
                          user_id INTEGER NOT NULL,
                          name TEXT NOT NULL,
                          description TEXT,
                          servings INTEGER DEFAULT 1,
                          prep_time INTEGER,
                          cook_time INTEGER,
                          calories_per_serving INTEGER,
                          protein_per_serving REAL,
                          instructions TEXT,
                          tags TEXT,
                          is_public INTEGER DEFAULT 0,
                          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                          UNIQUE(user_id, name))''')
            
            # Recipe ingredients
            c.execute('''CREATE TABLE IF NOT EXISTS recipe_ingredients
                         (id INTEGER PRIMARY KEY AUTOINCREMENT,
                          recipe_id INTEGER NOT NULL,
                          food_name TEXT NOT NULL,
                          quantity REAL NOT NULL,
                          unit TEXT NOT NULL,
                          is_optional INTEGER DEFAULT 0,
                          notes TEXT,
                          FOREIGN KEY (recipe_id) REFERENCES recipes(id) ON DELETE CASCADE)''')
            
            # Meal plans
            c.execute('''CREATE TABLE IF NOT EXISTS meal_plans
                         (id INTEGER PRIMARY KEY AUTOINCREMENT,
                          user_id INTEGER NOT NULL,
                          recipe_id INTEGER NOT NULL,
                          planned_date TEXT NOT NULL,
                          meal_type TEXT DEFAULT 'dinner',
                          servings INTEGER DEFAULT 1,
                          completed INTEGER DEFAULT 0,
                          notes TEXT,
                          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                          FOREIGN KEY (recipe_id) REFERENCES recipes(id))''')
            
            # Shopping lists
            c.execute('''CREATE TABLE IF NOT EXISTS shopping_lists
                         (id INTEGER PRIMARY KEY AUTOINCREMENT,
                          user_id INTEGER NOT NULL,
                          name TEXT,
                          created_date TEXT NOT NULL,
                          completed INTEGER DEFAULT 0,
                          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
            
            # Shopping list items
            c.execute('''CREATE TABLE IF NOT EXISTS shopping_list_items
                         (id INTEGER PRIMARY KEY AUTOINCREMENT,
                          list_id INTEGER NOT NULL,
                          food_name TEXT NOT NULL,
                          quantity REAL NOT NULL,
                          unit TEXT NOT NULL,
                          checked INTEGER DEFAULT 0,
                          category TEXT,
                          estimated_cost REAL,
                          notes TEXT,
                          FOREIGN KEY (list_id) REFERENCES shopping_lists(id) ON DELETE CASCADE)''')
            
            # Create indexes
            c.execute("CREATE INDEX IF NOT EXISTS idx_inventory_user_food ON food_inventory(user_id, food_name)")
            c.execute("CREATE INDEX IF NOT EXISTS idx_recipes_user ON recipes(user_id)")
            c.execute("CREATE INDEX IF NOT EXISTS idx_meal_plans_user_date ON meal_plans(user_id, planned_date)")
            
            # Create helpful views
            c.execute('''CREATE VIEW IF NOT EXISTS recipe_availability AS
                         SELECT r.*, 
                                COUNT(DISTINCT ri.food_name) as total_ingredients,
                                COUNT(DISTINCT CASE 
                                    WHEN fi.quantity >= ri.quantity THEN ri.food_name 
                                END) as available_ingredients
                         FROM recipes r
                         JOIN recipe_ingredients ri ON r.id = ri.recipe_id
                         LEFT JOIN food_inventory fi ON ri.food_name = fi.food_name 
                                                      AND r.user_id = fi.user_id
                         GROUP BY r.id''')
    
    # Inventory management
    def add_inventory_item(self, user_id: int, food_name: str, quantity: float, 
                          unit: str, location: str = 'pantry', 
                          expiration_date: Optional[str] = None,
                          cost: Optional[float] = None) -> int:
        """Add or update food inventory item"""
        with self.get_cursor() as c:
            # Check if item exists
            c.execute('''SELECT id, quantity FROM food_inventory 
                         WHERE user_id = ? AND food_name = ? AND location = ?''',
                      (user_id, food_name.lower(), location))
            existing = c.fetchone()
            
            if existing:
                # Update quantity
                new_quantity = existing[1] + quantity
                c.execute('''UPDATE food_inventory 
                             SET quantity = ?, updated_at = CURRENT_TIMESTAMP,
                                 expiration_date = COALESCE(?, expiration_date)
                             WHERE id = ?''',
                          (new_quantity, expiration_date, existing[0]))
                return existing[0]
            else:
                # Insert new
                c.execute('''INSERT INTO food_inventory 
                             (user_id, food_name, quantity, unit, location, 
                              expiration_date, purchase_date, cost)
                             VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                          (user_id, food_name.lower(), quantity, unit, location,
                           expiration_date, date.today().isoformat(), cost))
                return c.lastrowid
    
    def update_inventory_quantity(self, user_id: int, food_name: str, 
                                 new_quantity: float, location: Optional[str] = None) -> bool:
        """Update inventory quantity (set to 0 to remove)"""
        with self.get_cursor() as c:
            if location:
                c.execute('''UPDATE food_inventory 
                             SET quantity = ?, updated_at = CURRENT_TIMESTAMP
                             WHERE user_id = ? AND food_name = ? AND location = ?''',
                          (new_quantity, user_id, food_name.lower(), location))
            else:
                c.execute('''UPDATE food_inventory 
                             SET quantity = ?, updated_at = CURRENT_TIMESTAMP
                             WHERE user_id = ? AND food_name = ?''',
                          (new_quantity, user_id, food_name.lower()))
            
            # Delete if quantity is 0
            if new_quantity == 0:
                c.execute('''DELETE FROM food_inventory 
                             WHERE user_id = ? AND food_name = ? AND quantity = 0''',
                          (user_id, food_name.lower()))
            
            return c.rowcount > 0
    
    def get_inventory(self, user_id: int, location: Optional[str] = None,
                     include_expired: bool = False) -> List[Dict]:
        """Get user's food inventory"""
        with self.get_cursor() as c:
            query = '''SELECT * FROM food_inventory WHERE user_id = ?'''
            params = [user_id]
            
            if location:
                query += ' AND location = ?'
                params.append(location)
            
            if not include_expired:
                query += ' AND (expiration_date IS NULL OR expiration_date > date("now"))'
            
            query += ' ORDER BY food_name'
            
            c.execute(query, params)
            columns = [col[0] for col in c.description]
            return [dict(zip(columns, row)) for row in c.fetchall()]
    
    def get_expiring_items(self, user_id: int, days: int = 7) -> List[Dict]:
        """Get items expiring within specified days"""
        with self.get_cursor() as c:
            c.execute('''SELECT * FROM food_inventory 
                         WHERE user_id = ? 
                         AND expiration_date IS NOT NULL
                         AND expiration_date <= date("now", "+" || ? || " days")
                         AND expiration_date > date("now")
                         ORDER BY expiration_date''',
                      (user_id, days))
            
            columns = [col[0] for col in c.description]
            return [dict(zip(columns, row)) for row in c.fetchall()]
    
    # Recipe management
    def create_recipe(self, user_id: int, name: str, ingredients: List[Dict],
                     servings: int = 1, description: Optional[str] = None,
                     instructions: Optional[str] = None,
                     prep_time: Optional[int] = None, cook_time: Optional[int] = None,
                     calories: Optional[int] = None, protein: Optional[float] = None,
                     tags: Optional[List[str]] = None) -> int:
        """Create a new recipe with ingredients"""
        with self.get_cursor() as c:
            # Insert recipe
            c.execute('''INSERT INTO recipes 
                         (user_id, name, description, servings, prep_time, cook_time,
                          calories_per_serving, protein_per_serving, instructions, tags)
                         VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                      (user_id, name, description, servings, prep_time, cook_time,
                       calories, protein, instructions, 
                       json.dumps(tags) if tags else None))
            
            recipe_id = c.lastrowid
            
            # Insert ingredients
            for ingredient in ingredients:
                c.execute('''INSERT INTO recipe_ingredients 
                             (recipe_id, food_name, quantity, unit, is_optional, notes)
                             VALUES (?, ?, ?, ?, ?, ?)''',
                          (recipe_id, ingredient['food_name'].lower(), 
                           ingredient['quantity'], ingredient['unit'],
                           ingredient.get('is_optional', 0),
                           ingredient.get('notes')))
            
            return recipe_id
    
    def get_recipe(self, recipe_id: int) -> Optional[Dict]:
        """Get recipe with ingredients"""
        with self.get_cursor() as c:
            # Get recipe
            c.execute('SELECT * FROM recipes WHERE id = ?', (recipe_id,))
            recipe_row = c.fetchone()
            
            if not recipe_row:
                return None
            
            columns = [col[0] for col in c.description]
            recipe = dict(zip(columns, recipe_row))
            
            # Get ingredients
            c.execute('''SELECT food_name, quantity, unit, is_optional, notes
                         FROM recipe_ingredients WHERE recipe_id = ?''',
                      (recipe_id,))
            
            recipe['ingredients'] = []
            for row in c.fetchall():
                recipe['ingredients'].append({
                    'food_name': row[0],
                    'quantity': row[1],
                    'unit': row[2],
                    'is_optional': bool(row[3]),
                    'notes': row[4]
                })
            
            # Parse tags
            if recipe.get('tags'):
                recipe['tags'] = json.loads(recipe['tags'])
            
            return recipe
    
    def get_user_recipes(self, user_id: int, tags: Optional[List[str]] = None) -> List[Dict]:
        """Get all recipes for a user, optionally filtered by tags"""
        with self.get_cursor() as c:
            query = 'SELECT * FROM recipes WHERE user_id = ?'
            params = [user_id]
            
            if tags:
                # Filter by tags (requires JSON support)
                tag_conditions = []
                for tag in tags:
                    tag_conditions.append(f"tags LIKE '%\"{tag}\"%'")
                query += f' AND ({" OR ".join(tag_conditions)})'
            
            query += ' ORDER BY name'
            
            c.execute(query, params)
            columns = [col[0] for col in c.description]
            recipes = []
            
            for row in c.fetchall():
                recipe = dict(zip(columns, row))
                if recipe.get('tags'):
                    recipe['tags'] = json.loads(recipe['tags'])
                recipes.append(recipe)
            
            return recipes
    
    def check_recipe_availability(self, user_id: int, recipe_id: int) -> Dict:
        """Check if user has ingredients for a recipe"""
        with self.get_cursor() as c:
            # Get recipe ingredients
            c.execute('''SELECT ri.food_name, ri.quantity, ri.unit, ri.is_optional,
                                fi.quantity as available_quantity
                         FROM recipe_ingredients ri
                         LEFT JOIN food_inventory fi ON ri.food_name = fi.food_name 
                                                      AND fi.user_id = ?
                         WHERE ri.recipe_id = ?''',
                      (user_id, recipe_id))
            
            ingredients = []
            missing = []
            partial = []
            
            for row in c.fetchall():
                ingredient = {
                    'food_name': row[0],
                    'required': row[1],
                    'unit': row[2],
                    'is_optional': bool(row[3]),
                    'available': row[4] or 0
                }
                
                ingredients.append(ingredient)
                
                if not ingredient['is_optional']:
                    if ingredient['available'] == 0:
                        missing.append(ingredient)
                    elif ingredient['available'] < ingredient['required']:
                        ingredient['needed'] = ingredient['required'] - ingredient['available']
                        partial.append(ingredient)
            
            return {
                'can_make': len(missing) == 0 and len(partial) == 0,
                'ingredients': ingredients,
                'missing': missing,
                'partial': partial
            }
    
    def get_available_recipes(self, user_id: int) -> List[Dict]:
        """Get all recipes user can make with current inventory"""
        with self.get_cursor() as c:
            c.execute('''SELECT r.*, 
                                COUNT(DISTINCT ri.food_name) as total_ingredients,
                                COUNT(DISTINCT CASE 
                                    WHEN fi.quantity >= ri.quantity THEN ri.food_name 
                                END) as available_ingredients
                         FROM recipes r
                         JOIN recipe_ingredients ri ON r.id = ri.recipe_id
                         LEFT JOIN food_inventory fi ON ri.food_name = fi.food_name 
                                                      AND r.user_id = fi.user_id
                                                      AND ri.is_optional = 0
                         WHERE r.user_id = ?
                         GROUP BY r.id
                         HAVING available_ingredients = COUNT(DISTINCT CASE 
                                                            WHEN ri.is_optional = 0 
                                                            THEN ri.food_name 
                                                         END)''',
                      (user_id,))
            
            columns = [col[0] for col in c.description]
            recipes = []
            
            for row in c.fetchall():
                recipe = dict(zip(columns, row))
                if recipe.get('tags'):
                    recipe['tags'] = json.loads(recipe['tags'])
                recipes.append(recipe)
            
            return recipes
    
    # Meal planning
    def add_meal_plan(self, user_id: int, recipe_id: int, planned_date: str,
                     meal_type: str = 'dinner', servings: int = 1) -> int:
        """Add a meal to the plan"""
        with self.get_cursor() as c:
            c.execute('''INSERT INTO meal_plans 
                         (user_id, recipe_id, planned_date, meal_type, servings)
                         VALUES (?, ?, ?, ?, ?)''',
                      (user_id, recipe_id, planned_date, meal_type, servings))
            return c.lastrowid
    
    def get_meal_plan(self, user_id: int, start_date: str, end_date: str) -> List[Dict]:
        """Get meal plan for date range"""
        with self.get_cursor() as c:
            c.execute('''SELECT mp.*, r.name as recipe_name, r.description,
                                r.calories_per_serving, r.protein_per_serving
                         FROM meal_plans mp
                         JOIN recipes r ON mp.recipe_id = r.id
                         WHERE mp.user_id = ? 
                         AND mp.planned_date >= ? 
                         AND mp.planned_date <= ?
                         ORDER BY mp.planned_date, 
                                  CASE mp.meal_type
                                      WHEN 'breakfast' THEN 1
                                      WHEN 'lunch' THEN 2
                                      WHEN 'dinner' THEN 3
                                      ELSE 4
                                  END''',
                      (user_id, start_date, end_date))
            
            columns = [col[0] for col in c.description]
            return [dict(zip(columns, row)) for row in c.fetchall()]
    
    def mark_meal_completed(self, user_id: int, meal_plan_id: int) -> bool:
        """Mark a planned meal as completed"""
        with self.get_cursor() as c:
            c.execute('''UPDATE meal_plans SET completed = 1 
                         WHERE id = ? AND user_id = ?''',
                      (meal_plan_id, user_id))
            return c.rowcount > 0
    
    # Shopping list generation
    def generate_shopping_list(self, user_id: int, start_date: str, end_date: str,
                              name: Optional[str] = None) -> int:
        """Generate shopping list based on meal plan"""
        with self.get_cursor() as c:
            # Create shopping list
            if not name:
                name = f"Shopping List {start_date}"
            
            c.execute('''INSERT INTO shopping_lists 
                         (user_id, name, created_date)
                         VALUES (?, ?, ?)''',
                      (user_id, name, date.today().isoformat()))
            
            list_id = c.lastrowid
            
            # Get all ingredients needed for meal plan
            c.execute('''SELECT ri.food_name, 
                                SUM(ri.quantity * mp.servings) as total_needed,
                                ri.unit,
                                COALESCE(fi.quantity, 0) as available
                         FROM meal_plans mp
                         JOIN recipe_ingredients ri ON mp.recipe_id = ri.recipe_id
                         LEFT JOIN food_inventory fi ON ri.food_name = fi.food_name 
                                                      AND fi.user_id = mp.user_id
                         WHERE mp.user_id = ? 
                         AND mp.planned_date >= ? 
                         AND mp.planned_date <= ?
                         AND mp.completed = 0
                         AND ri.is_optional = 0
                         GROUP BY ri.food_name, ri.unit''',
                      (user_id, start_date, end_date))
            
            # Add items to shopping list
            for row in c.fetchall():
                food_name, total_needed, unit, available = row
                
                if total_needed > available:
                    quantity_to_buy = total_needed - available
                    
                    # Categorize food items
                    category = self._categorize_food(food_name)
                    
                    c.execute('''INSERT INTO shopping_list_items 
                                 (list_id, food_name, quantity, unit, category)
                                 VALUES (?, ?, ?, ?, ?)''',
                              (list_id, food_name, quantity_to_buy, unit, category))
            
            return list_id
    
    def get_shopping_list(self, list_id: int) -> Optional[Dict]:
        """Get shopping list with items"""
        with self.get_cursor() as c:
            # Get list
            c.execute('SELECT * FROM shopping_lists WHERE id = ?', (list_id,))
            list_row = c.fetchone()
            
            if not list_row:
                return None
            
            columns = [col[0] for col in c.description]
            shopping_list = dict(zip(columns, list_row))
            
            # Get items grouped by category
            c.execute('''SELECT * FROM shopping_list_items 
                         WHERE list_id = ?
                         ORDER BY category, food_name''',
                      (list_id,))
            
            items_columns = [col[0] for col in c.description]
            shopping_list['items'] = [dict(zip(items_columns, row)) 
                                     for row in c.fetchall()]
            
            return shopping_list
    
    def check_shopping_item(self, item_id: int, checked: bool = True) -> bool:
        """Mark shopping list item as checked/unchecked"""
        with self.get_cursor() as c:
            c.execute('''UPDATE shopping_list_items 
                         SET checked = ? 
                         WHERE id = ?''',
                      (int(checked), item_id))
            return c.rowcount > 0
    
    def _categorize_food(self, food_name: str) -> str:
        """Categorize food items for shopping list organization"""
        categories = {
            'produce': ['apple', 'banana', 'lettuce', 'tomato', 'onion', 'garlic',
                       'carrot', 'celery', 'pepper', 'broccoli', 'spinach'],
            'meat': ['chicken', 'beef', 'pork', 'fish', 'salmon', 'turkey'],
            'dairy': ['milk', 'cheese', 'yogurt', 'butter', 'cream', 'eggs'],
            'grains': ['rice', 'pasta', 'bread', 'flour', 'oats', 'quinoa'],
            'pantry': ['oil', 'salt', 'pepper', 'sugar', 'sauce', 'spice'],
            'frozen': ['frozen', 'ice cream'],
            'beverages': ['juice', 'soda', 'coffee', 'tea']
        }
        
        food_lower = food_name.lower()
        for category, keywords in categories.items():
            for keyword in keywords:
                if keyword in food_lower:
                    return category
        
        return 'other'