#!/usr/bin/env python3
"""
Run both Health & Fitness Discord bots simultaneously
"""

import asyncio
import sys
import signal
import logging
import subprocess
import os
import time
from datetime import datetime
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from src.core import config

# Configure logging
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(config.LOG_FILE_MANAGER),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('BotManager')


class BotProcess:
    """Manages a single bot process"""
    
    def __init__(self, name: str, script_path: str):
        self.name = name
        self.script_path = script_path
        self.process = None
        self.restart_count = 0
        self.last_restart = None
    
    def start(self) -> bool:
        """Start the bot process"""
        try:
            logger.info(f"Starting {self.name}...")
            self.process = subprocess.Popen(
                [sys.executable, self.script_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )
            logger.info(f"{self.name} started with PID {self.process.pid}")
            return True
        except Exception as e:
            logger.error(f"Failed to start {self.name}: {e}")
            return False
    
    def stop(self, timeout: int = 5) -> bool:
        """Stop the bot process gracefully"""
        if not self.process or self.process.poll() is not None:
            return True
        
        logger.info(f"Stopping {self.name}...")
        self.process.terminate()
        
        try:
            self.process.wait(timeout=timeout)
            logger.info(f"{self.name} stopped gracefully")
            return True
        except subprocess.TimeoutExpired:
            logger.warning(f"{self.name} didn't stop gracefully, forcing...")
            self.process.kill()
            self.process.wait()
            logger.info(f"{self.name} force stopped")
            return True
    
    def is_running(self) -> bool:
        """Check if process is running"""
        return self.process is not None and self.process.poll() is None
    
    def restart(self) -> bool:
        """Restart the bot process"""
        self.stop()
        time.sleep(2)  # Brief pause before restart
        
        self.restart_count += 1
        self.last_restart = datetime.now()
        
        return self.start()
    
    def get_output(self) -> str:
        """Get recent output from the process"""
        if not self.process or not self.process.stdout:
            return ""
        
        try:
            line = self.process.stdout.readline()
            return line.strip() if line else ""
        except:
            return ""


class BotManager:
    """Manages multiple Discord bots"""
    
    def __init__(self):
        self.bots = {
            'nutrition': BotProcess('Nutrition Bot', 'nutrition_bot.py'),
            'workout': BotProcess('Workout Bot', 'workout_bot.py')
        }
        self.running = False
        self.auto_restart = True
        self.max_restart_attempts = 5
        self.restart_cooldown = 60  # seconds
    
    async def start_all(self):
        """Start all bots"""
        logger.info("Starting all bots...")
        
        for name, bot in self.bots.items():
            if not bot.start():
                logger.error(f"Failed to start {name}")
                return False
        
        self.running = True
        logger.info("All bots started successfully")
        return True
    
    def stop_all(self):
        """Stop all bots"""
        logger.info("Stopping all bots...")
        self.running = False
        
        for name, bot in self.bots.items():
            bot.stop()
        
        logger.info("All bots stopped")
    
    async def monitor_bots(self):
        """Monitor bot processes and restart if needed"""
        while self.running:
            for name, bot in self.bots.items():
                # Check if bot is running
                if not bot.is_running():
                    logger.warning(f"{bot.name} is not running")
                    
                    # Check if we should restart
                    if self.auto_restart and self.should_restart(bot):
                        logger.info(f"Attempting to restart {bot.name}")
                        
                        if bot.restart():
                            logger.info(f"{bot.name} restarted successfully")
                        else:
                            logger.error(f"Failed to restart {bot.name}")
                
                # Log any output
                output = bot.get_output()
                if output:
                    logger.info(f"[{bot.name}] {output}")
            
            await asyncio.sleep(1)
    
    def should_restart(self, bot: BotProcess) -> bool:
        """Determine if bot should be restarted"""
        # Check restart attempts
        if bot.restart_count >= self.max_restart_attempts:
            logger.error(f"{bot.name} exceeded max restart attempts")
            return False
        
        # Check cooldown
        if bot.last_restart:
            elapsed = (datetime.now() - bot.last_restart).seconds
            if elapsed < self.restart_cooldown:
                logger.info(f"Waiting for cooldown ({elapsed}/{self.restart_cooldown}s)")
                return False
        
        return True
    
    def get_status(self) -> dict:
        """Get status of all bots"""
        status = {}
        for name, bot in self.bots.items():
            status[name] = {
                'running': bot.is_running(),
                'pid': bot.process.pid if bot.process else None,
                'restarts': bot.restart_count,
                'last_restart': bot.last_restart
            }
        return status


class InteractiveShell:
    """Interactive command shell for bot management"""
    
    def __init__(self, manager: BotManager):
        self.manager = manager
        self.commands = {
            'help': self.cmd_help,
            'status': self.cmd_status,
            'start': self.cmd_start,
            'stop': self.cmd_stop,
            'restart': self.cmd_restart,
            'logs': self.cmd_logs,
            'backup': self.cmd_backup,
            'quit': self.cmd_quit,
            'exit': self.cmd_quit
        }
    
    async def run(self):
        """Run interactive shell"""
        print("\n🏃 Health & Fitness Bot Manager")
        print("================================")
        print("Type 'help' for available commands\n")
        
        while self.manager.running:
            try:
                # Get user input
                user_input = await asyncio.get_event_loop().run_in_executor(
                    None, input, "bot-manager> "
                )
                
                await self.process_command(user_input.strip())
                
            except EOFError:
                break
            except KeyboardInterrupt:
                print("\nUse 'quit' to exit")
            except Exception as e:
                logger.error(f"Error in shell: {e}")
    
    async def process_command(self, command: str):
        """Process user command"""
        if not command:
            return
        
        parts = command.split()
        cmd = parts[0].lower()
        args = parts[1:] if len(parts) > 1 else []
        
        if cmd in self.commands:
            await self.commands[cmd](args)
        else:
            print(f"Unknown command: {cmd}")
    
    async def cmd_help(self, args):
        """Show help"""
        print("\nAvailable commands:")
        print("  help              - Show this help")
        print("  status            - Show bot status")
        print("  start [bot]       - Start bot(s)")
        print("  stop [bot]        - Stop bot(s)")
        print("  restart [bot]     - Restart bot(s)")
        print("  logs [lines]      - Show recent logs")
        print("  backup            - Backup databases")
        print("  quit/exit         - Exit manager")
        print()
    
    async def cmd_status(self, args):
        """Show bot status"""
        status = self.manager.get_status()
        
        print("\nBot Status:")
        print("-" * 40)
        
        for name, info in status.items():
            status_str = "✅ Running" if info['running'] else "❌ Stopped"
            print(f"{name.title():15} {status_str}")
            
            if info['pid']:
                print(f"{'':15} PID: {info['pid']}")
            
            if info['restarts'] > 0:
                print(f"{'':15} Restarts: {info['restarts']}")
        
        print()
    
    async def cmd_start(self, args):
        """Start bot(s)"""
        if not args:
            # Start all
            await self.manager.start_all()
        else:
            bot_name = args[0].lower()
            if bot_name in self.manager.bots:
                bot = self.manager.bots[bot_name]
                if bot.start():
                    print(f"Started {bot.name}")
                else:
                    print(f"Failed to start {bot.name}")
            else:
                print(f"Unknown bot: {bot_name}")
    
    async def cmd_stop(self, args):
        """Stop bot(s)"""
        if not args:
            # Stop all
            self.manager.stop_all()
        else:
            bot_name = args[0].lower()
            if bot_name in self.manager.bots:
                bot = self.manager.bots[bot_name]
                bot.stop()
                print(f"Stopped {bot.name}")
            else:
                print(f"Unknown bot: {bot_name}")
    
    async def cmd_restart(self, args):
        """Restart bot(s)"""
        if not args:
            # Restart all
            for bot in self.manager.bots.values():
                bot.restart()
            print("All bots restarted")
        else:
            bot_name = args[0].lower()
            if bot_name in self.manager.bots:
                bot = self.manager.bots[bot_name]
                if bot.restart():
                    print(f"Restarted {bot.name}")
                else:
                    print(f"Failed to restart {bot.name}")
            else:
                print(f"Unknown bot: {bot_name}")
    
    async def cmd_logs(self, args):
        """Show recent logs"""
        lines = int(args[0]) if args else 20
        
        try:
            with open(config.LOG_FILE_MANAGER, 'r') as f:
                all_lines = f.readlines()
                recent = all_lines[-lines:]
                
                print(f"\nLast {lines} log entries:")
                print("-" * 60)
                for line in recent:
                    print(line.strip())
                print()
        except FileNotFoundError:
            print("No log file found")
    
    async def cmd_backup(self, args):
        """Backup databases"""
        from src.models import NutritionDatabase, WorkoutDatabase
        
        print("\nCreating backups...")
        
        # Backup nutrition database
        if config.NUTRITION_DB_PATH.exists():
            db = NutritionDatabase(config.NUTRITION_DB_PATH)
            backup_path = db.backup()
            print(f"✅ Nutrition DB: {backup_path}")
        
        # Backup workout database
        if config.WORKOUT_DB_PATH.exists():
            db = WorkoutDatabase(config.WORKOUT_DB_PATH)
            backup_path = db.backup()
            print(f"✅ Workout DB: {backup_path}")
        
        print()
    
    async def cmd_quit(self, args):
        """Quit the manager"""
        print("\nShutting down...")
        self.manager.stop_all()
        self.manager.running = False


async def main():
    """Main entry point"""
    # Validate configuration
    if not config.validate_config():
        logger.error("Configuration validation failed")
        sys.exit(1)
    
    # Create manager
    manager = BotManager()
    
    # Start bots
    if not await manager.start_all():
        logger.error("Failed to start bots")
        sys.exit(1)
    
    # Check for background mode
    if '--background' in sys.argv or '-b' in sys.argv:
        logger.info("Running in background mode")
        # Just monitor
        await manager.monitor_bots()
    else:
        # Interactive mode
        shell = InteractiveShell(manager)
        
        # Run monitoring and shell concurrently
        monitor_task = asyncio.create_task(manager.monitor_bots())
        shell_task = asyncio.create_task(shell.run())
        
        # Wait for either to complete
        done, pending = await asyncio.wait(
            [monitor_task, shell_task],
            return_when=asyncio.FIRST_COMPLETED
        )
        
        # Cancel pending tasks
        for task in pending:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
    
    logger.info("Manager stopped")


def signal_handler(signum, frame):
    """Handle interrupt signals"""
    logger.info(f"Received signal {signum}")
    raise KeyboardInterrupt


if __name__ == "__main__":
    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Windows-specific event loop policy
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nShutdown complete")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)