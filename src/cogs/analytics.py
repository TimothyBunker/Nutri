"""
Analytics cog for nutrition data visualization
"""

import discord
from discord.ext import commands
import matplotlib.pyplot as plt
import io
from datetime import date, timedelta

from ..utils import EmbedBuilder, format_date


class NutritionAnalyticsCog(commands.Cog, name="Analytics"):
    """Commands for nutrition analytics and visualization"""
    
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db
    
    @commands.command(name='plot', aliases=['chart', 'graph'])
    async def plot_progress(self, ctx, days: int = 7):
        """
        Generate nutrition progress charts
        
        Example: !plot 7
        """
        if days < 1 or days > 365:
            await ctx.send(embed=EmbedBuilder.error(
                "Invalid range",
                "Days must be between 1 and 365"
            ))
            return
        
        # Get data
        trends = self.db.get_nutrition_trends(ctx.author.id, days)
        
        if not trends:
            await ctx.send(embed=EmbedBuilder.info(
                "No Data",
                f"No nutrition data found for the last {days} days"
            ))
            return
        
        # Get user targets
        user_stats = self.db.get_user_stats(ctx.author.id)
        cal_target = user_stats['daily_calorie_target'] if user_stats else 2000
        protein_target = user_stats['daily_protein_target'] if user_stats else 150
        
        # Prepare data
        dates = [format_date(t['date'], "%m/%d") for t in trends]
        calories = [t['daily_calories'] for t in trends]
        protein = [t['daily_protein'] for t in trends]
        
        # Create plots
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
        
        # Calories plot
        ax1.bar(dates, calories, color='skyblue', alpha=0.7)
        ax1.axhline(y=cal_target, color='red', linestyle='--', 
                    label=f'Target ({cal_target})')
        ax1.set_ylabel('Calories')
        ax1.set_title('Daily Calorie Intake')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Protein plot
        ax2.bar(dates, protein, color='lightgreen', alpha=0.7)
        ax2.axhline(y=protein_target, color='red', linestyle='--', 
                    label=f'Target ({protein_target}g)')
        ax2.set_ylabel('Protein (g)')
        ax2.set_xlabel('Date')
        ax2.set_title('Daily Protein Intake')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # Rotate x-axis labels if many days
        if len(dates) > 14:
            plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45)
            plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45)
        
        plt.tight_layout()
        
        # Save to buffer
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        plt.close()
        
        # Send plot
        file = discord.File(buffer, filename='nutrition_progress.png')
        
        # Calculate stats
        avg_calories = sum(calories) / len(calories)
        avg_protein = sum(protein) / len(protein)
        
        embed = discord.Embed(
            title=f"📊 {days}-Day Nutrition Progress",
            color=discord.Color.blue()
        )
        
        embed.add_field(
            name="Average Daily",
            value=f"Calories: {avg_calories:.0f}\nProtein: {avg_protein:.1f}g",
            inline=True
        )
        
        embed.add_field(
            name="Days Tracked",
            value=f"{len(trends)}/{days}",
            inline=True
        )
        
        embed.set_image(url="attachment://nutrition_progress.png")
        
        await ctx.send(embed=embed, file=file)
    
    @commands.command(name='stats', aliases=['s'])
    async def show_stats(self, ctx, days: int = 7):
        """
        Show nutrition statistics
        
        Example: !stats 30
        """
        if days < 1 or days > 365:
            await ctx.send(embed=EmbedBuilder.error(
                "Invalid range",
                "Days must be between 1 and 365"
            ))
            return
        
        # Get trends
        trends = self.db.get_nutrition_trends(ctx.author.id, days)
        
        if not trends:
            await ctx.send(embed=EmbedBuilder.info(
                "No Data",
                f"No nutrition data found for the last {days} days"
            ))
            return
        
        # Calculate statistics
        total_days = len(trends)
        total_calories = sum(t['daily_calories'] for t in trends)
        total_protein = sum(t['daily_protein'] for t in trends)
        
        avg_calories = total_calories / total_days
        avg_protein = total_protein / total_days
        
        # Get min/max
        min_cal = min(t['daily_calories'] for t in trends)
        max_cal = max(t['daily_calories'] for t in trends)
        
        # Get weight change
        weight_history = self.db.get_weight_history(ctx.author.id, days)
        
        embed = discord.Embed(
            title=f"📊 {days}-Day Statistics",
            color=discord.Color.blue()
        )
        
        # Tracking summary
        embed.add_field(
            name="Tracking",
            value=f"Days logged: {total_days}/{days}\n"
                  f"Completion: {(total_days/days*100):.1f}%",
            inline=True
        )
        
        # Calorie stats
        embed.add_field(
            name="Calories",
            value=f"Average: {avg_calories:.0f}\n"
                  f"Range: {min_cal} - {max_cal}",
            inline=True
        )
        
        # Protein stats
        embed.add_field(
            name="Protein",
            value=f"Average: {avg_protein:.1f}g\n"
                  f"Total: {total_protein:.0f}g",
            inline=True
        )
        
        # Weight change if available
        if weight_history and len(weight_history) >= 2:
            start_weight = weight_history[-1]['weight']
            end_weight = weight_history[0]['weight']
            weight_change = end_weight - start_weight
            
            embed.add_field(
                name="Weight Change",
                value=f"{weight_change:+.1f} lbs\n"
                      f"({start_weight:.1f} → {end_weight:.1f})",
                inline=False
            )
        
        # Most frequent foods
        freq_foods = self.db.get_meal_frequency(ctx.author.id, days)
        if freq_foods:
            top_foods = list(freq_foods.items())[:5]
            food_text = "\n".join([f"{i+1}. {food} ({count}x)" 
                                  for i, (food, count) in enumerate(top_foods)])
            
            embed.add_field(
                name="Top Foods",
                value=food_text,
                inline=False
            )
        
        await ctx.send(embed=embed)


async def setup(bot):
    """Setup function for cog"""
    await bot.add_cog(NutritionAnalyticsCog(bot))