"""
Nutrition tracking cog for Discord bot
"""

import discord
from discord.ext import commands
from datetime import datetime, date
from typing import Optional

from ..utils import (
    EmbedBuilder, validate_calories, validate_macros,
    format_number, format_calories, format_macros
)


class NutritionCog(commands.Cog, name="Nutrition"):
    """Commands for nutrition tracking"""
    
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db
        self.user_prefs = bot.user_prefs
        self.inventory_cog = None  # Will be set when both cogs are loaded
    
    @commands.Cog.listener()
    async def on_ready(self):
        """Get reference to inventory cog when bot is ready"""
        self.inventory_cog = self.bot.get_cog('Inventory & Meal Planning')
    
    @commands.command(name='log', aliases=['l', 'food', 'meal'])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def log_meal(self, ctx, food_item: str, calories: int, 
                       protein: float = 0, carbs: float = 0, fats: float = 0):
        """
        Log a meal with nutrition information
        
        Examples:
        !log "chicken breast" 165 31 0 3.6
        !log "protein shake" 150 30 5 2
        """
        # Validate inputs
        valid, error = validate_calories(calories)
        if not valid:
            await ctx.send(embed=EmbedBuilder.error("Invalid calories", error))
            return
        
        valid, error = validate_macros(protein, carbs, fats)
        if not valid:
            await ctx.send(embed=EmbedBuilder.error("Invalid macros", error))
            return
        
        # Check if this matches a recipe and offer to use it
        recipe_match = None
        deduct_ingredients = False
        
        if self.inventory_cog:
            inventory_db = self.inventory_cog.db
            recipes = inventory_db.get_user_recipes(ctx.author.id)
            
            # Find exact or similar recipe match
            for recipe in recipes:
                if recipe['name'].lower() == food_item.lower():
                    recipe_match = recipe
                    break
            
            # If exact match found, check availability and ask user
            if recipe_match:
                availability = inventory_db.check_recipe_availability(
                    ctx.author.id, recipe_match['id']
                )
                
                if availability['can_make']:
                    # Ask if they want to deduct ingredients
                    embed = EmbedBuilder.info(
                        "Recipe Match Found!",
                        f"**{recipe_match['name']}** found in your recipes.\n"
                        f"Would you like to deduct the ingredients from your inventory?\n\n"
                        f"React with ✅ to deduct ingredients or ❌ to just log the meal."
                    )
                    message = await ctx.send(embed=embed)
                    await message.add_reaction('✅')
                    await message.add_reaction('❌')
                    
                    def check(reaction, user):
                        return (user == ctx.author and 
                               str(reaction.emoji) in ['✅', '❌'] and
                               reaction.message.id == message.id)
                    
                    try:
                        reaction, user = await self.bot.wait_for(
                            'reaction_add', timeout=30.0, check=check
                        )
                        
                        if str(reaction.emoji) == '✅':
                            deduct_ingredients = True
                            # Use recipe nutrition if available
                            recipe_data = inventory_db.get_recipe(recipe_match['id'])
                            if recipe_data.get('calories_per_serving'):
                                calories = recipe_data['calories_per_serving']
                            if recipe_data.get('protein_per_serving'):
                                protein = recipe_data['protein_per_serving']
                    except:
                        pass  # Timeout or error, just continue with regular logging
                    
                    await message.delete()
        
        # Log the meal
        meal_id = self.db.log_meal(
            ctx.author.id, food_item, calories,
            protein, carbs, fats
        )
        
        # Check if this is a recipe from inventory and deduct ingredients
        inventory_updated = False
        if self.inventory_cog and recipe_match and deduct_ingredients:
            # Deduct ingredients if user confirmed
            inventory_updated = await self.inventory_cog.deduct_recipe_ingredients(
                ctx.author.id, food_item
            )
        
        # Get today's totals
        today = date.today().isoformat()
        totals = self.db.get_daily_totals(ctx.author.id, today)
        
        # Get user targets
        user_stats = self.db.get_user_stats(ctx.author.id)
        if user_stats:
            cal_target = user_stats['daily_calorie_target'] or 2000
            protein_target = user_stats['daily_protein_target'] or 150
        else:
            cal_target = 2000
            protein_target = 150
        
        # Create response embed
        embed = EmbedBuilder.meal_logged(food_item, calories, meal_id)
        
        # Add macro info
        embed.add_field(
            name="Macros",
            value=format_macros(protein, carbs, fats),
            inline=True
        )
        
        # Add daily progress
        cal_percent = (totals['calories'] / cal_target * 100) if cal_target > 0 else 0
        protein_percent = (totals['protein'] / protein_target * 100) if protein_target > 0 else 0
        
        embed.add_field(
            name="Daily Progress",
            value=f"Calories: {totals['calories']}/{cal_target} ({cal_percent:.1f}%)\n"
                  f"Protein: {totals['protein']:.1f}g/{protein_target}g ({protein_percent:.1f}%)",
            inline=False
        )
        
        # Add inventory update notification
        if inventory_updated:
            embed.add_field(
                name="📦 Inventory Updated",
                value="Recipe ingredients have been deducted from your inventory",
                inline=False
            )
        
        # Add tip about available recipes
        if self.inventory_cog:
            available_count = len(self.inventory_cog.db.get_available_recipes(ctx.author.id))
            if available_count > 0:
                embed.set_footer(
                    text=f"💡 You have {available_count} recipes available. Use {ctx.prefix}browse_recipes to see them!"
                )
            else:
                embed.set_footer(
                    text=f"Tip: Edit with {ctx.prefix}edit {meal_id} [field] [value]"
                )
        else:
            embed.set_footer(
                text=f"Tip: Edit with {ctx.prefix}edit {meal_id} [field] [value]"
            )
        
        await ctx.send(embed=embed)
    
    @commands.command(name='today', aliases=['t', 'summary'])
    async def today_summary(self, ctx):
        """Show today's nutrition summary"""
        today = date.today()
        
        # Get meals
        meals = self.db.get_meals_for_date(ctx.author.id, today.isoformat())
        
        # Get totals
        totals = self.db.get_daily_totals(ctx.author.id, today.isoformat())
        
        # Get user targets
        user_stats = self.db.get_user_stats(ctx.author.id)
        
        # Create embed
        embed = discord.Embed(
            title="📊 Today's Nutrition Summary",
            description=today.strftime("%A, %B %d, %Y"),
            color=discord.Color.blue()
        )
        
        # Add meals list
        if meals:
            meal_text = ""
            for meal in meals[:10]:  # Limit to 10
                meal_text += f"`#{meal['id']}` {meal['time']} - {meal['food_item']} "
                meal_text += f"({meal['calories']} cal)\n"
            
            embed.add_field(name="Meals", value=meal_text, inline=False)
        else:
            embed.add_field(
                name="No meals logged",
                value=f"Use `{ctx.prefix}log` to add meals",
                inline=False
            )
        
        # Add totals with progress bars
        if user_stats:
            targets = {
                'calories': user_stats['daily_calorie_target'] or 2000,
                'protein': user_stats['daily_protein_target'] or 150
            }
        else:
            targets = {'calories': 2000, 'protein': 150}
        
        embed = EmbedBuilder.daily_summary(
            today.strftime("%A, %B %d, %Y"),
            totals,
            targets
        )
        
        # Add macro breakdown
        if totals['calories'] > 0:
            protein_pct, carbs_pct, fats_pct = self._calculate_macro_percentages(
                totals['protein'], totals['carbs'], totals['fats']
            )
            
            embed.add_field(
                name="Macro Split",
                value=f"P: {protein_pct:.0f}% | C: {carbs_pct:.0f}% | F: {fats_pct:.0f}%",
                inline=False
            )
        
        await ctx.send(embed=embed)
    
    @commands.command(name='edit')
    async def edit_meal(self, ctx, meal_id: int, field: str, value: float):
        """
        Edit a previously logged meal
        
        Fields: calories, protein, carbs, fats
        Example: !edit 123 calories 200
        """
        # Validate field
        valid_fields = ['calories', 'protein', 'carbs', 'fats']
        if field.lower() not in valid_fields:
            await ctx.send(embed=EmbedBuilder.error(
                "Invalid field",
                f"Valid fields: {', '.join(valid_fields)}"
            ))
            return
        
        # Update the meal
        success = self.db.update_meal(
            meal_id, ctx.author.id,
            **{field: value}
        )
        
        if success:
            meal = self.db.get_meal(meal_id, ctx.author.id)
            embed = EmbedBuilder.success(
                "Meal Updated",
                f"Set {field} to {value} for: {meal['food_item']}"
            )
        else:
            embed = EmbedBuilder.error(
                "Update failed",
                "Check the meal ID or use !today to see your meals"
            )
        
        await ctx.send(embed=embed)
    
    @commands.command(name='delete', aliases=['remove'])
    async def delete_meal(self, ctx, meal_id: int):
        """Delete a logged meal"""
        # Get meal details first
        meal = self.db.get_meal(meal_id, ctx.author.id)
        
        if not meal:
            await ctx.send(embed=EmbedBuilder.error(
                "Meal not found",
                "Check the meal ID or use !today to see your meals"
            ))
            return
        
        # Delete the meal
        success = self.db.delete_meal(meal_id, ctx.author.id)
        
        if success:
            embed = EmbedBuilder.success(
                "Meal Deleted",
                f"Removed: {meal['food_item']} ({meal['calories']} calories)"
            )
        else:
            embed = EmbedBuilder.error("Failed to delete meal")
        
        await ctx.send(embed=embed)
    
    @commands.command(name='undo', aliases=['u'])
    async def undo_last(self, ctx):
        """Undo the last logged meal"""
        # Get the most recent meal
        today = date.today().isoformat()
        meals = self.db.get_meals_for_date(ctx.author.id, today)
        
        if not meals:
            await ctx.send(embed=EmbedBuilder.error(
                "No meals to undo",
                "You haven't logged any meals today"
            ))
            return
        
        # Delete the most recent one
        last_meal = meals[-1]
        success = self.db.delete_meal(last_meal['id'], ctx.author.id)
        
        if success:
            embed = EmbedBuilder.success(
                "Meal Removed",
                f"Deleted: {last_meal['food_item']} ({last_meal['calories']} calories)"
            )
        else:
            embed = EmbedBuilder.error("Failed to undo meal")
        
        await ctx.send(embed=embed)
    
    @commands.command(name='track_recipe', aliases=['tr', 'recipe_log'])
    async def track_recipe(self, ctx, *, recipe_name: str):
        """
        Track a recipe from your collection and auto-deduct ingredients
        
        Example: !track_recipe Chicken Stir Fry
        """
        if not self.inventory_cog:
            await ctx.send(embed=EmbedBuilder.error(
                "Inventory system not available",
                "Please try again in a moment"
            ))
            return
        
        # Get user's recipes from inventory
        inventory_db = self.inventory_cog.db
        recipes = inventory_db.get_user_recipes(ctx.author.id)
        
        # Find matching recipe
        recipe = None
        for r in recipes:
            if r['name'].lower() == recipe_name.lower():
                recipe = inventory_db.get_recipe(r['id'])
                break
        
        if not recipe:
            # Show available recipes
            recipe_names = [r['name'] for r in recipes[:10]]
            embed = EmbedBuilder.error(
                "Recipe not found",
                f"'{recipe_name}' not in your collection.\n\n"
                f"**Available recipes:**\n" + "\n".join(f"• {name}" for name in recipe_names)
            )
            if len(recipes) > 10:
                embed.set_footer(text=f"...and {len(recipes) - 10} more. Use !recipes to see all")
            await ctx.send(embed=embed)
            return
        
        # Check if ingredients are available
        availability = inventory_db.check_recipe_availability(ctx.author.id, recipe['id'])
        
        if not availability['can_make']:
            missing_text = []
            for item in availability['missing'][:5]:
                missing_text.append(f"• {item['food_name']} (need {item['required']} {item['unit']})")
            
            embed = EmbedBuilder.error(
                "Missing Ingredients",
                f"Cannot track **{recipe['name']}** - missing ingredients:\n" + 
                "\n".join(missing_text)
            )
            embed.set_footer(text=f"Add missing items with {ctx.prefix}add_food")
            await ctx.send(embed=embed)
            return
        
        # Calculate nutrition (if available)
        calories = recipe.get('calories_per_serving', 0)
        protein = recipe.get('protein_per_serving', 0)
        
        # If no nutrition info, estimate based on common ingredients
        if calories == 0:
            # Basic estimation
            calories = 300  # Default estimate
            protein = 20    # Default estimate
            
        # Log the meal
        meal_id = self.db.log_meal(
            ctx.author.id, recipe['name'], calories,
            protein, 0, 0  # Simplified macros
        )
        
        # Deduct ingredients
        success = await self.inventory_cog.deduct_recipe_ingredients(
            ctx.author.id, recipe['name']
        )
        
        # Create response
        embed = EmbedBuilder.success(
            "🍽️ Recipe Tracked!",
            f"Logged **{recipe['name']}** ({calories} calories)"
        )
        
        # Show what was deducted
        deducted_text = []
        for ing in recipe['ingredients'][:5]:
            if not ing['is_optional']:
                deducted_text.append(f"• {ing['quantity']} {ing['unit']} {ing['food_name']}")
        
        embed.add_field(
            name="📦 Ingredients Used",
            value="\n".join(deducted_text),
            inline=False
        )
        
        # Get today's totals
        today = date.today().isoformat()
        totals = self.db.get_daily_totals(ctx.author.id, today)
        
        # Get user targets
        user_stats = self.db.get_user_stats(ctx.author.id)
        if user_stats:
            cal_target = user_stats['daily_calorie_target'] or 2000
        else:
            cal_target = 2000
        
        cal_percent = (totals['calories'] / cal_target * 100) if cal_target > 0 else 0
        
        embed.add_field(
            name="📊 Daily Progress",
            value=f"Calories: {totals['calories']}/{cal_target} ({cal_percent:.1f}%)",
            inline=False
        )
        
        # Check what recipes are still available
        still_available = inventory_db.get_available_recipes(ctx.author.id)
        if still_available:
            embed.set_footer(text=f"✨ You can still make {len(still_available)} more recipes today!")
        else:
            embed.set_footer(text="Time to restock! Use !shopping_list to see what you need")
        
        await ctx.send(embed=embed)
    
    @commands.command(name='browse_recipes', aliases=['br', 'available', 'can_cook'])
    async def browse_recipes(self, ctx, category: Optional[str] = None):
        """
        Browse recipes you can make with your current inventory
        
        Examples:
        !browse_recipes          # Show all available recipes
        !browse_recipes breakfast # Show breakfast recipes only
        """
        if not self.inventory_cog:
            await ctx.send(embed=EmbedBuilder.error(
                "Inventory system not available",
                "Please try again in a moment"
            ))
            return
        
        # Get available recipes
        inventory_db = self.inventory_cog.db
        available_recipes = inventory_db.get_available_recipes(ctx.author.id)
        
        if not available_recipes:
            # Show what they're missing
            all_recipes = inventory_db.get_user_recipes(ctx.author.id)
            if not all_recipes:
                embed = EmbedBuilder.info(
                    "No Recipes Found",
                    f"You haven't added any recipes yet!\n\n"
                    f"**Get started:**\n"
                    f"• `{ctx.prefix}load_recipes` - Load premade recipes\n"
                    f"• `{ctx.prefix}add_recipe` - Create your own recipe\n"
                    f"• `{ctx.prefix}add_food` - Add ingredients to inventory"
                )
            else:
                embed = EmbedBuilder.info(
                    "No Available Recipes",
                    f"You don't have enough ingredients for any of your {len(all_recipes)} recipes.\n"
                    f"Use `{ctx.prefix}shopping_list` to see what you need!"
                )
            await ctx.send(embed=embed)
            return
        
        # Filter by category if specified
        if category:
            filtered = []
            for recipe in available_recipes:
                if recipe.get('tags') and category.lower() in recipe['tags']:
                    filtered.append(recipe)
            
            if not filtered:
                embed = EmbedBuilder.error(
                    "No recipes in category",
                    f"No available {category} recipes found.\n"
                    f"Try: breakfast, lunch, dinner, or snack"
                )
                await ctx.send(embed=embed)
                return
            
            available_recipes = filtered
        
        # Create paginated embed
        embed = discord.Embed(
            title=f"🍳 Available Recipes{f' - {category.title()}' if category else ''}",
            description=f"Found **{len(available_recipes)}** recipes you can make right now!",
            color=discord.Color.green()
        )
        
        # Group by meal type
        categorized = {
            'breakfast': [],
            'lunch': [],
            'dinner': [],
            'snack': [],
            'other': []
        }
        
        for recipe in available_recipes:
            added = False
            if recipe.get('tags'):
                for cat in ['breakfast', 'lunch', 'dinner', 'snack']:
                    if cat in recipe['tags']:
                        categorized[cat].append(recipe)
                        added = True
                        break
            if not added:
                categorized['other'].append(recipe)
        
        # Display recipes by category
        shown = 0
        for cat, recipes in categorized.items():
            if recipes and shown < 20:
                recipe_list = []
                for recipe in recipes[:5]:
                    if shown >= 20:
                        break
                    
                    # Build recipe info
                    info_parts = []
                    if recipe.get('calories_per_serving'):
                        info_parts.append(f"{recipe['calories_per_serving']} cal")
                    if recipe.get('protein_per_serving'):
                        info_parts.append(f"{recipe['protein_per_serving']}g protein")
                    if recipe.get('prep_time'):
                        info_parts.append(f"{recipe['prep_time']} min")
                    
                    recipe_text = f"• **{recipe['name']}**"
                    if info_parts:
                        recipe_text += f" ({' | '.join(info_parts)})"
                    
                    recipe_list.append(recipe_text)
                    shown += 1
                
                if recipe_list:
                    cat_emoji = {
                        'breakfast': '🍳',
                        'lunch': '🥗', 
                        'dinner': '🍽️',
                        'snack': '🍿',
                        'other': '🍴'
                    }
                    embed.add_field(
                        name=f"{cat_emoji.get(cat, '🍴')} {cat.title()}",
                        value="\n".join(recipe_list),
                        inline=False
                    )
        
        # Add quick actions
        embed.add_field(
            name="🚀 Quick Actions",
            value=f"• `{ctx.prefix}track_recipe [name]` - Track & deduct ingredients\n"
                  f"• `{ctx.prefix}recipe [name]` - View full recipe details\n"
                  f"• `{ctx.prefix}log [name] [calories]` - Log without deducting",
            inline=False
        )
        
        # Add helpful footer
        remaining_count = len(available_recipes) - shown
        if remaining_count > 0:
            embed.set_footer(text=f"...and {remaining_count} more recipes! Use specific categories to see more.")
        else:
            embed.set_footer(text="💡 Tip: Plan your week with !plan_meal [date] [meal] [recipe]")
        
        await ctx.send(embed=embed)
    
    @commands.command(name='set_goal', aliases=['goal', 'target'])
    async def set_goal(self, ctx, calories: int, protein: int = None, carbs: int = None, fats: int = None):
        """
        Set your daily nutrition goals
        
        Examples:
        !set_goal 2200 150 250 80
        !set_goal 1800 120  # calories and protein only
        """
        # Validate calories
        valid, error = validate_calories(calories)
        if not valid:
            await ctx.send(embed=EmbedBuilder.error("Invalid calories", error))
            return
        
        # Validate macros if provided
        if protein is not None or carbs is not None or fats is not None:
            valid, error = validate_macros(protein or 0, carbs or 0, fats or 0)
            if not valid:
                await ctx.send(embed=EmbedBuilder.error("Invalid macros", error))
                return
        
        # Update user goals
        self.db.set_user_goals(ctx.author.id, calories, protein, carbs, fats)
        
        # Create confirmation embed
        embed = EmbedBuilder.success(
            "🎯 Goals Updated!",
            f"Your daily nutrition goals have been set:"
        )
        
        embed.add_field(name="Calories", value=f"{calories:,} cal", inline=True)
        if protein:
            embed.add_field(name="Protein", value=f"{protein}g", inline=True)
        if carbs:
            embed.add_field(name="Carbs", value=f"{carbs}g", inline=True)
        if fats:
            embed.add_field(name="Fats", value=f"{fats}g", inline=True)
        
        embed.set_footer(text="Use !today to see your progress toward these goals")
        
        await ctx.send(embed=embed)
    
    @commands.command(name='help')
    async def nutrition_help(self, ctx, command: str = None):
        """
        Show help for nutrition commands
        
        Examples:
        !help          # Show all commands
        !help log      # Show help for log command
        """
        if command:
            # Show help for specific command
            cmd = self.bot.get_command(command)
            if cmd and cmd.cog_name == "Nutrition":
                embed = discord.Embed(
                    title=f"Help: {cmd.name}",
                    description=cmd.help or "No description available",
                    color=discord.Color.blue()
                )
                
                if cmd.aliases:
                    embed.add_field(
                        name="Aliases",
                        value=", ".join(f"`{alias}`" for alias in cmd.aliases),
                        inline=False
                    )
                
                usage = f"{ctx.prefix}{cmd.name} {cmd.signature}"
                embed.add_field(name="Usage", value=f"`{usage}`", inline=False)
                
            else:
                embed = EmbedBuilder.error("Command not found", f"No nutrition command named '{command}'")
        else:
            # Show all nutrition commands
            embed = discord.Embed(
                title="🍎 Nutrition Bot Commands",
                description="Track your daily nutrition and reach your goals!",
                color=discord.Color.green()
            )
            
            # Basic logging
            embed.add_field(
                name="📝 Food Logging",
                value=(
                    f"`{ctx.prefix}log <food> <calories> [protein] [carbs] [fats]`\n"
                    f"`{ctx.prefix}today` - View today's summary\n"
                    f"`{ctx.prefix}edit <id> <field> <value>` - Edit a meal\n"
                    f"`{ctx.prefix}delete <id>` - Delete a meal\n"
                    f"`{ctx.prefix}undo` - Delete last meal"
                ),
                inline=False
            )
            
            # Goals and progress
            embed.add_field(
                name="🎯 Goals & Progress",
                value=(
                    f"`{ctx.prefix}set_goal <calories> [protein] [carbs] [fats]`\n"
                    f"`{ctx.prefix}stats [days]` - Nutrition statistics\n"
                    f"`{ctx.prefix}chart [days]` - Generate charts"
                ),
                inline=False
            )
            
            # Presets and recipes
            embed.add_field(
                name="🍽️ Presets & Recipes",
                value=(
                    f"`{ctx.prefix}preset <name>` - Use saved preset\n"
                    f"`{ctx.prefix}presets` - List all presets\n"
                    f"`{ctx.prefix}browse_recipes [category]` - Available recipes\n"
                    f"`{ctx.prefix}track_recipe <name>` - Log recipe & deduct ingredients"
                ),
                inline=False
            )
            
            embed.set_footer(text=f"Use {ctx.prefix}help <command> for detailed help on a specific command")
        
        await ctx.send(embed=embed)
    
    def _calculate_macro_percentages(self, protein: float, carbs: float, fats: float):
        """Calculate macro percentages from grams"""
        total_calories = (protein * 4) + (carbs * 4) + (fats * 9)
        
        if total_calories == 0:
            return 0, 0, 0
        
        protein_pct = (protein * 4 / total_calories) * 100
        carbs_pct = (carbs * 4 / total_calories) * 100
        fats_pct = (fats * 9 / total_calories) * 100
        
        return protein_pct, carbs_pct, fats_pct


async def setup(bot):
    """Setup function for cog"""
    await bot.add_cog(NutritionCog(bot))