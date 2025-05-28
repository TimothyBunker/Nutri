"""
Main entry point for Workout Bot
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

import discord
from discord.ext import commands

from src.core import config
from src.models import WorkoutDatabase
from src.utils import UserPreferences
from src.cogs.workout import WorkoutCog
from src.cogs.workout_planning import WorkoutPlanningCog
from src.cogs.workout_analytics import WorkoutAnalyticsCog

# Set up logging
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(config.LOG_FILE_WORKOUT),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('WorkoutBot')


class WorkoutBot(commands.Bot):
    """Custom bot class for workout tracking"""
    
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        
        super().__init__(
            command_prefix=config.BOT_PREFIX,
            intents=intents,
            help_command=None  # We'll create a custom help command
        )
        
        # Initialize database
        self.db = WorkoutDatabase(config.WORKOUT_DB_PATH)
        self.db.init_db()
        
        # Initialize user preferences
        self.user_prefs = UserPreferences(self.db)
    
    async def setup_hook(self):
        """Called when bot is starting up"""
        # Load cogs
        await self.add_cog(WorkoutCog(self))
        await self.add_cog(WorkoutPlanningCog(self))
        await self.add_cog(WorkoutAnalyticsCog(self))
        
        logger.info("Cogs loaded successfully")
    
    async def on_ready(self):
        """Called when bot is ready"""
        logger.info(f'{self.user} has connected to Discord!')
        logger.info(f'Bot is in {len(self.guilds)} guilds')
        
        # Set status
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name=f"{config.BOT_PREFIX}help | Workout Tracking"
            )
        )
    
    async def on_command_error(self, ctx, error):
        """Global error handler"""
        if isinstance(error, commands.CommandNotFound):
            return  # Ignore command not found
        
        elif isinstance(error, commands.CommandOnCooldown):
            await ctx.send(
                f"⏱️ Command on cooldown. Try again in {error.retry_after:.1f} seconds.",
                delete_after=5
            )
        
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(
                f"❌ Missing required argument: `{error.param.name}`\n"
                f"Use `{config.BOT_PREFIX}help {ctx.command}` for usage info."
            )
        
        elif isinstance(error, commands.BadArgument):
            await ctx.send(f"❌ Invalid argument: {error}")
        
        elif isinstance(error, commands.CheckFailure):
            await ctx.send("❌ You don't have permission to use this command.")
        
        else:
            logger.error(f"Unhandled error in command {ctx.command}: {error}", exc_info=error)
            await ctx.send(
                "❌ An unexpected error occurred. Please try again later."
            )


def main():
    """Main entry point"""
    # Validate configuration
    if not config.validate_config():
        logger.error("Configuration validation failed")
        sys.exit(1)
    
    # Create and run bot
    bot = WorkoutBot()
    
    try:
        bot.run(config.WORKOUT_BOT_TOKEN)
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()