"""
Main workout tracking cog
"""

import discord
from discord.ext import commands
from datetime import datetime
from typing import Optional

from ..utils import (
    EmbedBuilder, validate_weight, validate_reps, validate_rpe,
    format_weight, format_duration, UnitConverter
)


class WorkoutCog(commands.Cog, name="Workout"):
    """Commands for workout tracking"""
    
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db
        self.user_prefs = bot.user_prefs
        self.sessions = {}  # Active workout sessions
    
    @commands.command(name='start_workout', aliases=['start', 'begin'])
    async def start_workout(self, ctx, *, workout_name: str):
        """
        Start a workout session
        
        Example: !start_workout Push Day
        """
        # Check for existing session
        if ctx.author.id in self.sessions:
            embed = EmbedBuilder.warning(
                "Active Workout",
                "You already have an active workout session",
                fields=[
                    ("Current", self.sessions[ctx.author.id]['name'], True),
                    ("Action", f"Use `{ctx.prefix}end_workout` to finish", False)
                ]
            )
            await ctx.send(embed=embed)
            return
        
        # Get template
        template = self.db.get_template(ctx.author.id, workout_name)
        
        if not template:
            # Show available templates
            templates = self.db.get_all_templates(ctx.author.id)
            
            if templates:
                template_list = "\n".join([f"• {t['name']} ({t['day_type']})" 
                                          for t in templates[:10]])
                embed = EmbedBuilder.error(
                    "Workout not found",
                    f"Available workouts:\n{template_list}"
                )
            else:
                embed = EmbedBuilder.error(
                    "No workouts",
                    f"Create one with `{ctx.prefix}create_workout`"
                )
            
            await ctx.send(embed=embed)
            return
        
        # Start workout
        workout_id = self.db.start_workout(
            ctx.author.id, 
            template['name'], 
            template['id']
        )
        
        # Create session
        self.sessions[ctx.author.id] = {
            'id': workout_id,
            'name': template['name'],
            'template_id': template['id'],
            'exercises': template['exercises'],
            'start_time': datetime.now(),
            'sets_completed': {}
        }
        
        # Build workout display
        embed = discord.Embed(
            title=f"🏋️ Started: {template['name']}",
            description=f"Workout #{workout_id}",
            color=discord.Color.green()
        )
        
        # Add exercises
        exercise_text = ""
        for i, ex in enumerate(template['exercises'], 1):
            exercise_text += f"{i}. **{ex['name'].title()}** - "
            exercise_text += f"{ex['sets']}x{ex['min_reps']}-{ex['max_reps']}\n"
        
        embed.add_field(
            name="Today's Exercises",
            value=exercise_text,
            inline=False
        )
        
        # Quick commands
        embed.add_field(
            name="Commands",
            value=f"• `{ctx.prefix}log [exercise] [weight] [reps]` - Log a set\n"
                  f"• `{ctx.prefix}status` - View progress\n"
                  f"• `{ctx.prefix}end_workout` - Finish workout",
            inline=False
        )
        
        await ctx.send(embed=embed)
    
    @commands.command(name='log_set', aliases=['log', 'ls'])
    async def log_set(self, ctx, exercise_name: str, weight: float, reps: int, 
                     rpe: Optional[float] = None):
        """
        Log a set
        
        Examples:
        !log "bench press" 185 8
        !log "bench press" 185 8 8.5
        """
        # Check for active session
        if ctx.author.id not in self.sessions:
            embed = EmbedBuilder.error(
                "No active workout",
                f"Start one with `{ctx.prefix}start_workout [name]`"
            )
            await ctx.send(embed=embed)
            return
        
        session = self.sessions[ctx.author.id]
        
        # Get user units
        units = self.user_prefs.get_user_units(ctx.author.id)
        
        # Validate inputs
        valid, error = validate_weight(weight, 'kg' if units == 'metric' else 'lbs')
        if not valid:
            await ctx.send(embed=EmbedBuilder.error("Invalid weight", error))
            return
        
        valid, error = validate_reps(reps)
        if not valid:
            await ctx.send(embed=EmbedBuilder.error("Invalid reps", error))
            return
        
        if rpe is not None:
            valid, error = validate_rpe(rpe)
            if not valid:
                await ctx.send(embed=EmbedBuilder.error("Invalid RPE", error))
                return
        
        # Convert weight if needed
        if units == 'metric':
            weight_lbs = UnitConverter.convert_weight(weight, 'kg', 'lbs')
        else:
            weight_lbs = weight
        
        # Get set number
        exercise_lower = exercise_name.lower()
        if exercise_lower not in session['sets_completed']:
            session['sets_completed'][exercise_lower] = []
        
        set_number = len(session['sets_completed'][exercise_lower]) + 1
        
        # Log the set
        self.db.log_set(
            session['id'], exercise_name, set_number,
            weight_lbs, reps, rpe
        )
        
        # Update session
        session['sets_completed'][exercise_lower].append({
            'weight': weight_lbs,
            'reps': reps,
            'rpe': rpe
        })
        
        # Check for PR
        pr_id = self.db.check_and_save_pr(
            ctx.author.id, exercise_name, weight_lbs, reps
        )
        
        # Build response
        weight_display = format_weight(weight, units)
        
        embed = EmbedBuilder.success(
            f"Set {set_number} Logged",
            f"**{exercise_name.title()}**: {weight_display} x {reps} reps"
        )
        
        if rpe:
            embed.add_field(name="RPE", value=str(rpe), inline=True)
        
        if pr_id:
            from ..utils.calculations import calculate_1rm
            e1rm = calculate_1rm(weight_lbs, reps)
            e1rm_display = format_weight(
                e1rm if units == 'imperial' else UnitConverter.convert_weight(e1rm, 'lbs', 'kg'),
                units
            )
            
            embed = EmbedBuilder.personal_record(
                exercise_name.title(),
                weight_display,
                reps,
                e1rm_display
            )
        
        await ctx.send(embed=embed)
    
    @commands.command(name='status', aliases=['current'])
    async def workout_status(self, ctx):
        """Show current workout status"""
        if ctx.author.id not in self.sessions:
            embed = EmbedBuilder.info(
                "No Active Workout",
                f"Start one with `{ctx.prefix}start_workout [name]`"
            )
            await ctx.send(embed=embed)
            return
        
        session = self.sessions[ctx.author.id]
        duration = int((datetime.now() - session['start_time']).seconds / 60)
        
        # Calculate progress
        total_exercises = len(session['exercises'])
        completed = 0
        total_sets = 0
        total_volume = 0
        
        for ex in session['exercises']:
            ex_name = ex['name']
            sets_done = len(session['sets_completed'].get(ex_name, []))
            if sets_done >= ex['sets']:
                completed += 1
            total_sets += sets_done
            
            # Calculate volume
            for set_data in session['sets_completed'].get(ex_name, []):
                total_volume += set_data['weight'] * set_data['reps']
        
        progress_percent = (completed / total_exercises * 100) if total_exercises > 0 else 0
        
        # Create embed
        embed = EmbedBuilder.workout_status(
            session['name'],
            session['id'],
            progress_percent,
            duration
        )
        
        # Add stats
        units = self.user_prefs.get_user_units(ctx.author.id)
        if units == 'metric':
            volume = UnitConverter.convert_weight(total_volume, 'lbs', 'kg')
            volume_str = f"{volume:,.0f} kg"
        else:
            volume_str = f"{total_volume:,.0f} lbs"
        
        embed.add_field(name="Total Sets", value=str(total_sets), inline=True)
        embed.add_field(name="Volume", value=volume_str, inline=True)
        
        # Exercise details
        for ex in session['exercises']:
            ex_name = ex['name']
            sets_done = len(session['sets_completed'].get(ex_name, []))
            target_sets = ex['sets']
            
            status = "✅" if sets_done >= target_sets else "🔄" if sets_done > 0 else "⏳"
            
            field_value = f"Progress: {sets_done}/{target_sets} sets"
            if sets_done > 0:
                last_set = session['sets_completed'][ex_name][-1]
                if units == 'metric':
                    weight = UnitConverter.convert_weight(last_set['weight'], 'lbs', 'kg')
                    field_value += f"\nLast: {weight:.1f}kg x {last_set['reps']}"
                else:
                    field_value += f"\nLast: {last_set['weight']}lbs x {last_set['reps']}"
            
            embed.add_field(
                name=f"{status} {ex_name.title()}",
                value=field_value,
                inline=False
            )
        
        await ctx.send(embed=embed)
    
    @commands.command(name='end_workout', aliases=['end', 'finish'])
    async def end_workout(self, ctx, *, notes: Optional[str] = None):
        """
        End current workout
        
        Example: !end_workout Great session, felt strong
        """
        if ctx.author.id not in self.sessions:
            embed = EmbedBuilder.error(
                "No active workout",
                "You don't have an active workout to end"
            )
            await ctx.send(embed=embed)
            return
        
        session = self.sessions[ctx.author.id]
        
        # Calculate summary
        duration = int((datetime.now() - session['start_time']).seconds / 60)
        total_sets = sum(len(sets) for sets in session['sets_completed'].values())
        total_volume = sum(
            s['weight'] * s['reps'] 
            for sets in session['sets_completed'].values() 
            for s in sets
        )
        
        # End workout in database
        self.db.end_workout(session['id'], notes)
        
        # Remove session
        del self.sessions[ctx.author.id]
        
        # Create summary embed
        embed = discord.Embed(
            title="💪 Workout Complete!",
            description=f"Great job finishing {session['name']}!",
            color=discord.Color.green()
        )
        
        embed.add_field(
            name="Duration",
            value=format_duration(duration),
            inline=True
        )
        
        embed.add_field(
            name="Total Sets",
            value=str(total_sets),
            inline=True
        )
        
        # Volume with units
        units = self.user_prefs.get_user_units(ctx.author.id)
        if units == 'metric':
            volume = UnitConverter.convert_weight(total_volume, 'lbs', 'kg')
            volume_str = f"{volume:,.0f} kg"
        else:
            volume_str = f"{total_volume:,.0f} lbs"
        
        embed.add_field(
            name="Total Volume",
            value=volume_str,
            inline=True
        )
        
        if notes:
            embed.add_field(
                name="Notes",
                value=notes[:200],
                inline=False
            )
        
        await ctx.send(embed=embed)
    
    @commands.command(name='w', aliases=['quick'])
    async def quick_log(self, ctx, *, args: str):
        """
        Quick log shortcut
        
        Examples:
        !w bench 185 8
        !w bench 185 8 8.5
        """
        parts = args.split()
        if len(parts) < 3:
            await ctx.send(embed=EmbedBuilder.error(
                "Invalid format",
                "Use: !w [exercise] [weight] [reps] [optional: rpe]"
            ))
            return
        
        # Find weight position
        weight_idx = None
        for i in range(1, len(parts)):
            try:
                float(parts[i])
                weight_idx = i
                break
            except ValueError:
                continue
        
        if weight_idx is None or weight_idx + 1 >= len(parts):
            await ctx.send(embed=EmbedBuilder.error(
                "Invalid format",
                "Could not parse weight and reps"
            ))
            return
        
        exercise = " ".join(parts[:weight_idx])
        weight = float(parts[weight_idx])
        reps = int(parts[weight_idx + 1])
        rpe = float(parts[weight_idx + 2]) if len(parts) > weight_idx + 2 else None
        
        # Call log_set
        await self.log_set(ctx, exercise, weight, reps, rpe)


async def setup(bot):
    """Setup function for cog"""
    await bot.add_cog(WorkoutCog(bot))