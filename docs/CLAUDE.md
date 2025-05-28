# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a comprehensive Health and Fitness Discord bot system with a clean, modular architecture:

1. **Nutrition Bot** - Tracks meals, calories, macros, and nutritional goals
2. **Workout Bot** - Logs workouts, tracks progress, manages training programs

## Architecture

### Directory Structure
```
HealthAndFitness/
├── src/
│   ├── core/           # Core functionality
│   │   └── config.py   # Configuration management
│   ├── models/         # Database models
│   │   ├── base.py     # Base database manager
│   │   ├── nutrition.py # Nutrition database operations
│   │   └── workout.py   # Workout database operations
│   ├── cogs/           # Discord command groups
│   │   ├── nutrition.py          # Basic nutrition commands
│   │   ├── meal_planning.py      # Meal presets and planning
│   │   ├── analytics.py          # Nutrition analytics
│   │   ├── inventory.py          # Food inventory management
│   │   ├── recipes.py            # Recipe management and meal planning
│   │   ├── workout.py            # Basic workout commands
│   │   ├── workout_planning.py   # Workout templates
│   │   └── workout_analytics.py  # Progress tracking
│   └── utils/          # Shared utilities
│       ├── calculations.py   # Fitness calculations
│       ├── formatters.py     # Display formatting
│       ├── validators.py     # Input validation
│       ├── converters.py     # Unit conversions
│       ├── embed_builder.py  # Discord embed creation
│       └── user_preferences.py # User settings
├── data/               # Database files
├── logs/               # Log files
├── backups/            # Automatic backups
├── nutrition_bot.py    # Nutrition bot entry point
├── workout_bot.py      # Workout bot entry point
├── run_bots.py        # Bot manager for running both
└── setup.py           # Setup script
```

### Database Schema

#### Nutrition Database (`data/nutrition.db`)
- **meals** - Food intake logs with full nutrition data
- **meal_schedule** - Scheduled meal reminders
- **user_stats** - User profiles and goals
- **weight_log** - Weight and body composition tracking
- **meal_presets** - Saved meals for quick logging
- **user_preferences** - User settings (units, timezone, etc.)
- **inventory** - Food inventory tracking with quantities and expiration dates
- **premade_recipes** - System-provided recipe database
- **user_recipes** - User-created custom recipes
- **recipe_ingredients** - Ingredient lists for recipes
- **recipe_uses** - Tracks recipe usage history

#### Workout Database (`data/workout.db`)
- **exercises** - Exercise database
- **workout_templates** - Reusable workout plans
- **workout_logs** - Workout session tracking
- **set_logs** - Individual set data
- **personal_records** - PR tracking
- **active_sessions** - Persistent workout sessions
- **exercise_history** - Aggregated performance data
- **periodization_blocks** - Training phase management

### Key Design Patterns

1. **Cog-based Architecture**: Commands are organized into cogs (categories) for better organization
2. **Database Abstraction**: All DB operations go through model classes
3. **Validation Layer**: Input validation happens before any database operations
4. **User Preferences**: Metric/imperial units, timezone support
5. **Session Persistence**: Workout sessions survive bot restarts

## Common Development Tasks

### Running the Bots
```bash
# First time setup
python setup.py

# Run both bots
python run_bots.py

# Or use shortcuts
./start         # Unix/Mac
start.cmd       # Windows

# Run individual bots
python nutrition_bot.py
python workout_bot.py
```

### Adding New Commands

1. **Create/modify appropriate cog** in `src/cogs/`
2. **Add command method** with `@commands.command()` decorator
3. **Use validation** from `src/utils/validators.py`
4. **Use database models** from `src/models/`
5. **Use EmbedBuilder** for consistent responses

Example:
```python
@commands.command(name='mycommand')
async def my_command(self, ctx, arg: int):
    # Validate
    valid, error = validate_positive(arg)
    if not valid:
        await ctx.send(embed=EmbedBuilder.error("Invalid input", error))
        return
    
    # Database operation
    result = self.db.some_operation(ctx.author.id, arg)
    
    # Response
    embed = EmbedBuilder.success("Success!", f"Processed: {result}")
    await ctx.send(embed=embed)
```

### Database Operations

Always use the model classes:
```python
# Good
user_stats = self.db.get_user_stats(user_id)

# Bad - Don't use raw SQL in cogs
with db.get_cursor() as c:
    c.execute("SELECT * FROM user_stats...")
```

### Testing Commands
1. Start bots with `python run_bots.py`
2. Use interactive shell commands:
   - `status` - Check bot status
   - `logs` - View recent logs
   - `restart nutrition` - Restart specific bot
3. Test in Discord with appropriate prefix (default: `!`)

## Important Implementation Details

### Configuration
- All config in `src/core/config.py` and `.env`
- Databases stored in `data/` directory
- Logs stored in `logs/` directory
- Automatic backups in `backups/` directory

### Error Handling
- Global error handler in main bot classes
- Command-specific validation before operations
- User-friendly error messages via EmbedBuilder

### Performance Considerations
- Database indexes on frequently queried columns
- Matplotlib figures generated in memory (no temp files)
- Connection pooling through context managers
- Efficient batch operations where possible

### Security
- Bot tokens in `.env` (never commit!)
- Input validation on all user commands
- User ownership checks on data operations
- SQL injection prevention through parameterized queries

## Maintenance

### Adding Features
1. Identify appropriate cog or create new one
2. Add database schema if needed (update model's `init_db`)
3. Implement command with proper validation
4. Test thoroughly with edge cases

### Debugging
- Check `logs/` directory for detailed logs
- Use `DEBUG_MODE=true` in `.env` for verbose output
- Interactive shell in `run_bots.py` for live debugging

### Backups
- Automatic backups enabled by default
- Manual backup: `backup` command in bot manager
- Backup files in `backups/` with timestamps

## Feature Documentation

### Inventory Management System
The nutrition bot includes a comprehensive inventory management system:

**Commands:**
- `!add_inventory <item> <quantity> [unit] [expiry_date]` - Add items to inventory
- `!inventory` - View current inventory with quantities and expiration dates
- `!use_inventory <item> <quantity> [unit]` - Manually use inventory items
- `!remove_inventory <item>` - Remove items from inventory
- `!expiring [days]` - View items expiring soon (default: 7 days)

**Features:**
- Automatic inventory deduction when logging meals
- Smart unit matching and conversion
- Expiration date tracking and alerts
- Low stock warnings
- Integration with recipe system for ingredient availability checking

### Recipe and Meal Planning System
A comprehensive recipe management system with both premade and custom recipes:

**Recipe Commands:**
- `!recipes` - Browse available recipes (both premade and custom)
- `!recipe <name>` - View detailed recipe information
- `!add_recipe` - Interactive custom recipe creation
- `!cook <recipe_name> [servings]` - Cook a recipe and log nutrition
- `!can_make` - Show recipes you can make with current inventory
- `!missing <recipe_name>` - Show missing ingredients for a recipe
- `!delete_recipe <name>` - Delete a custom recipe
- `!search_recipes <ingredient>` - Find recipes containing an ingredient

**Premade Recipes:**
The system includes 50+ professionally crafted recipes covering:
- Breakfast options (smoothies, oatmeal, eggs, etc.)
- Lunch ideas (salads, sandwiches, bowls)
- Dinner recipes (stir-fries, curries, pasta, etc.)
- Snacks and desserts
- Various dietary preferences (vegetarian, vegan, low-carb, etc.)

**Features:**
- Automatic inventory checking and deduction
- Nutritional calculation based on ingredients
- Serving size adjustments
- Recipe popularity tracking
- Smart ingredient matching with units
- Interactive recipe builder with validation

### Integration Features

**Nutrition-Inventory Integration:**
- When logging meals with `!log`, the system automatically:
  - Searches for matching inventory items
  - Deducts appropriate quantities
  - Warns about low stock
  - Suggests similar items if exact match not found

**Recipe-Inventory Integration:**
- `!can_make` command shows all recipes you have ingredients for
- `!cook` command automatically deducts all ingredients from inventory
- Missing ingredient alerts before cooking
- Partial ingredient availability warnings

**Smart Features:**
- Fuzzy matching for ingredient names
- Unit conversion and compatibility checking
- Expiration date consideration in recipe suggestions
- Nutritional goal integration with meal planning