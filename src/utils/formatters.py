"""
Formatting utilities for display
"""

from datetime import datetime, date
from typing import Union


def format_number(value: float, decimals: int = 1) -> str:
    """Format number with thousands separator"""
    if decimals == 0:
        return f"{value:,.0f}"
    return f"{value:,.{decimals}f}"


def format_weight(value: float, unit: str) -> str:
    """Format weight with unit"""
    if unit in ['kg', 'kilograms']:
        return f"{value:.1f}kg"
    elif unit in ['lbs', 'pounds']:
        return f"{value:.1f}lbs"
    else:
        return f"{value:.1f} {unit}"


def format_height(value: float, unit: str) -> str:
    """Format height with unit"""
    if unit == 'cm':
        return f"{value:.0f}cm"
    elif unit == 'inches':
        # Convert to feet and inches
        feet = int(value // 12)
        inches = int(value % 12)
        return f"{feet}'{inches}\""
    else:
        return f"{value:.1f} {unit}"


def format_duration(minutes: int) -> str:
    """Format duration in human-readable format"""
    if minutes < 60:
        return f"{minutes} min"
    
    hours = minutes // 60
    mins = minutes % 60
    
    if mins == 0:
        return f"{hours}h"
    else:
        return f"{hours}h {mins}m"


def format_date(date_obj: Union[date, str], format: str = "%b %d, %Y") -> str:
    """Format date in readable format"""
    if isinstance(date_obj, str):
        date_obj = datetime.strptime(date_obj, "%Y-%m-%d").date()
    
    return date_obj.strftime(format)


def format_time(time_str: str, format_24h: bool = False) -> str:
    """Format time string"""
    time_obj = datetime.strptime(time_str, "%H:%M")
    
    if format_24h:
        return time_obj.strftime("%H:%M")
    else:
        return time_obj.strftime("%I:%M %p").lstrip('0')


def format_calories(calories: int) -> str:
    """Format calories with 'cal' suffix"""
    return f"{calories:,} cal"


def format_macros(protein: float, carbs: float, fats: float) -> str:
    """Format macros as P/C/F"""
    return f"{protein:.0f}p/{carbs:.0f}c/{fats:.0f}f"


def format_percentage(value: float, total: float) -> str:
    """Format as percentage"""
    if total == 0:
        return "0%"
    
    percentage = (value / total) * 100
    return f"{percentage:.1f}%"


def format_progress_bar(current: float, target: float, length: int = 10) -> str:
    """Create a text progress bar"""
    if target == 0:
        return "░" * length
    
    progress = min(current / target, 1.0)
    filled = int(progress * length)
    
    return "█" * filled + "░" * (length - filled)


def format_rest_timer(seconds: int) -> str:
    """Format rest timer display"""
    minutes = seconds // 60
    secs = seconds % 60
    return f"{minutes}:{secs:02d}"


def format_rpe(rpe: float) -> str:
    """Format RPE value"""
    if rpe is None:
        return "N/A"
    
    # Show .5 values, otherwise show as integer
    if rpe % 1 == 0.5:
        return f"{rpe:.1f}"
    else:
        return f"{int(rpe)}"


def format_volume(volume: float, unit: str = 'lbs') -> str:
    """Format training volume"""
    return f"{format_number(volume, 0)} {unit}"


def format_exercise_name(name: str) -> str:
    """Format exercise name for display"""
    return name.replace('_', ' ').title()