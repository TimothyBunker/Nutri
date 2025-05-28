"""
Food inventory and meal planning Discord cog
"""

import discord
from discord.ext import commands
from datetime import datetime, date, timedelta
from typing import Optional, List
import asyncio

from ..utils import EmbedBuilder, format_number
from ..utils.premade_recipes import PREMADE_RECIPES, get_all_recipe_names
from ..models.inventory import InventoryDatabase


class InventoryCog(commands.Cog, name="Inventory & Meal Planning"):
    """Commands for food inventory and meal planning"""
    
    def __init__(self, bot):
        self.bot = bot
        self.db = InventoryDatabase(bot.db.db_path)  # Use same DB as nutrition
        self.db.init_db()
        self.nutrition_cog = None  # Will be set when both cogs are loaded
    
    @commands.Cog.listener()
    async def on_ready(self):
        """Get reference to nutrition cog when bot is ready"""
        self.nutrition_cog = self.bot.get_cog('Nutrition')
    
    # Recipe Commands
    @commands.command(name='load_recipes', aliases=['import_recipes'])
    @commands.cooldown(1, 60, commands.BucketType.user)
    async def load_premade_recipes(self, ctx):
        """
        Load premade recipes into your recipe collection
        
        Example: !load_recipes
        """
        # Check if user already has premade recipes
        existing_recipes = self.db.get_user_recipes(ctx.author.id)
        existing_names = [r['name'] for r in existing_recipes]
        
        loaded = 0
        skipped = 0
        
        for recipe_id, recipe_data in PREMADE_RECIPES.items():
            if recipe_data['name'] in existing_names:
                skipped += 1
                continue
            
            # Convert ingredient format
            ingredients = []
            for ing in recipe_data['ingredients']:
                ingredients.append({
                    'food_name': ing['item'],
                    'quantity': ing['quantity'],
                    'unit': ing['unit']
                })
            
            # Create recipe
            self.db.create_recipe(
                ctx.author.id,
                recipe_data['name'],
                ingredients,
                servings=1,
                description=f"Premade {recipe_data['category']} recipe",
                tags=[recipe_data['category'], 'premade']
            )
            loaded += 1
        
        embed = EmbedBuilder.success(
            "🍽️ Recipes Loaded!",
            f"Successfully loaded {loaded} premade recipes"
        )
        
        if skipped > 0:
            embed.add_field(
                name="ℹ️ Skipped",
                value=f"{skipped} recipes already exist in your collection",
                inline=False
            )
        
        # Show some of the loaded recipes
        if loaded > 0:
            sample_recipes = list(PREMADE_RECIPES.values())[:5]
            recipe_list = "\n".join(f"• {r['name']}" for r in sample_recipes)
            embed.add_field(
                name="📖 Sample Recipes",
                value=recipe_list + ("\n...and more!" if len(PREMADE_RECIPES) > 5 else ""),
                inline=False
            )
        
        embed.set_footer(text=f"Use {ctx.prefix}recipes to see all your recipes")
        await ctx.send(embed=embed)
    
    # Inventory Commands
    @commands.command(name='add_food', aliases=['add_item', 'stock'])
    async def add_food(self, ctx, quantity: float, unit: str, *, food_name: str):
        """
        Add food to your inventory
        
        Examples:
        !add_food 2 lbs chicken breast
        !add_food 1 dozen eggs
        !add_food 500 grams rice
        """
        # Optional: Ask for location and expiration
        location = 'pantry'  # Default
        
        # Check if it's a perishable item
        perishables = ['chicken', 'beef', 'milk', 'eggs', 'yogurt', 'fish']
        if any(p in food_name.lower() for p in perishables):
            # Ask for expiration date
            embed = EmbedBuilder.info(
                "Expiration Date",
                f"When does the {food_name} expire? (Reply with date like: 2024-12-25 or 'skip')"
            )
            await ctx.send(embed=embed)
            
            def check(m):
                return m.author == ctx.author and m.channel == ctx.channel
            
            try:
                msg = await self.bot.wait_for('message', timeout=30.0, check=check)
                if msg.content.lower() != 'skip':
                    expiration = msg.content
                else:
                    expiration = None
            except asyncio.TimeoutError:
                expiration = None
            
            # Ask for location
            if any(p in ['chicken', 'beef', 'fish', 'frozen'] for p in food_name.lower().split()):
                location = 'freezer'
            elif any(p in ['milk', 'eggs', 'yogurt', 'cheese'] for p in food_name.lower().split()):
                location = 'fridge'
        else:
            expiration = None
        
        # Add to inventory
        item_id = self.db.add_inventory_item(
            ctx.author.id, food_name, quantity, unit,
            location=location, expiration_date=expiration
        )
        
        embed = EmbedBuilder.success(
            "✅ Added to Inventory",
            f"Added {quantity} {unit} of **{food_name}** to {location}"
        )
        
        if expiration:
            embed.add_field(name="📅 Expires", value=expiration, inline=True)
        
        # Check what recipes are now available
        available_recipes = self.db.get_available_recipes(ctx.author.id)
        if available_recipes:
            recipe_names = [r['name'] for r in available_recipes[:3]]
            embed.add_field(
                name="🍳 You can now make",
                value="\n".join(f"• {name}" for name in recipe_names),
                inline=False
            )
            if len(available_recipes) > 3:
                embed.add_field(
                    name="",
                    value=f"...and {len(available_recipes) - 3} more recipes! 🎉",
                    inline=False
                )
        
        await ctx.send(embed=embed)
    
    @commands.command(name='inventory', aliases=['inv', 'pantry'])
    async def show_inventory(self, ctx, location: Optional[str] = None):
        """
        Show your food inventory
        
        Examples:
        !inventory          # Show all
        !inventory fridge   # Show only fridge items
        !inventory freezer  # Show only freezer items
        """
        inventory = self.db.get_inventory(ctx.author.id, location)
        
        if not inventory:
            embed = EmbedBuilder.info(
                "Empty Inventory",
                f"No items found{f' in {location}' if location else ''}.\n"
                f"Add items with `{ctx.prefix}add_food`"
            )
            await ctx.send(embed=embed)
            return
        
        # Group by location
        locations = {}
        for item in inventory:
            loc = item['location']
            if loc not in locations:
                locations[loc] = []
            locations[loc].append(item)
        
        embed = discord.Embed(
            title=f"📦 {'Your' if not location else location.title()} Inventory",
            color=discord.Color.blue()
        )
        
        # Add location emojis
        location_emojis = {
            'fridge': '🥶',
            'freezer': '🧊',
            'pantry': '🗄️'
        }
        
        for loc, items in locations.items():
            items_text = []
            for item in items[:10]:  # Limit per location
                text = f"• **{item['food_name']}**: {item['quantity']} {item['unit']}"
                if item['expiration_date']:
                    exp_date = datetime.strptime(item['expiration_date'], "%Y-%m-%d").date()
                    days_until = (exp_date - date.today()).days
                    if days_until <= 3:
                        text += f" ⚠️ (expires in {days_until} days)"
                items_text.append(text)
            
            emoji = location_emojis.get(loc, '📦')
            embed.add_field(
                name=f"{emoji} {loc.title()} ({len(items)} items)",
                value="\n".join(items_text),
                inline=False
            )
        
        # Check expiring items
        expiring = self.db.get_expiring_items(ctx.author.id, days=7)
        if expiring:
            exp_text = []
            for item in expiring[:5]:
                exp_date = datetime.strptime(item['expiration_date'], "%Y-%m-%d").date()
                days_until = (exp_date - date.today()).days
                exp_text.append(f"• {item['food_name']} - {days_until} days")
            
            embed.add_field(
                name="⚠️ Expiring Soon",
                value="\n".join(exp_text),
                inline=False
            )
        
        await ctx.send(embed=embed)
    
    @commands.command(name='use_food', aliases=['use', 'consume'])
    async def use_food(self, ctx, quantity: float, unit: str, *, food_name: str):
        """
        Use/consume food from inventory
        
        Example: !use 1 lbs chicken breast
        """
        # Get current inventory
        inventory = self.db.get_inventory(ctx.author.id)
        
        # Find the item
        found_item = None
        for item in inventory:
            if item['food_name'].lower() == food_name.lower():
                found_item = item
                break
        
        if not found_item:
            embed = EmbedBuilder.error(
                "Item not found",
                f"You don't have **{food_name}** in your inventory"
            )
            await ctx.send(embed=embed)
            return
        
        # Calculate new quantity
        new_quantity = found_item['quantity'] - quantity
        
        if new_quantity < 0:
            embed = EmbedBuilder.error(
                "Insufficient quantity",
                f"You only have {found_item['quantity']} {found_item['unit']} of {food_name}"
            )
            await ctx.send(embed=embed)
            return
        
        # Update inventory
        self.db.update_inventory_quantity(
            ctx.author.id, food_name, new_quantity, found_item['location']
        )
        
        embed = EmbedBuilder.success(
            "✅ Inventory Updated",
            f"Used {quantity} {unit} of **{food_name}**"
        )
        
        if new_quantity > 0:
            embed.add_field(
                name="📦 Remaining",
                value=f"{new_quantity} {found_item['unit']}",
                inline=True
            )
        else:
            embed.add_field(
                name="🗑️ Status",
                value="Item removed from inventory",
                inline=True
            )
        
        await ctx.send(embed=embed)
    
    # Recipe Commands
    @commands.command(name='add_recipe', aliases=['create_recipe'])
    async def add_recipe(self, ctx, *, name: str):
        """
        Create a new recipe interactively
        
        Example: !add_recipe Chicken Stir Fry
        """
        # Start interactive recipe creation
        embed = EmbedBuilder.info(
            f"Creating Recipe: {name}",
            "Let's add the ingredients. Reply with ingredients in format:\n"
            "`quantity unit ingredient` (one per line)\n"
            "Example:\n2 lbs chicken breast\n1 cup rice\n\n"
            "Type 'done' when finished."
        )
        await ctx.send(embed=embed)
        
        ingredients = []
        
        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel
        
        while True:
            try:
                msg = await self.bot.wait_for('message', timeout=60.0, check=check)
                
                if msg.content.lower() == 'done':
                    break
                
                # Parse ingredient
                parts = msg.content.split(maxsplit=2)
                if len(parts) >= 3:
                    try:
                        quantity = float(parts[0])
                        unit = parts[1]
                        ingredient = parts[2]
                        
                        ingredients.append({
                            'food_name': ingredient,
                            'quantity': quantity,
                            'unit': unit
                        })
                        
                        await msg.add_reaction('✅')
                    except ValueError:
                        await msg.add_reaction('❌')
                        await ctx.send("Invalid format. Use: `quantity unit ingredient`", delete_after=5)
                
            except asyncio.TimeoutError:
                await ctx.send("Recipe creation timed out.")
                return
        
        if not ingredients:
            await ctx.send(embed=EmbedBuilder.error("No ingredients added"))
            return
        
        # Ask for additional details
        embed = EmbedBuilder.info(
            "Recipe Details",
            "How many servings does this make? (Reply with a number)"
        )
        await ctx.send(embed=embed)
        
        try:
            msg = await self.bot.wait_for('message', timeout=30.0, check=check)
            servings = int(msg.content)
        except (asyncio.TimeoutError, ValueError):
            servings = 1
        
        # Create recipe
        recipe_id = self.db.create_recipe(
            ctx.author.id, name, ingredients, servings=servings
        )
        
        embed = EmbedBuilder.success(
            "✅ Recipe Created!",
            f"**{name}** has been saved with {len(ingredients)} ingredients"
        )
        
        # Check if can make it now
        availability = self.db.check_recipe_availability(ctx.author.id, recipe_id)
        if availability['can_make']:
            embed.add_field(
                name="✅ Ready to Cook!",
                value="You have all ingredients for this recipe",
                inline=False
            )
        else:
            missing_text = "\n".join(
                f"• {item['food_name']} ({item['required']} {item['unit']})"
                for item in availability['missing'][:5]
            )
            embed.add_field(
                name="Missing Ingredients",
                value=missing_text,
                inline=False
            )
        
        await ctx.send(embed=embed)
    
    @commands.command(name='recipes', aliases=['my_recipes'])
    async def list_recipes(self, ctx):
        """Show all your saved recipes"""
        recipes = self.db.get_user_recipes(ctx.author.id)
        
        if not recipes:
            embed = EmbedBuilder.info(
                "No Recipes",
                f"Create your first recipe with `{ctx.prefix}add_recipe`"
            )
            await ctx.send(embed=embed)
            return
        
        # Check which ones can be made
        available_ids = [r['id'] for r in self.db.get_available_recipes(ctx.author.id)]
        
        embed = discord.Embed(
            title="📖 Your Recipe Collection",
            description=f"Total: {len(recipes)} recipes",
            color=discord.Color.blue()
        )
        
        can_make = []
        cannot_make = []
        
        for recipe in recipes:
            if recipe['id'] in available_ids:
                can_make.append(recipe)
            else:
                cannot_make.append(recipe)
        
        # Show recipes you can make first
        if can_make:
            recipe_text = []
            for recipe in can_make[:10]:
                text = f"✅ **{recipe['name']}**"
                if recipe['servings'] > 1:
                    text += f" ({recipe['servings']} servings)"
                # Add category emoji if it's a premade recipe
                if recipe.get('tags') and 'premade' in recipe['tags']:
                    if 'breakfast' in recipe['tags']:
                        text = "🍳 " + text
                    elif 'lunch' in recipe['tags']:
                        text = "🥗 " + text
                    elif 'dinner' in recipe['tags']:
                        text = "🍽️ " + text
                    elif 'snack' in recipe['tags']:
                        text = "🍿 " + text
                recipe_text.append(text)
            
            embed.add_field(
                name=f"🟢 Can Make Now ({len(can_make)})",
                value="\n".join(recipe_text),
                inline=False
            )
        
        if cannot_make:
            recipe_text = []
            for recipe in cannot_make[:10]:
                text = f"⭕ **{recipe['name']}**"
                if recipe['servings'] > 1:
                    text += f" ({recipe['servings']} servings)"
                # Add category emoji if it's a premade recipe
                if recipe.get('tags') and 'premade' in recipe['tags']:
                    if 'breakfast' in recipe['tags']:
                        text = "🍳 " + text
                    elif 'lunch' in recipe['tags']:
                        text = "🥗 " + text
                    elif 'dinner' in recipe['tags']:
                        text = "🍽️ " + text
                    elif 'snack' in recipe['tags']:
                        text = "🍿 " + text
                recipe_text.append(text)
            
            embed.add_field(
                name=f"🔴 Missing Ingredients ({len(cannot_make)})",
                value="\n".join(recipe_text),
                inline=False
            )
        
        embed.set_footer(text=f"Total: {len(recipes)} recipes | Use {ctx.prefix}recipe [name] for details")
        
        await ctx.send(embed=embed)
    
    @commands.command(name='recipe', aliases=['show_recipe'])
    async def show_recipe(self, ctx, *, recipe_name: str):
        """Show detailed recipe information"""
        # Find recipe
        recipes = self.db.get_user_recipes(ctx.author.id)
        recipe = None
        
        for r in recipes:
            if r['name'].lower() == recipe_name.lower():
                recipe = self.db.get_recipe(r['id'])
                break
        
        if not recipe:
            embed = EmbedBuilder.error(
                "Recipe not found",
                f"Use `{ctx.prefix}recipes` to see your recipes"
            )
            await ctx.send(embed=embed)
            return
        
        # Check availability
        availability = self.db.check_recipe_availability(ctx.author.id, recipe['id'])
        
        embed = discord.Embed(
            title=f"🍽️ {recipe['name']}",
            description=recipe['description'] or "No description",
            color=discord.Color.green() if availability['can_make'] else discord.Color.orange()
        )
        
        # Basic info
        if recipe['servings']:
            embed.add_field(name="Servings", value=str(recipe['servings']), inline=True)
        if recipe['prep_time']:
            embed.add_field(name="Prep Time", value=f"{recipe['prep_time']} min", inline=True)
        if recipe['cook_time']:
            embed.add_field(name="Cook Time", value=f"{recipe['cook_time']} min", inline=True)
        
        # Ingredients
        ingredients_text = []
        for ing in recipe['ingredients']:
            status = "✅" if any(
                i['food_name'] == ing['food_name'] and i['available'] >= ing['quantity']
                for i in availability['ingredients']
            ) else "❌"
            
            text = f"{status} {ing['quantity']} {ing['unit']} {ing['food_name']}"
            if ing['is_optional']:
                text += " *(optional)*"
            ingredients_text.append(text)
        
        embed.add_field(
            name="Ingredients",
            value="\n".join(ingredients_text),
            inline=False
        )
        
        # Instructions
        if recipe['instructions']:
            embed.add_field(
                name="Instructions",
                value=recipe['instructions'][:1024],
                inline=False
            )
        
        # Availability status
        if availability['can_make']:
            embed.add_field(
                name="✅ Ready to Cook!",
                value="You have all required ingredients",
                inline=False
            )
        else:
            missing_text = []
            for item in availability['missing'][:5]:
                missing_text.append(f"• {item['food_name']} - need {item['required']} {item['unit']}")
            
            embed.add_field(
                name="❌ Missing Ingredients",
                value="\n".join(missing_text),
                inline=False
            )
        
        await ctx.send(embed=embed)
    
    @commands.command(name='can_make', aliases=['available_recipes'])
    async def can_make(self, ctx):
        """Show recipes you can make with current inventory"""
        recipes = self.db.get_available_recipes(ctx.author.id)
        
        if not recipes:
            embed = EmbedBuilder.info(
                "No Available Recipes",
                "You don't have enough ingredients for any recipes.\n"
                f"Add food with `{ctx.prefix}add_food` or create simpler recipes!"
            )
            await ctx.send(embed=embed)
            return
        
        embed = discord.Embed(
            title="🍳 Recipes You Can Make Right Now!",
            description=f"🎉 Found {len(recipes)} recipes you have all ingredients for!",
            color=discord.Color.green()
        )
        
        # Group by category if they have tags
        categorized = {
            'breakfast': [],
            'lunch': [],
            'dinner': [],
            'snack': [],
            'other': []
        }
        
        for recipe in recipes:
            if recipe.get('tags'):
                added = False
                for category in ['breakfast', 'lunch', 'dinner', 'snack']:
                    if category in recipe['tags']:
                        categorized[category].append(recipe)
                        added = True
                        break
                if not added:
                    categorized['other'].append(recipe)
            else:
                categorized['other'].append(recipe)
        
        # Display by category
        category_emojis = {
            'breakfast': '🍳',
            'lunch': '🥗',
            'dinner': '🍽️',
            'snack': '🍿',
            'other': '🍴'
        }
        
        shown = 0
        for category, cat_recipes in categorized.items():
            if cat_recipes and shown < 15:
                recipe_text = []
                for recipe in cat_recipes[:5]:
                    if shown >= 15:
                        break
                    text = f"✅ **{recipe['name']}**"
                    details = []
                    if recipe['servings'] > 1:
                        details.append(f"{recipe['servings']} servings")
                    if recipe['calories_per_serving']:
                        details.append(f"{recipe['calories_per_serving']} cal")
                    if details:
                        text += f" ({' | '.join(details)})"
                    recipe_text.append(text)
                    shown += 1
                
                if recipe_text:
                    emoji = category_emojis.get(category, '🍴')
                    embed.add_field(
                        name=f"{emoji} {category.title()}",
                        value="\n".join(recipe_text),
                        inline=False
                    )
        
        if len(recipes) > shown:
            embed.add_field(
                name="",
                value=f"✨ ...and {len(recipes) - shown} more recipes available!",
                inline=False
            )
        
        embed.set_footer(text=f"💡 Use {ctx.prefix}recipe [name] for cooking instructions")
        
        await ctx.send(embed=embed)
    
    # Meal Planning Commands
    @commands.command(name='plan_meal', aliases=['plan'])
    async def plan_meal(self, ctx, date_str: str, meal_type: str, *, recipe_name: str):
        """
        Plan a meal for a specific date
        
        Examples:
        !plan 2024-01-15 dinner Chicken Stir Fry
        !plan tomorrow lunch Sandwich
        !plan monday breakfast Oatmeal
        """
        # Parse date
        if date_str.lower() == 'today':
            planned_date = date.today()
        elif date_str.lower() == 'tomorrow':
            planned_date = date.today() + timedelta(days=1)
        else:
            try:
                planned_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            except ValueError:
                # Try parsing weekday
                weekdays = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
                if date_str.lower() in weekdays:
                    today = date.today()
                    target_weekday = weekdays.index(date_str.lower())
                    days_ahead = target_weekday - today.weekday()
                    if days_ahead <= 0:
                        days_ahead += 7
                    planned_date = today + timedelta(days=days_ahead)
                else:
                    await ctx.send(embed=EmbedBuilder.error("Invalid date format"))
                    return
        
        # Validate meal type
        valid_meals = ['breakfast', 'lunch', 'dinner', 'snack']
        if meal_type.lower() not in valid_meals:
            await ctx.send(embed=EmbedBuilder.error(
                "Invalid meal type",
                f"Choose from: {', '.join(valid_meals)}"
            ))
            return
        
        # Find recipe
        recipes = self.db.get_user_recipes(ctx.author.id)
        recipe = None
        for r in recipes:
            if r['name'].lower() == recipe_name.lower():
                recipe = r
                break
        
        if not recipe:
            await ctx.send(embed=EmbedBuilder.error(
                "Recipe not found",
                f"Use `{ctx.prefix}recipes` to see your recipes"
            ))
            return
        
        # Add to meal plan
        meal_id = self.db.add_meal_plan(
            ctx.author.id, recipe['id'], 
            planned_date.isoformat(), meal_type.lower()
        )
        
        embed = EmbedBuilder.success(
            "Meal Planned!",
            f"**{recipe['name']}** scheduled for {meal_type} on {planned_date.strftime('%A, %B %d')}"
        )
        
        # Check if ingredients available
        availability = self.db.check_recipe_availability(ctx.author.id, recipe['id'])
        if not availability['can_make']:
            missing_count = len(availability['missing'])
            embed.add_field(
                name="⚠️ Missing Ingredients",
                value=f"You're missing {missing_count} ingredients for this recipe",
                inline=False
            )
        
        await ctx.send(embed=embed)
    
    @commands.command(name='meal_plan', aliases=['meals', 'menu'])
    async def show_meal_plan(self, ctx, days: int = 7):
        """
        Show your meal plan
        
        Example: !meal_plan 7  # Show next 7 days
        """
        start_date = date.today()
        end_date = start_date + timedelta(days=days)
        
        meals = self.db.get_meal_plan(
            ctx.author.id, 
            start_date.isoformat(), 
            end_date.isoformat()
        )
        
        if not meals:
            embed = EmbedBuilder.info(
                "No Meals Planned",
                f"Plan meals with `{ctx.prefix}plan_meal`"
            )
            await ctx.send(embed=embed)
            return
        
        embed = discord.Embed(
            title=f"📅 Meal Plan ({days} days)",
            color=discord.Color.blue()
        )
        
        # Group by date
        by_date = {}
        for meal in meals:
            meal_date = meal['planned_date']
            if meal_date not in by_date:
                by_date[meal_date] = []
            by_date[meal_date].append(meal)
        
        for meal_date, day_meals in sorted(by_date.items()):
            date_obj = datetime.strptime(meal_date, "%Y-%m-%d").date()
            date_str = date_obj.strftime("%A, %b %d")
            
            meals_text = []
            for meal in day_meals:
                status = "✅" if meal['completed'] else "🔲"
                text = f"{status} **{meal['meal_type'].title()}**: {meal['recipe_name']}"
                if meal['calories_per_serving']:
                    text += f" ({meal['calories_per_serving']} cal)"
                meals_text.append(text)
            
            embed.add_field(
                name=date_str,
                value="\n".join(meals_text),
                inline=False
            )
        
        await ctx.send(embed=embed)
    
    @commands.command(name='shopping_list', aliases=['shop', 'grocery'])
    async def shopping_list(self, ctx, days: int = 7):
        """
        Generate shopping list for meal plan
        
        Example: !shopping_list 7  # For next 7 days
        """
        start_date = date.today()
        end_date = start_date + timedelta(days=days)
        
        # Generate list
        list_id = self.db.generate_shopping_list(
            ctx.author.id,
            start_date.isoformat(),
            end_date.isoformat()
        )
        
        shopping_list = self.db.get_shopping_list(list_id)
        
        if not shopping_list['items']:
            embed = EmbedBuilder.info(
                "Shopping List Empty",
                "You already have all ingredients for your planned meals! 🎉"
            )
            await ctx.send(embed=embed)
            return
        
        embed = discord.Embed(
            title=f"🛒 Shopping List ({days} days)",
            description=f"Items needed for your meal plan",
            color=discord.Color.blue()
        )
        
        # Group by category
        by_category = {}
        total_items = 0
        
        for item in shopping_list['items']:
            category = item['category'] or 'other'
            if category not in by_category:
                by_category[category] = []
            by_category[category].append(item)
            total_items += 1
        
        # Display by category
        for category, items in sorted(by_category.items()):
            items_text = []
            for item in items[:10]:  # Limit per category
                check = "☑️" if item['checked'] else "🔲"
                text = f"{check} {item['quantity']} {item['unit']} **{item['food_name']}**"
                items_text.append(text)
            
            if len(items) > 10:
                items_text.append(f"...and {len(items) - 10} more")
            
            embed.add_field(
                name=f"{category.title()} ({len(items)} items)",
                value="\n".join(items_text),
                inline=False
            )
        
        embed.set_footer(text=f"Total: {total_items} items | List ID: {list_id}")
        
        await ctx.send(embed=embed)


    # Nutrition Integration
    async def deduct_recipe_ingredients(self, user_id: int, recipe_name: str) -> bool:
        """
        Deduct ingredients from inventory when a recipe is tracked in nutrition
        Returns True if successful, False if ingredients not available
        """
        # Find the recipe
        recipes = self.db.get_user_recipes(user_id)
        recipe = None
        for r in recipes:
            if r['name'].lower() == recipe_name.lower():
                recipe = self.db.get_recipe(r['id'])
                break
        
        if not recipe:
            return False
        
        # Check availability first
        availability = self.db.check_recipe_availability(user_id, recipe['id'])
        if not availability['can_make']:
            return False
        
        # Deduct each ingredient
        for ingredient in recipe['ingredients']:
            if not ingredient['is_optional']:
                # Get current inventory
                inventory = self.db.get_inventory(user_id)
                for item in inventory:
                    if item['food_name'].lower() == ingredient['food_name'].lower():
                        new_quantity = item['quantity'] - ingredient['quantity']
                        self.db.update_inventory_quantity(
                            user_id, 
                            ingredient['food_name'],
                            max(0, new_quantity),
                            item['location']
                        )
                        break
        
        return True


async def setup(bot):
    """Setup function for cog"""
    await bot.add_cog(InventoryCog(bot))