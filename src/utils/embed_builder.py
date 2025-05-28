"""
Discord embed builder utilities
"""

import discord
from typing import Optional, List, Tuple
from datetime import datetime


# Color constants
COLORS = {
    'success': 0x00ff00,  # Green
    'error': 0xff0000,    # Red
    'info': 0x0099ff,     # Blue
    'warning': 0xffff00,  # Yellow
    'gold': 0xffd700,     # Gold for PRs/achievements
    'purple': 0x9b59b6,   # Purple for special events
    'orange': 0xff8c00,   # Orange for reminders
}


class EmbedBuilder:
    """Consistent embed creation across bots"""
    
    @staticmethod
    def _create_base_embed(title: str, description: Optional[str] = None, 
                          color: int = COLORS['info']) -> discord.Embed:
        """Create base embed with common properties"""
        embed = discord.Embed(
            title=title,
            description=description,
            color=color,
            timestamp=datetime.utcnow()
        )
        return embed
    
    @staticmethod
    def success(title: str, description: Optional[str] = None, 
                fields: Optional[List[Tuple[str, str, bool]]] = None) -> discord.Embed:
        """Create success embed"""
        embed = EmbedBuilder._create_base_embed(
            f"✅ {title}",
            description,
            COLORS['success']
        )
        
        if fields:
            for name, value, inline in fields:
                embed.add_field(name=name, value=value, inline=inline)
        
        return embed
    
    @staticmethod
    def error(message: str, details: Optional[str] = None) -> discord.Embed:
        """Create error embed"""
        embed = EmbedBuilder._create_base_embed(
            "❌ Error",
            message,
            COLORS['error']
        )
        
        if details:
            embed.add_field(name="Details", value=details, inline=False)
        
        return embed
    
    @staticmethod
    def info(title: str, description: Optional[str] = None, 
             fields: Optional[List[Tuple[str, str, bool]]] = None) -> discord.Embed:
        """Create info embed"""
        embed = EmbedBuilder._create_base_embed(
            f"ℹ️ {title}",
            description,
            COLORS['info']
        )
        
        if fields:
            for name, value, inline in fields:
                embed.add_field(name=name, value=value, inline=inline)
        
        return embed
    
    @staticmethod
    def warning(title: str, message: str, 
                fields: Optional[List[Tuple[str, str, bool]]] = None) -> discord.Embed:
        """Create warning embed"""
        embed = EmbedBuilder._create_base_embed(
            f"⚠️ {title}",
            message,
            COLORS['warning']
        )
        
        if fields:
            for name, value, inline in fields:
                embed.add_field(name=name, value=value, inline=inline)
        
        return embed
    
    @staticmethod
    def achievement(title: str, description: str, 
                   icon: str = "🏆") -> discord.Embed:
        """Create achievement embed"""
        embed = EmbedBuilder._create_base_embed(
            f"{icon} {title}",
            description,
            COLORS['gold']
        )
        
        return embed
    
    @staticmethod
    def personal_record(exercise: str, weight: str, reps: int, 
                       estimated_1rm: str) -> discord.Embed:
        """Create PR embed"""
        embed = EmbedBuilder._create_base_embed(
            "🎉 NEW PERSONAL RECORD!",
            f"**{exercise}**",
            COLORS['gold']
        )
        
        embed.add_field(name="Weight", value=weight, inline=True)
        embed.add_field(name="Reps", value=str(reps), inline=True)
        embed.add_field(name="Est. 1RM", value=estimated_1rm, inline=True)
        
        return embed
    
    @staticmethod
    def meal_logged(food: str, calories: int, meal_id: int) -> discord.Embed:
        """Create meal logged embed"""
        embed = EmbedBuilder._create_base_embed(
            "✅ Meal Logged!",
            f"ID: #{meal_id}",
            COLORS['success']
        )
        
        embed.add_field(name="Food", value=food, inline=False)
        embed.add_field(name="Calories", value=str(calories), inline=True)
        
        return embed
    
    @staticmethod
    def workout_status(workout_name: str, workout_id: int, 
                      progress_percent: float, duration: int) -> discord.Embed:
        """Create workout status embed"""
        # Progress bar
        progress = int(progress_percent / 10)
        progress_bar = "█" * progress + "░" * (10 - progress)
        
        embed = EmbedBuilder._create_base_embed(
            f"🏋️ {workout_name} - Workout #{workout_id}",
            f"{progress_bar} {progress_percent:.0f}%",
            COLORS['info']
        )
        
        embed.add_field(name="Duration", value=f"{duration} min", inline=True)
        
        return embed
    
    @staticmethod
    def daily_summary(date_str: str, calories_data: dict, 
                     targets: dict) -> discord.Embed:
        """Create daily nutrition summary embed"""
        embed = EmbedBuilder._create_base_embed(
            "📊 Daily Summary",
            date_str,
            COLORS['info']
        )
        
        # Calculate percentages
        cal_percent = (calories_data['calories'] / targets['calories'] * 100) if targets['calories'] > 0 else 0
        protein_percent = (calories_data['protein'] / targets['protein'] * 100) if targets['protein'] > 0 else 0
        
        # Progress bars
        cal_bar = "█" * int(cal_percent / 10) + "░" * (10 - int(cal_percent / 10))
        protein_bar = "█" * int(protein_percent / 10) + "░" * (10 - int(protein_percent / 10))
        
        embed.add_field(
            name="Calories",
            value=f"{calories_data['calories']}/{targets['calories']} ({cal_percent:.1f}%)\n{cal_bar}",
            inline=False
        )
        
        embed.add_field(
            name="Protein",
            value=f"{calories_data['protein']:.1f}g/{targets['protein']}g ({protein_percent:.1f}%)\n{protein_bar}",
            inline=False
        )
        
        return embed
    
    @staticmethod
    def help_embed(command_name: str, description: str, 
                  usage: str, examples: List[str]) -> discord.Embed:
        """Create help embed for a command"""
        embed = EmbedBuilder._create_base_embed(
            f"Help: {command_name}",
            description,
            COLORS['info']
        )
        
        embed.add_field(name="Usage", value=f"```{usage}```", inline=False)
        
        if examples:
            examples_text = "\n".join([f"• {ex}" for ex in examples])
            embed.add_field(name="Examples", value=examples_text, inline=False)
        
        return embed
    
    @staticmethod
    def leaderboard(title: str, entries: List[Tuple[str, str, str]]) -> discord.Embed:
        """Create leaderboard embed"""
        embed = EmbedBuilder._create_base_embed(
            f"🏆 {title}",
            None,
            COLORS['gold']
        )
        
        # Add entries (rank, name, value)
        for i, (rank, name, value) in enumerate(entries[:10]):  # Limit to top 10
            medal = "🥇" if i == 0 else "🥈" if i == 1 else "🥉" if i == 2 else f"{i+1}."
            embed.add_field(
                name=f"{medal} {name}",
                value=value,
                inline=False
            )
        
        return embed
    
    @staticmethod
    def paginated_embed(title: str, items: List[str], page: int, 
                       per_page: int = 10) -> discord.Embed:
        """Create paginated embed"""
        total_pages = (len(items) + per_page - 1) // per_page
        start_idx = (page - 1) * per_page
        end_idx = min(start_idx + per_page, len(items))
        
        embed = EmbedBuilder._create_base_embed(
            title,
            f"Page {page}/{total_pages}",
            COLORS['info']
        )
        
        # Add items for current page
        page_items = items[start_idx:end_idx]
        if page_items:
            embed.add_field(
                name="Results",
                value="\n".join(page_items),
                inline=False
            )
        else:
            embed.add_field(
                name="No Results",
                value="No items to display",
                inline=False
            )
        
        embed.set_footer(text=f"Showing {start_idx+1}-{end_idx} of {len(items)} items")
        
        return embed