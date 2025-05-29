# Correct Nutrition Bot Commands

## ❌ Commands that DON'T exist:
- `!setup` - This command doesn't exist (set goals individually)
- `!edit_meal` - Use `!edit` instead
- `!units` - This command doesn't exist (units stored per user but no command to change)

## ✅ Working Commands:

### Setting Goals
```
!set_goal calories 2000
!goal protein 150
!target carbs 250
```

### Logging Meals
```
!log "chicken breast" 165 31 0 3.6
!l "protein shake" 150 30 5 2
!food "brown rice" 220 5 45 2
```

### Managing Logged Meals
```
!today              # View today's summary
!edit 123 calories 200    # Edit a meal (use meal ID from !today)
!delete 123         # Delete a meal
!undo              # Delete last logged meal
```

### Meal Presets
```
!preset chicken "Grilled chicken breast" 165 31 0 3.6
!save oats "Morning oatmeal" 300 10 50 5
!quick chicken      # Use preset
!q chicken 1.5     # Use 1.5 servings
!presets           # List all presets
!delete_preset chicken
```

### Recipe Tracking
```
!track_recipe "Chicken Stir Fry"    # Log recipe & deduct ingredients
!browse_recipes                      # See available recipes
!br breakfast                        # Browse breakfast recipes
```

### Analytics
```
!plot              # Generate progress chart
!plot 30           # Last 30 days
!stats             # Show statistics
!stats 7           # Last 7 days
```

### Inventory Management
```
!add_food 2 lbs chicken breast       # Add to inventory
!inventory                           # View all inventory
!use_food 1 lb chicken breast        # Manually use inventory
```

### Recipe Management
```
!load_recipes                        # Load premade recipes
!add_recipe "My Recipe"              # Create custom recipe (interactive)
!recipes                             # List all recipes
!recipe "Chicken Stir Fry"           # View recipe details
!can_make                            # Show recipes you can make now
```

### Meal Planning
```
!plan_meal 2024-01-15 dinner "Chicken Stir Fry"
!plan tomorrow lunch "Sandwich"
!meal_plan                           # View meal plan
!meal_plan 7                         # View 7-day plan
!shopping_list 7                     # Generate shopping list
```

## Notes:
1. There is NO setup command - you need to set goals individually using `!set_goal`
2. Units are stored per user but there's no command to change them
3. Use `!edit` not `!edit_meal`
4. All commands use the prefix set in .env (default: !)
5. First time users should:
   - Run `!load_recipes` to get premade recipes
   - Set goals with `!set_goal calories 2000` etc.
   - Add inventory with `!add_food`