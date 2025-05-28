"""
Workout planning and template management cog
"""

import discord
from discord.ext import commands
import json

from ..utils import EmbedBuilder, parse_rep_range


class WorkoutPlanningCog(commands.Cog, name="Workout Planning"):
    """Commands for workout planning and templates"""
    
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db
    
    @commands.command(name='create_workout', aliases=['create'])
    async def create_workout(self, ctx, name: str, day_type: str):
        """
        Create a workout template
        
        Example: !create_workout "Push Day" push
        """
        valid_types = ['push', 'pull', 'legs', 'upper', 'lower', 'full', 'cardio', 'custom']
        
        if day_type.lower() not in valid_types:
            embed = EmbedBuilder.error(
                "Invalid workout type",
                f"Valid types: {', '.join(valid_types)}"
            )
            await ctx.send(embed=embed)
            return
        
        # Check if exists
        existing = self.db.get_template(ctx.author.id, name)
        if existing:
            embed = EmbedBuilder.error(
                "Template exists",
                "Use a different name or delete the existing template"
            )
            await ctx.send(embed=embed)
            return
        
        # Create template
        template_id = self.db.create_template(
            ctx.author.id, name, day_type, []
        )
        
        embed = EmbedBuilder.success(
            "Workout Created",
            f"Created **{name}** ({day_type} day)",
            fields=[
                ("Next Step", f"Add exercises with `{ctx.prefix}add_exercise`", False)
            ]
        )
        
        await ctx.send(embed=embed)
    
    @commands.command(name='add_exercise', aliases=['add'])
    async def add_exercise(self, ctx, workout_name: str, exercise_name: str, 
                          sets: int, rep_range: str):
        """
        Add exercise to workout
        
        Example: !add_exercise "Push Day" "bench press" 3 8-10
        """
        # Get template
        template = self.db.get_template(ctx.author.id, workout_name)
        
        if not template:
            embed = EmbedBuilder.error(
                "Workout not found",
                f"Create it with `{ctx.prefix}create_workout`"
            )
            await ctx.send(embed=embed)
            return
        
        # Parse rep range
        try:
            min_reps, max_reps = parse_rep_range(rep_range)
        except ValueError:
            embed = EmbedBuilder.error(
                "Invalid rep range",
                "Use format like: 8-10 or 8"
            )
            await ctx.send(embed=embed)
            return
        
        # Add exercise
        exercises = template['exercises']
        exercises.append({
            'name': exercise_name.lower(),
            'sets': sets,
            'min_reps': min_reps,
            'max_reps': max_reps
        })
        
        # Update template
        success = self.db.update_template(
            ctx.author.id, template['id'],
            exercises=exercises
        )
        
        if success:
            embed = EmbedBuilder.success(
                "Exercise Added",
                f"Added **{exercise_name}** - {sets}x{rep_range} to **{workout_name}**"
            )
        else:
            embed = EmbedBuilder.error("Failed to add exercise")
        
        await ctx.send(embed=embed)
    
    @commands.command(name='templates', aliases=['workouts'])
    async def list_templates(self, ctx):
        """List all workout templates"""
        templates = self.db.get_all_templates(ctx.author.id)
        
        if not templates:
            embed = EmbedBuilder.info(
                "No Templates",
                f"Create one with `{ctx.prefix}create_workout`"
            )
            await ctx.send(embed=embed)
            return
        
        embed = discord.Embed(
            title="📋 Your Workout Templates",
            color=discord.Color.blue()
        )
        
        for template in templates[:25]:  # Discord limit
            exercise_count = len(template['exercises'])
            total_sets = sum(ex['sets'] for ex in template['exercises'])
            
            value = f"Type: {template['day_type']}\n"
            value += f"Exercises: {exercise_count} | Sets: {total_sets}"
            
            if template['last_used']:
                value += f"\nLast used: {template['last_used'][:10]}"
            
            embed.add_field(
                name=template['name'],
                value=value,
                inline=True
            )
        
        await ctx.send(embed=embed)
    
    @commands.command(name='view_workout', aliases=['view'])
    async def view_workout(self, ctx, *, workout_name: str):
        """View exercises in a workout template"""
        template = self.db.get_template(ctx.author.id, workout_name)
        
        if not template:
            embed = EmbedBuilder.error(
                "Workout not found",
                "Check the name or use !templates to list all"
            )
            await ctx.send(embed=embed)
            return
        
        embed = discord.Embed(
            title=f"📋 {template['name']}",
            description=f"Type: {template['day_type']}",
            color=discord.Color.blue()
        )
        
        if template['exercises']:
            exercise_text = ""
            for i, ex in enumerate(template['exercises'], 1):
                exercise_text += f"{i}. **{ex['name'].title()}** - "
                exercise_text += f"{ex['sets']}x{ex['min_reps']}-{ex['max_reps']}\n"
            
            embed.add_field(
                name="Exercises",
                value=exercise_text,
                inline=False
            )
            
            total_sets = sum(ex['sets'] for ex in template['exercises'])
            embed.add_field(
                name="Total Sets",
                value=str(total_sets),
                inline=True
            )
        else:
            embed.add_field(
                name="No Exercises",
                value=f"Add exercises with `{ctx.prefix}add_exercise`",
                inline=False
            )
        
        if template['times_completed']:
            embed.add_field(
                name="Times Completed",
                value=str(template['times_completed']),
                inline=True
            )
        
        await ctx.send(embed=embed)
    
    @commands.command(name='delete_workout')
    async def delete_workout(self, ctx, *, workout_name: str):
        """Delete a workout template"""
        template = self.db.get_template(ctx.author.id, workout_name)
        
        if not template:
            embed = EmbedBuilder.error(
                "Workout not found",
                "Check the name or use !templates to list all"
            )
            await ctx.send(embed=embed)
            return
        
        success = self.db.delete_template(ctx.author.id, template['id'])
        
        if success:
            embed = EmbedBuilder.success(
                "Workout Deleted",
                f"Removed template: {workout_name}"
            )
        else:
            embed = EmbedBuilder.error("Failed to delete workout")
        
        await ctx.send(embed=embed)


async def setup(bot):
    """Setup function for cog"""
    await bot.add_cog(WorkoutPlanningCog(bot))