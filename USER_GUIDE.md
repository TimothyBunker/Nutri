# Health & Fitness Bot - Complete User Guide

## Table of Contents

1. [Getting Started](#getting-started)
2. [Nutrition Bot Commands](#nutrition-bot-commands)
3. [Workout Bot Commands](#workout-bot-commands)
4. [Inventory & Meal Planning Commands](#inventory--meal-planning-commands)
5. [Analytics & Progress Tracking](#analytics--progress-tracking)
6. [Tips & Best Practices](#tips--best-practices)
7. [Troubleshooting](#troubleshooting)

---

## Getting Started

### Initial Setup

1. **Start the bots** using one of these methods:
   - Windows: Double-click `start.bat`
   - Mac/Linux: Run `./start.sh`
   - Manual: Run `python launcher.py`

2. **Default prefix**: All commands start with `!`

3. **First-time users** should:
   - Set daily targets: `!target calories 2000` and `!target protein 150`
   - Load premade recipes: `!load_recipes`
   - Create your first workout: `!create_workout "Push Day" push`

---

## Nutrition Bot Commands

### Basic Food Logging

#### `!log` / `!l` / `!food` / `!meal`
Log a meal with nutrition information.

**Format**: `!log "food name" calories protein carbs fats`

**Examples**:
```
!log "chicken breast" 165 31 0 3.6
!log "protein shake" 150 30 5 2
!log "brown rice" 220 5 45 2
```

**Smart Features**:
- If the food matches a recipe in your collection, you'll be prompted to deduct ingredients
- Automatically shows daily progress after logging

#### `!today` / `!t` / `!summary`
Show today's nutrition summary with all meals and totals.

**Example**: `!today`

**Shows**:
- List of all meals logged today with IDs
- Total calories and macros
- Progress bars for daily targets
- Macro percentage breakdown

#### `!edit`
Edit a previously logged meal.

**Format**: `!edit meal_id field value`

**Fields**: calories, protein, carbs, fats

**Example**: `!edit 123 calories 200`

#### `!delete` / `!remove`
Delete a logged meal.

**Format**: `!delete meal_id`

**Example**: `!delete 123`

#### `!undo` / `!u`
Delete the last logged meal of the day.

**Example**: `!undo`

### Recipe Integration

#### `!track_recipe` / `!tr` / `!recipe_log`
Track a recipe from your collection and automatically deduct ingredients from inventory.

**Format**: `!track_recipe recipe_name`

**Example**: `!track_recipe Chicken Stir Fry`

**Features**:
- Automatically calculates nutrition from recipe
- Deducts all required ingredients from inventory
- Shows remaining available recipes

#### `!browse_recipes` / `!br` / `!available` / `!can_cook`
Browse recipes you can make with current inventory.

**Format**: `!browse_recipes [category]`

**Examples**:
```
!browse_recipes           # Show all available
!browse_recipes breakfast # Show only breakfast recipes
```

**Categories**: breakfast, lunch, dinner, snack

### Meal Presets

#### `!preset` / `!save`
Save a meal as a preset for quick logging.

**Format**: `!preset name "food description" calories protein carbs fats`

**Example**: `!preset chicken "Grilled chicken breast" 165 31 0 3.6`

#### `!quick` / `!q`
Quick log using a saved preset.

**Format**: `!quick preset_name [multiplier]`

**Examples**:
```
!quick chicken       # Logs 1 serving
!quick chicken 1.5   # Logs 1.5 servings
```

#### `!presets` / `!list_presets`
Show all saved meal presets.

**Example**: `!presets`

#### `!delete_preset`
Delete a saved preset.

**Format**: `!delete_preset name`

**Example**: `!delete_preset chicken`

---

## Workout Bot Commands

### Workout Sessions

#### `!start_workout` / `!start` / `!begin`
Start a workout session from a template.

**Format**: `!start_workout "workout name"`

**Example**: `!start_workout Push Day`

**Features**:
- Shows all exercises for the workout
- Tracks time automatically
- Enables set logging

#### `!log_set` / `!log` / `!ls`
Log a set during active workout.

**Format**: `!log exercise weight reps [rpe]`

**Examples**:
```
!log "bench press" 185 8
!log "bench press" 185 8 8.5   # With RPE
```

**Features**:
- Automatically tracks set numbers
- Detects personal records
- Calculates estimated 1RM

#### `!w` / `!quick`
Quick log shortcut for experienced users.

**Format**: `!w exercise weight reps [rpe]`

**Example**: `!w bench 185 8`

#### `!status` / `!current`
Show current workout progress.

**Example**: `!status`

**Shows**:
- Workout duration
- Exercise completion status
- Total volume
- Last set for each exercise

#### `!end_workout` / `!end` / `!finish`
End current workout session.

**Format**: `!end_workout [notes]`

**Example**: `!end_workout Great session, felt strong`

### Workout Templates

#### `!create_workout` / `!create`
Create a new workout template.

**Format**: `!create_workout "name" type`

**Types**: push, pull, legs, upper, lower, full, cardio, custom

**Example**: `!create_workout "Push Day" push`

#### `!add_exercise` / `!add`
Add exercise to workout template.

**Format**: `!add_exercise "workout" "exercise" sets rep_range`

**Examples**:
```
!add_exercise "Push Day" "bench press" 3 8-10
!add_exercise "Push Day" "overhead press" 4 6-8
```

#### `!templates` / `!workouts`
List all workout templates.

**Example**: `!templates`

#### `!view_workout` / `!view`
View detailed workout template.

**Format**: `!view_workout workout_name`

**Example**: `!view_workout Push Day`

#### `!delete_workout`
Delete a workout template.

**Format**: `!delete_workout workout_name`

**Example**: `!delete_workout Push Day`

---

## Inventory & Meal Planning Commands

### Food Inventory Management

#### `!add_food` / `!add_item` / `!stock`
Add food to your inventory.

**Format**: `!add_food quantity unit food_name`

**Examples**:
```
!add_food 2 lbs chicken breast
!add_food 1 dozen eggs
!add_food 500 grams rice
```

**Features**:
- Auto-prompts for expiration date on perishables
- Auto-assigns storage location (fridge/freezer/pantry)
- Shows newly available recipes

#### `!inventory` / `!inv` / `!pantry`
Show your food inventory.

**Format**: `!inventory [location]`

**Examples**:
```
!inventory          # Show all items
!inventory fridge   # Show only fridge items
!inventory freezer  # Show only freezer items
```

**Features**:
- Groups by storage location
- Shows expiring items with warnings
- Displays quantity and units

#### `!use_food` / `!use` / `!consume`
Manually use/consume food from inventory.

**Format**: `!use_food quantity unit food_name`

**Example**: `!use 1 lbs chicken breast`

### Recipe Management

#### `!load_recipes` / `!import_recipes`
Load premade recipes into your collection.

**Example**: `!load_recipes`

**Features**:
- Loads 20+ premade recipes
- Covers breakfast, lunch, dinner, snacks
- Skips duplicates automatically

#### `!add_recipe` / `!create_recipe`
Create a custom recipe interactively.

**Format**: `!add_recipe recipe_name`

**Example**: `!add_recipe Chicken Alfredo`

**Process**:
1. Bot prompts for ingredients
2. Enter ingredients as: `quantity unit ingredient`
3. Type 'done' when finished
4. Specify number of servings

#### `!recipes` / `!my_recipes`
Show all your saved recipes.

**Example**: `!recipes`

**Features**:
- Shows which recipes you can make now
- Groups by availability
- Shows serving sizes

#### `!recipe` / `!show_recipe`
Show detailed recipe information.

**Format**: `!recipe recipe_name`

**Example**: `!recipe Chicken Stir Fry`

**Shows**:
- Full ingredient list with availability
- Instructions
- Prep/cook time
- Missing ingredients if any

#### `!can_make` / `!available_recipes`
Show only recipes you have ingredients for.

**Example**: `!can_make`

### Meal Planning

#### `!plan_meal` / `!plan`
Schedule a recipe for a specific date and meal.

**Format**: `!plan date meal_type recipe_name`

**Examples**:
```
!plan 2024-01-15 dinner Chicken Stir Fry
!plan tomorrow lunch Sandwich
!plan monday breakfast Oatmeal
```

**Date formats**: YYYY-MM-DD, today, tomorrow, weekday names

**Meal types**: breakfast, lunch, dinner, snack

#### `!meal_plan` / `!meals` / `!menu`
View your meal plan.

**Format**: `!meal_plan [days]`

**Example**: `!meal_plan 7`

**Features**:
- Shows planned meals by date
- Indicates completed meals
- Shows calories per meal

#### `!shopping_list` / `!shop` / `!grocery`
Generate shopping list for meal plan.

**Format**: `!shopping_list [days]`

**Example**: `!shopping_list 7`

**Features**:
- Calculates needed ingredients
- Accounts for current inventory
- Groups by category
- Checkable items

---

## Analytics & Progress Tracking

### Nutrition Analytics

#### `!plot` / `!chart` / `!graph`
Generate nutrition progress charts.

**Format**: `!plot [days]`

**Example**: `!plot 30`

**Shows**:
- Daily calorie intake vs target
- Daily protein intake vs target
- Visual trend lines

#### `!stats` / `!s`
Show nutrition statistics.

**Format**: `!stats [days]`

**Example**: `!stats 30`

**Shows**:
- Average daily intake
- Tracking consistency
- Min/max values
- Weight change (if tracked)
- Most frequent foods

### Workout Analytics

#### `!progress`
Show progress for specific exercise.

**Format**: `!progress exercise_name`

**Example**: `!progress bench press`

**Features**:
- Estimated 1RM progression chart
- Trend line with gains per session
- Starting vs current strength

#### `!prs` / `!records`
Show all personal records.

**Example**: `!prs`

**Shows**:
- Top lifts by estimated 1RM
- Weight x reps = 1RM
- Date achieved

#### `!history` / `!recent`
Show recent workout history.

**Format**: `!history [days]`

**Example**: `!history 30`

**Shows**:
- Recent workouts with duration
- Total volume per session
- RPE ratings

#### `!volume`
Analyze training volume by muscle group.

**Format**: `!volume [days]`

**Example**: `!volume 14`

**Features**:
- Pie chart of volume distribution
- Sets per muscle group
- Helps identify imbalances

---

## Tips & Best Practices

### Nutrition Tips

1. **Log consistently**: Try to log meals right after eating
2. **Use presets**: Save frequent meals as presets for quick logging
3. **Plan ahead**: Use meal planning to prepare for the week
4. **Track recipes**: Use `!track_recipe` to maintain accurate inventory
5. **Review regularly**: Check `!stats` weekly to stay on track

### Workout Tips

1. **Use templates**: Create templates for consistent workouts
2. **Log immediately**: Log sets right after completing them
3. **Track RPE**: Include RPE for better fatigue management
4. **Review progress**: Check `!progress` monthly for each main lift
5. **Complete workouts**: Always use `!end_workout` to save data

### Inventory Tips

1. **Regular updates**: Add groceries to inventory after shopping
2. **Set expiration dates**: Especially for perishables
3. **Use recipes**: Let recipes auto-deduct ingredients
4. **Check availability**: Use `!can_make` before meal planning
5. **Generate lists**: Use `!shopping_list` before grocery trips

---

## Troubleshooting

### Common Issues

**Bot not responding**
- Check bot is online (green status)
- Verify using correct prefix (!)
- Ensure proper command format

**"No active workout" error**
- Start a workout first with `!start_workout`
- Check if previous workout was ended properly

**"Recipe not found" error**
- Check exact recipe name with `!recipes`
- Recipe names are case-insensitive
- Use quotes for multi-word names

**"Insufficient ingredients" error**
- Check inventory with `!inventory`
- Add missing items with `!add_food`
- Use `!shopping_list` to see what's needed

**Commands on cooldown**
- Some commands have cooldowns to prevent spam
- Wait the specified time before retrying

### Getting Help

1. **Check command usage**: Most errors show correct format
2. **View examples**: This guide provides examples for all commands
3. **Check logs**: Bot logs are in the `logs/` directory
4. **Restart bots**: Use the launcher to restart if needed

### Data Management

- **Databases**: Located in `data/` directory
- **Backups**: Automatically created in `backups/`
- **Export data**: Use database viewers for SQLite files

---

## Quick Reference Card

### Essential Nutrition Commands
- `!log "food" calories protein carbs fats` - Log meal
- `!today` - View daily summary
- `!track_recipe "name"` - Track recipe & deduct inventory
- `!browse_recipes` - See available recipes

### Essential Workout Commands  
- `!start_workout "name"` - Begin workout
- `!log "exercise" weight reps` - Log a set
- `!status` - Check workout progress
- `!end_workout` - Finish workout

### Essential Inventory Commands
- `!add_food qty unit food` - Add to inventory
- `!inventory` - View all items
- `!can_make` - Available recipes
- `!shopping_list 7` - Weekly shopping list

---

Remember: Consistency is key! Regular tracking leads to better results. 💪🥗