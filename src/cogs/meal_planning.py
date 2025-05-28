"""
Meal planning and preset management cog
"""

import discord
from discord.ext import commands
from typing import Optional

from ..utils import EmbedBuilder


class MealPlanningCog(commands.Cog, name="Meal Planning"):
    """Commands for meal planning and presets"""
    
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db
    
    @commands.command(name='preset', aliases=['save'])
    async def save_preset(self, ctx, name: str, food_item: str, calories: int, 
                         protein: float = 0, carbs: float = 0, fats: float = 0):
        """
        Save a meal as a preset for quick logging
        
        Example: !preset chicken "Grilled chicken breast" 165 31 0 3.6
        """
        success = self.db.save_preset(
            ctx.author.id, name, food_item,
            calories, protein, carbs, fats
        )
        
        if success:
            embed = EmbedBuilder.success(
                "Preset Saved",
                f"Use `{ctx.prefix}quick {name}` to log this meal"
            )
        else:
            embed = EmbedBuilder.error(
                "Failed to save preset",
                "A preset with this name may already exist"
            )
        
        await ctx.send(embed=embed)
    
    @commands.command(name='quick', aliases=['q'])
    async def quick_log(self, ctx, preset_name: str, multiplier: float = 1.0):
        """
        Quick log using a preset
        
        Examples:
        !quick chicken      # Logs 1 serving
        !quick chicken 1.5  # Logs 1.5 servings
        """
        # Get preset
        preset = self.db.get_preset(ctx.author.id, preset_name)
        
        if not preset:
            # Show available presets
            presets = self.db.get_all_presets(ctx.author.id)
            
            if presets:
                preset_names = [p['name'] for p in presets]
                embed = EmbedBuilder.error(
                    "Preset not found",
                    f"Available presets: {', '.join(preset_names)}"
                )
            else:
                embed = EmbedBuilder.error(
                    "No presets saved",
                    f"Create one with `{ctx.prefix}preset`"
                )
            
            await ctx.send(embed=embed)
            return
        
        # Apply multiplier and log
        food = preset['food_item']
        if multiplier != 1.0:
            food = f"{food} x{multiplier}"
        
        # Call the log command
        nutrition_cog = self.bot.get_cog('Nutrition')
        if nutrition_cog:
            await nutrition_cog.log_meal(
                ctx,
                food,
                int(preset['calories'] * multiplier),
                preset['protein'] * multiplier,
                preset['carbs'] * multiplier,
                preset['fats'] * multiplier
            )
    
    @commands.command(name='presets', aliases=['list_presets'])
    async def list_presets(self, ctx):
        """List all saved meal presets"""
        presets = self.db.get_all_presets(ctx.author.id)
        
        if not presets:
            embed = EmbedBuilder.info(
                "No Presets",
                f"Save presets with `{ctx.prefix}preset`"
            )
            await ctx.send(embed=embed)
            return
        
        embed = discord.Embed(
            title="📋 Your Meal Presets",
            color=discord.Color.blue()
        )
        
        for preset in presets[:25]:  # Discord embed field limit
            value = f"{preset['food_item']}\n"
            value += f"{preset['calories']} cal | "
            value += f"{preset['protein']:.1f}p/{preset['carbs']:.1f}c/{preset['fats']:.1f}f"
            
            embed.add_field(
                name=preset['name'],
                value=value,
                inline=True
            )
        
        await ctx.send(embed=embed)
    
    @commands.command(name='delete_preset')
    async def delete_preset(self, ctx, name: str):
        """Delete a saved preset"""
        success = self.db.delete_preset(ctx.author.id, name)
        
        if success:
            embed = EmbedBuilder.success(
                "Preset Deleted",
                f"Removed preset: {name}"
            )
        else:
            embed = EmbedBuilder.error(
                "Preset not found",
                f"No preset named '{name}'"
            )
        
        await ctx.send(embed=embed)


async def setup(bot):
    """Setup function for cog"""
    await bot.add_cog(MealPlanningCog(bot))