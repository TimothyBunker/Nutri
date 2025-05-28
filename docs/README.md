# Health & Fitness Discord Bot

A comprehensive Discord bot system for tracking nutrition and workouts with advanced features for scalability and user experience.

## Features

### Nutrition Bot
- 📊 Track calories, protein, carbs, and fats
- 🎯 Set and monitor daily targets
- 📈 Generate progress charts
- ⏰ Meal reminders
- 🔄 Edit and delete logged meals
- 💾 Save meal presets for quick logging
- 🌍 Metric/Imperial unit support

### Workout Bot
- 💪 Create custom workout templates
- 📝 Log sets with weight, reps, and RPE
- 🏆 Track personal records
- 📊 Analyze training volume
- 🔄 Periodization blocks
- 📈 Progress tracking

## Quick Start

### 1. Installation

```bash
# Clone the repository
git clone <your-repo-url>
cd HealthAndFitness

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

1. Copy the example environment file:
```bash
cp .env.example .env
```

2. Edit `.env` and add your Discord bot tokens:
```
NUTRITION_BOT_TOKEN=your_nutrition_bot_token_here
WORKOUT_BOT_TOKEN=your_workout_bot_token_here
```

3. (Optional) Customize other settings in `.env`

### 3. Run the Bots

```bash
# Run the improved nutrition bot
python nutri_improved.py

# Run the workout bot (in a separate terminal)
python worko.py
```

## Usage Examples

### Nutrition Commands

```
# Initial setup (Imperial)
!setup 5'10" 180 175 2800 180

# Initial setup (Metric)
!setup 178cm 82 79 2800 180

# Log a meal
!log "chicken breast" 165 31 0 3.6

# Save a preset
!preset chicken "Grilled chicken breast" 165 31 0 3.6

# Quick log with preset
!quick chicken
!quick chicken 1.5  # 1.5 servings

# Edit a meal
!edit_meal 123 calories 200

# View today's summary
!today

# Change units
!units metric
```

### Workout Commands

```
# Create workout template
!create_workout "Push Day" push

# Add exercises
!add_exercise "Push Day" "bench press" 3 8-10

# Start workout
!start_workout Push Day

# Log sets
!log_set 1 "bench press" 185 8
!w bench 185 8  # Quick log shortcut

# View progress
!progress "bench press"

# Check PRs
!prs
```

## Key Improvements

### 1. **Reduced Redundancy**
- Shared utilities module (`utils.py`)
- Centralized database management
- Consistent embed formatting

### 2. **Better Scalability**
- User preferences (units, timezone)
- Input validation
- Rate limiting
- Auto-backups

### 3. **Enhanced User Experience**
- Command aliases for common operations
- Edit/delete functionality
- Meal presets
- Progress bars in summaries
- Better error messages

### 4. **Security**
- Environment variables for sensitive data
- Input validation
- User ownership checks

## Development

### Project Structure
```
HealthAndFitness/
├── nutri_improved.py    # Enhanced nutrition bot
├── worko.py            # Workout tracking bot
├── utils.py            # Shared utilities
├── config.py           # Configuration management
├── .env                # Environment variables (create from .env.example)
├── requirements.txt    # Python dependencies
└── README.md          # This file
```

### Adding New Features

1. **New Commands**: Add to the appropriate bot file with validation
2. **Database Changes**: Update `init_db()` function
3. **Shared Functionality**: Add to `utils.py`
4. **Configuration**: Add new settings to `config.py` and `.env.example`

### Best Practices

- Always validate user input
- Use the shared `DatabaseManager` for database operations
- Use `EmbedBuilder` for consistent message formatting
- Add command aliases for better UX
- Include helpful error messages

## Troubleshooting

### Bot won't start
- Check that `.env` file exists with valid tokens
- Ensure all dependencies are installed
- Check console for error messages

### Commands not working
- Verify bot has proper permissions in your Discord server
- Check command syntax and aliases
- Ensure database files have write permissions

### Database issues
- Backups are stored in `backups/` directory
- Delete `.db` files to reset (data will be lost)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes with proper validation
4. Test thoroughly
5. Submit a pull request

## License

[Your chosen license]

## Support

For issues or questions:
- Check existing issues on GitHub
- Join our Discord server: [invite link]
- Contact: [your contact info]