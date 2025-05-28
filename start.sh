#!/bin/bash
# Quick start script for Health & Fitness Discord Bots

echo "🏃 Health & Fitness Bot Launcher"
echo "================================"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  No .env file found. Creating from template..."
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo "✅ Created .env file. Please edit it and add your bot tokens."
        echo "   Edit .env and add:"
        echo "   - NUTRITION_BOT_TOKEN=your_token_here"
        echo "   - WORKOUT_BOT_TOKEN=your_token_here"
        exit 1
    else
        echo "❌ No .env.example file found."
        exit 1
    fi
fi

# Check if requirements are installed
echo "📦 Checking dependencies..."
python3 -m pip install -q -r requirements.txt

# Run migration if databases exist
if [ -f "nutrition.db" ] || [ -f "workout.db" ]; then
    echo "📊 Found existing databases. Running migration check..."
    python3 migrate.py --auto
fi

# Start the bot manager
echo ""
echo "🚀 Starting bots..."
echo "   Press Ctrl+C to stop"
echo "   Type 'help' for commands"
echo ""

python3 run_bots.py "$@"