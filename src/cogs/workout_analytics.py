"""
Workout analytics and progress tracking cog
"""

import discord
from discord.ext import commands
import matplotlib.pyplot as plt
import io
from datetime import date, timedelta

from ..utils import EmbedBuilder, format_date, format_weight, UnitConverter
from ..utils.calculations import calculate_1rm


class WorkoutAnalyticsCog(commands.Cog, name="Workout Analytics"):
    """Commands for workout analytics and progress tracking"""
    
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db
        self.user_prefs = bot.user_prefs
    
    @commands.command(name='progress')
    async def show_progress(self, ctx, *, exercise_name: str):
        """
        Show progress for an exercise
        
        Example: !progress bench press
        """
        # Get exercise history
        history = self.db.get_exercise_history(ctx.author.id, exercise_name, 90)
        
        if not history:
            embed = EmbedBuilder.info(
                "No Data",
                f"No data found for {exercise_name}"
            )
            await ctx.send(embed=embed)
            return
        
        # Get user units
        units = self.user_prefs.get_user_units(ctx.author.id)
        
        # Prepare data for plotting
        dates = [format_date(h['date']) for h in history]
        weights = []
        e1rms = []
        
        for h in history:
            weight = h['max_weight']
            if units == 'metric':
                weight = UnitConverter.convert_weight(weight, 'lbs', 'kg')
            weights.append(weight)
            
            # Calculate estimated 1RM
            e1rm = calculate_1rm(h['max_weight'], h['total_reps'] / h['total_sets'])
            if units == 'metric':
                e1rm = UnitConverter.convert_weight(e1rm, 'lbs', 'kg')
            e1rms.append(e1rm)
        
        # Create plot
        fig, ax = plt.subplots(figsize=(10, 6))
        
        ax.plot(dates, e1rms, 'b-o', linewidth=2, markersize=8, label='Estimated 1RM')
        
        # Add trend line
        if len(dates) > 2:
            import numpy as np
            x_numeric = list(range(len(dates)))
            z = np.polyfit(x_numeric, e1rms, 1)
            p = np.poly1d(z)
            ax.plot(dates, [p(x) for x in x_numeric], 'r--', alpha=0.8, 
                   label=f'Trend: +{z[0]:.2f} {units}/session')
        
        ax.set_xlabel('Date')
        ax.set_ylabel(f'Estimated 1RM ({units})')
        ax.set_title(f'{exercise_name.title()} Progress')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # Rotate x labels if many dates
        if len(dates) > 10:
            plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
        
        plt.tight_layout()
        
        # Save to buffer
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        plt.close()
        
        # Calculate stats
        improvement = e1rms[-1] - e1rms[0]
        improvement_pct = (improvement / e1rms[0]) * 100 if e1rms[0] > 0 else 0
        
        # Create embed
        embed = discord.Embed(
            title=f"📈 {exercise_name.title()} Progress",
            color=discord.Color.blue()
        )
        
        embed.add_field(
            name="Starting 1RM",
            value=format_weight(e1rms[0], units),
            inline=True
        )
        
        embed.add_field(
            name="Current 1RM",
            value=format_weight(e1rms[-1], units),
            inline=True
        )
        
        embed.add_field(
            name="Total Gain",
            value=f"+{improvement:.1f} {units} ({improvement_pct:.1f}%)",
            inline=True
        )
        
        embed.set_image(url="attachment://progress.png")
        
        file = discord.File(buffer, filename='progress.png')
        await ctx.send(embed=embed, file=file)
    
    @commands.command(name='prs', aliases=['records'])
    async def show_prs(self, ctx):
        """Show all personal records"""
        prs = self.db.get_personal_records(ctx.author.id)
        
        if not prs:
            embed = EmbedBuilder.info(
                "No PRs Yet",
                "Keep training and set some records! 💪"
            )
            await ctx.send(embed=embed)
            return
        
        units = self.user_prefs.get_user_units(ctx.author.id)
        
        embed = discord.Embed(
            title="🏆 Personal Records",
            color=discord.Color.gold()
        )
        
        for pr in prs[:10]:  # Show top 10
            weight = pr['weight']
            e1rm = pr['estimated_1rm']
            
            if units == 'metric':
                weight = UnitConverter.convert_weight(weight, 'lbs', 'kg')
                e1rm = UnitConverter.convert_weight(e1rm, 'lbs', 'kg')
            
            value = f"{format_weight(weight, units)} x {pr['reps']} = "
            value += f"**{e1rm:.0f} {units} 1RM**\n"
            value += f"{pr['date']}"
            
            embed.add_field(
                name=pr['exercise_name'].title(),
                value=value,
                inline=True
            )
        
        await ctx.send(embed=embed)
    
    @commands.command(name='history', aliases=['recent'])
    async def workout_history(self, ctx, days: int = 7):
        """
        Show recent workout history
        
        Example: !history 30
        """
        if days < 1 or days > 365:
            await ctx.send(embed=EmbedBuilder.error(
                "Invalid range",
                "Days must be between 1 and 365"
            ))
            return
        
        # Get workout history
        workouts = self.db.get_workout_history(ctx.author.id, days)
        
        if not workouts:
            embed = EmbedBuilder.info(
                "No Workouts",
                f"No workouts found in the last {days} days"
            )
            await ctx.send(embed=embed)
            return
        
        units = self.user_prefs.get_user_units(ctx.author.id)
        
        embed = discord.Embed(
            title=f"📊 Last {days} Days of Workouts",
            color=discord.Color.blue()
        )
        
        # Summary stats
        total_workouts = len(workouts)
        total_volume = sum(w['total_volume'] or 0 for w in workouts)
        total_time = sum(
            (int(w['end_time'].split(':')[0]) * 60 + int(w['end_time'].split(':')[1]) -
             int(w['start_time'].split(':')[0]) * 60 - int(w['start_time'].split(':')[1]))
            for w in workouts if w['end_time']
        )
        
        if units == 'metric':
            total_volume = UnitConverter.convert_weight(total_volume, 'lbs', 'kg')
        
        summary = f"**Workouts**: {total_workouts}\n"
        summary += f"**Total Time**: {total_time//60}h {total_time%60}m\n"
        summary += f"**Total Volume**: {total_volume:,.0f} {units}"
        
        embed.add_field(name="Summary", value=summary, inline=False)
        
        # Individual workouts
        for workout in workouts[:10]:  # Limit to 10
            date_str = format_date(workout['date'], "%a %m/%d")
            
            # Calculate duration
            if workout['start_time'] and workout['end_time']:
                start_h, start_m = map(int, workout['start_time'].split(':'))
                end_h, end_m = map(int, workout['end_time'].split(':'))
                duration = (end_h * 60 + end_m) - (start_h * 60 + start_m)
                duration_str = f"{duration} min"
            else:
                duration_str = "Not finished"
            
            value = f"⏱️ {duration_str}"
            
            if workout['total_volume']:
                volume = workout['total_volume']
                if units == 'metric':
                    volume = UnitConverter.convert_weight(volume, 'lbs', 'kg')
                value += f" | {volume:,.0f} {units}"
            
            if workout['session_rpe']:
                value += f" | RPE {workout['session_rpe']}"
            
            embed.add_field(
                name=f"{date_str}: {workout['template_name']}",
                value=value,
                inline=False
            )
        
        await ctx.send(embed=embed)
    
    @commands.command(name='volume')
    async def volume_analysis(self, ctx, days: int = 7):
        """
        Analyze training volume by muscle group
        
        Example: !volume 14
        """
        if days < 1 or days > 365:
            await ctx.send(embed=EmbedBuilder.error(
                "Invalid range",
                "Days must be between 1 and 365"
            ))
            return
        
        # Get volume data
        volume_data = self.db.get_volume_by_muscle_group(ctx.author.id, days)
        
        if not volume_data:
            embed = EmbedBuilder.info(
                "No Data",
                f"No training data found for the last {days} days"
            )
            await ctx.send(embed=embed)
            return
        
        # Create pie chart
        muscle_groups = list(volume_data.keys())
        sets = [v['sets'] for v in volume_data.values()]
        
        plt.figure(figsize=(10, 8))
        plt.pie(sets, labels=muscle_groups, autopct='%1.1f%%', startangle=90)
        plt.title(f'{days}-Day Volume Distribution by Muscle Group')
        
        # Save to buffer
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        plt.close()
        
        # Create embed
        embed = discord.Embed(
            title=f"📊 {days}-Day Volume Analysis",
            color=discord.Color.blue()
        )
        
        # Add muscle group breakdown
        total_sets = sum(sets)
        breakdown = ""
        for muscle, data in sorted(volume_data.items(), 
                                  key=lambda x: x[1]['sets'], 
                                  reverse=True):
            percentage = (data['sets'] / total_sets) * 100
            breakdown += f"**{muscle.title()}**: {data['sets']} sets ({percentage:.1f}%)\n"
        
        embed.add_field(
            name="Muscle Group Distribution",
            value=breakdown[:1024],  # Discord limit
            inline=False
        )
        
        embed.set_image(url="attachment://volume.png")
        
        file = discord.File(buffer, filename='volume.png')
        await ctx.send(embed=embed, file=file)


async def setup(bot):
    """Setup function for cog"""
    await bot.add_cog(WorkoutAnalyticsCog(bot))