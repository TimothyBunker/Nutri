# Health & Fitness Discord Bots - User Guide

## 🚀 Getting Started

### First Time Setup
1. Join the Discord server where the bots are running
2. Start with basic logging to familiarize yourself with the commands
3. Set your preferences: `!set_goal`, `!set_units`, `!timezone`
4. Load premade recipes: `!load_recipes`
5. Add some basic food inventory: `!add_food`

### Bot Prefixes
- **Nutrition Bot**: `!` (exclamation mark)
- **Workout Bot**: `!` (exclamation mark)

---

## 🍎 Nutrition Bot Commands

### Basic Food Logging

#### `!log <calories> [protein] [carbs] [fats] <food_name>`
Log a meal with nutritional information
- **Examples:**
  - `!log 350 25 45 12 Chicken and rice bowl`
  - `!log 150 Greek yogurt` (calories only)
  - `!log 520 35 40 20 Grilled salmon with vegetables`

#### `!delete_last` / `!dl`
Delete your most recent meal entry
- **Example:** `!delete_last`

#### `!edit_last <calories> [protein] [carbs] [fats]`
Edit the nutrition values of your last logged meal
- **Example:** `!edit_last 400 30 45 15`

### Meal Management

#### `!add_preset <name> <calories> [protein] [carbs] [fats]`
Create a reusable meal preset
- **Examples:**
  - `!add_preset "Protein Shake" 250 30 8 3`
  - `!add_preset "Morning Oatmeal" 320 12 58 8`

#### `!preset <preset_name>`
Log a meal using a saved preset
- **Example:** `!preset Protein Shake`

#### `!presets`
View all your saved meal presets

#### `!delete_preset <preset_name>`
Remove a meal preset
- **Example:** `!delete_preset "Old Recipe"`

### Goals & Progress

#### `!set_goal <calories> [protein] [carbs] [fats]`
Set your daily nutrition goals
- **Examples:**
  - `!set_goal 2200 150 250 80`
  - `!set_goal 1800` (calories only)

#### `!progress` / `!p`
View your daily nutrition progress with visual progress bars

#### `!weekly`
View your nutrition progress for the current week

#### `!streak`
Check your logging streak and consistency

### Data & Analytics

#### `!chart [days]`
Generate a nutrition chart (default: 7 days)
- **Examples:**
  - `!chart` (last 7 days)
  - `!chart 30` (last 30 days)

#### `!stats [days]`
View detailed nutrition statistics
- **Examples:**
  - `!stats` (last 7 days)
  - `!stats 14` (last 2 weeks)

#### `!export [days]`
Export your nutrition data to CSV
- **Example:** `!export 30`

### Recipe Integration

#### `!browse_recipes [category]` / `!br` / `!available`
Browse recipes you can make with current inventory
- **Examples:**
  - `!browse_recipes` (all available)
  - `!browse_recipes breakfast`
  - `!br lunch`

#### `!track_recipe <recipe_name>`
Log a recipe and automatically deduct ingredients from inventory
- **Example:** `!track_recipe Scrambled Eggs with Toast`

### Settings

#### `!set_units <metric|imperial>`
Set your preferred unit system
- **Example:** `!set_units metric`

#### `!timezone <timezone>`
Set your timezone for accurate daily tracking
- **Example:** `!timezone America/New_York`

---

## 🏋️ Workout Bot Commands

### Workout Sessions

#### `!start_workout [name]`
Begin a new workout session
- **Examples:**
  - `!start_workout` (generic session)
  - `!start_workout "Push Day"`
  - `!start_workout Upper Body`

#### `!end_workout`
End your current workout session

#### `!current_workout` / `!cw`
View your current workout session details

### Exercise Logging

#### `!add_exercise <exercise> <weight> <reps> [sets] [rpe]`
Log an exercise with weight and reps
- **Examples:**
  - `!add_exercise "Bench Press" 225 8 3` (3 sets)
  - `!add_exercise Squats 315 5 1 9` (1 set, RPE 9)
  - `!add_exercise "Pull-ups" bodyweight 12 3`

#### `!add_cardio <activity> <duration_minutes> [distance] [calories]`
Log cardio exercise
- **Examples:**
  - `!add_cardio Running 30 3.5` (30 min, 3.5 miles)
  - `!add_cardio Cycling 45 12 400` (45 min, 12 miles, 400 cal)

#### `!rest [minutes]`
Start a rest timer
- **Examples:**
  - `!rest` (default rest time)
  - `!rest 3` (3 minutes)

### Workout Templates

#### `!save_template <name>`
Save your current workout as a template
- **Example:** `!save_template "Push Day A"`

#### `!load_template <name>`
Start a workout using a saved template
- **Example:** `!load_template "Push Day A"`

#### `!templates`
View all your saved workout templates

#### `!delete_template <name>`
Delete a workout template
- **Example:** `!delete_template "Old Routine"`

### Progress Tracking

#### `!pr <exercise>` / `!personal_record`
View your personal record for an exercise
- **Examples:**
  - `!pr "Bench Press"`
  - `!pr Deadlift`

#### `!workout_history [days]`
View your recent workout history
- **Examples:**
  - `!workout_history` (last 7 days)
  - `!workout_history 30`

#### `!exercise_history <exercise> [days]`
View history for a specific exercise
- **Example:** `!exercise_history "Bench Press" 60`

### Analytics

#### `!workout_stats [days]`
View detailed workout statistics
- **Example:** `!workout_stats 30`

#### `!volume_chart <exercise> [days]`
Generate a volume chart for an exercise
- **Example:** `!volume_chart "Bench Press" 90`

#### `!strength_chart <exercise> [days]`
Generate a strength progression chart
- **Example:** `!strength_chart Squats 180`

---

## 📦 Inventory & Meal Planning Commands

### Inventory Management

#### `!add_food <quantity> <unit> <food_name> [location] [expiry_date]`
Add food to your inventory
- **Examples:**
  - `!add_food 2 cups rice`
  - `!add_food 1 lb chicken breast fridge 2024-06-15`
  - `!add_food 500 g pasta pantry`

#### `!use_food <quantity> <unit> <food_name>`
Remove food from your inventory
- **Examples:**
  - `!use_food 1 cup rice`
  - `!use_food 200 g chicken breast`

#### `!inventory [location]`
View your current food inventory
- **Examples:**
  - `!inventory` (all locations)
  - `!inventory fridge`
  - `!inventory pantry`

#### `!expiring [days]`
Check for food expiring soon
- **Examples:**
  - `!expiring` (next 3 days)
  - `!expiring 7` (next week)

### Recipe Management

#### `!load_recipes`
Load premade recipes into your collection
- **Example:** `!load_recipes`

#### `!add_recipe <name> <servings> <calories_per_serving> [prep_time]`
Create a new recipe
- **Example:** `!add_recipe "My Protein Bowl" 2 450 15`

#### `!add_ingredient <recipe_name> <quantity> <unit> <ingredient>`
Add ingredients to a recipe
- **Example:** `!add_ingredient "My Protein Bowl" 200 g chicken breast`

#### `!can_make [category]`
See which recipes you can make with current inventory
- **Examples:**
  - `!can_make` (all recipes)
  - `!can_make breakfast`

#### `!recipe <recipe_name>`
View recipe details and availability
- **Example:** `!recipe "Scrambled Eggs with Toast"`

### Meal Planning

#### `!plan_meal <recipe_name> <date> [meal_type]`
Plan a meal for a specific date
- **Examples:**
  - `!plan_meal "Chicken Stir Fry" 2024-06-15 dinner`
  - `!plan_meal "Oatmeal with Berries" tomorrow breakfast`

#### `!meal_plan [date]`
View meal plan for a specific date
- **Examples:**
  - `!meal_plan` (today)
  - `!meal_plan 2024-06-15`
  - `!meal_plan tomorrow`

#### `!weekly_plan`
View your meal plan for the current week

### Shopping Lists

#### `!shopping_list [start_date] [end_date]`
Generate shopping list based on meal plans
- **Examples:**
  - `!shopping_list` (next 7 days)
  - `!shopping_list 2024-06-15 2024-06-21`

#### `!add_to_shopping <item> [quantity] [unit]`
Manually add items to your shopping list
- **Examples:**
  - `!add_to_shopping milk 1 gallon`
  - `!add_to_shopping bananas 6`

#### `!remove_from_shopping <item>`
Remove items from your shopping list
- **Example:** `!remove_from_shopping milk`

---

## 📊 Analytics & Progress Commands

### Nutrition Analytics

#### `!daily_summary [date]`
Get a comprehensive daily nutrition summary
- **Examples:**
  - `!daily_summary` (today)
  - `!daily_summary 2024-06-14`

#### `!macro_breakdown [days]`
View macronutrient distribution
- **Example:** `!macro_breakdown 30`

#### `!calorie_trend [days]`
View calorie intake trends
- **Example:** `!calorie_trend 14`

### Workout Analytics

#### `!training_volume [days]`
View total training volume statistics
- **Example:** `!training_volume 30`

#### `!frequency_stats [days]`
View workout frequency statistics
- **Example:** `!frequency_stats 60`

#### `!strength_gains <exercise> [days]`
Calculate strength gains for an exercise
- **Example:** `!strength_gains "Bench Press" 90`

---

## 💡 Tips & Best Practices

### Nutrition Bot Tips
- **Consistency is Key**: Log meals regularly for accurate tracking
- **Use Presets**: Create presets for frequently eaten meals
- **Check Integration**: When logging meals, look for recipe matches to auto-deduct ingredients
- **Set Realistic Goals**: Use `!set_goal` with achievable targets
- **Weekly Reviews**: Use `!weekly` to assess your progress patterns

### Workout Bot Tips
- **Plan Your Sessions**: Use templates for consistent routines
- **Track RPE**: Include RPE values to monitor training intensity
- **Use Rest Timers**: The `!rest` command helps maintain consistent rest periods
- **Review PRs**: Check `!pr` regularly to track strength progression
- **Progressive Overload**: Use exercise history to plan progressive increases

### Inventory Tips
- **Regular Updates**: Keep inventory current for accurate meal planning
- **Check Expiry**: Use `!expiring` to minimize food waste
- **Plan Ahead**: Use meal planning to optimize grocery shopping
- **Load Recipes**: Start with `!load_recipes` for instant meal options

---

## 🔧 Troubleshooting

### Common Issues

#### "Command not found"
- Check that you're using the correct prefix: `!`
- Ensure you're in a channel where the bot has permissions
- Verify the command spelling and format

#### "Invalid format"
- Follow the exact format shown in examples
- Use quotes around multi-word food/exercise names
- Check that numbers are in the correct format

#### "No active workout session"
- Start a workout with `!start_workout` before logging exercises
- Check if your session timed out (sessions auto-end after 3 hours)

#### "Recipe not found"
- Check spelling and use exact recipe names
- Use `!can_make` to see available recipes
- Load premade recipes with `!load_recipes`

#### "Insufficient inventory"
- Check your inventory with `!inventory`
- Add missing ingredients with `!add_food`
- Adjust recipe quantities if needed

### Getting Help
- Use any command with incorrect parameters to see usage examples
- Check your recent entries with `!progress` or `!current_workout`
- Review available recipes with `!can_make` or `!browse_recipes`

---

## 📱 Quick Reference Card

### Essential Nutrition Commands
```
!log <calories> [protein] [carbs] [fats] <food_name>
!progress
!set_goal <calories> [protein] [carbs] [fats]
!preset <name>
!browse_recipes
```

### Essential Workout Commands
```
!start_workout [name]
!add_exercise <exercise> <weight> <reps> [sets] [rpe]
!add_cardio <activity> <duration> [distance]
!end_workout
!pr <exercise>
```

### Essential Inventory Commands
```
!add_food <quantity> <unit> <food_name>
!inventory
!can_make
!load_recipes
!shopping_list
```

### Quick Stats
```
!stats
!chart
!workout_stats
!weekly
```

---

*Happy tracking! 🏃‍♂️💪*