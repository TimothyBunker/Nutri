# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a comprehensive Health and Fitness Discord bot system with a clean, modular architecture:

1. **Nutrition Bot** - Tracks meals, calories, macros, nutritional goals, inventory management, and recipe planning
2. **Workout Bot** - Logs workouts, tracks progress, manages training programs with periodization support

## Technical Requirements

- **Python**: 3.8+ required (uses asyncio, type hints)
- **Key Dependencies**:
  - `discord.py>=2.3.0` - Discord bot framework
  - `matplotlib>=3.7.0` - Chart generation
  - `numpy>=1.24.0` - Numerical calculations
  - `python-dotenv>=1.0.0` - Environment configuration
  - `pytz>=2023.3` - Timezone support
  - `APScheduler>=3.10.0` - Scheduled tasks
  - `aiofiles>=23.0.0` - Async file operations

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
python tools/setup.py

# Install dependencies
pip install -r requirements.txt

# Run both bots (interactive mode with commands)
python run_bots.py

# Run both bots (background mode)
python run_bots.py --background

# Or use platform-specific shortcuts
./start.sh      # Unix/Mac
start.bat       # Windows
python launcher.py  # Cross-platform interactive launcher

# Run individual bots
python nutrition_bot.py
python workout_bot.py
```

### Bot Manager Commands
When running `python run_bots.py` in interactive mode:
- `status` - Show bot status
- `logs [lines]` - View recent logs (default: 20 lines)
- `restart [bot]` - Restart specific bot or all bots
- `stop [bot]` - Stop specific bot or all bots
- `start [bot]` - Start specific bot or all bots
- `backup` - Create manual database backups
- `quit` or `exit` - Exit manager

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

### Environment Variables (.env)
Required:
- `NUTRITION_BOT_TOKEN` - Discord bot token for nutrition bot
- `WORKOUT_BOT_TOKEN` - Discord bot token for workout bot

Optional:
- `BOT_PREFIX` - Command prefix (default: !)
- `LOG_LEVEL` - Logging level (default: INFO)
- `DEBUG_MODE` - Enable debug mode (default: false)
- `DEFAULT_TIMEZONE` - Default timezone (default: UTC)
- `DEFAULT_UNIT_SYSTEM` - Default units (default: imperial)
- `ENABLE_AUTO_BACKUP` - Enable automatic backups (default: true)
- `BACKUP_INTERVAL_HOURS` - Backup interval (default: 24)

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

### Unit Testing
Currently no automated tests. When implementing tests:
1. Create `tests/` directory  
2. Use `pytest` for test framework
3. Mock Discord.py components
4. Test database operations with in-memory SQLite
5. Run tests: `pytest tests/`

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

## Important Notes & Common Gotchas

### Database Considerations
- SQLite databases are in `data/` directory, not project root
- Automatic backups run every 24 hours (configurable)
- Database connections use context managers - always use model classes
- Indexes exist on frequently queried columns (user_id, date, etc.)

### Discord.py Specifics
- Commands use `@commands.command()` decorator
- Cogs must be loaded in main bot files
- Bot requires appropriate Discord permissions (Send Messages, Embed Links, Attach Files)
- Rate limiting is implemented (30 commands/minute by default)

### Common Issues
- **"No module named 'src'"**: Ensure running from project root
- **Bot not responding**: Check prefix in .env (default: !)
- **Database locked**: Only one process should access each database
- **Missing dependencies**: Run `pip install -r requirements.txt`

### Code Style Guidelines
- Use type hints for function parameters and returns
- Follow existing patterns for validation and error handling
- Use EmbedBuilder for all Discord responses
- Keep database operations in model classes only
- Use logging instead of print statements