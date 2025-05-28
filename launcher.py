#!/usr/bin/env python3
"""
Simple launcher for Health & Fitness Discord bots
"""

import os
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

def main():
    """Main launcher"""
    print("🏃 Health & Fitness Discord Bots")
    print("=================================")
    print()
    print("1. Run both bots (interactive)")
    print("2. Run both bots (background)")
    print("3. Run nutrition bot only")
    print("4. Run workout bot only")
    print("5. Setup/Install")
    print("6. Exit")
    print()
    
    while True:
        try:
            choice = input("Select option [1-6]: ").strip()
            
            if choice == "1":
                # Interactive mode
                os.system(f"python {PROJECT_ROOT}/run_bots.py")
                break
            elif choice == "2":
                # Background mode
                os.system(f"python {PROJECT_ROOT}/run_bots.py --background")
                break
            elif choice == "3":
                # Nutrition bot only
                os.system(f"python {PROJECT_ROOT}/nutrition_bot.py")
                break
            elif choice == "4":
                # Workout bot only
                os.system(f"python {PROJECT_ROOT}/workout_bot.py")
                break
            elif choice == "5":
                # Setup
                os.system(f"python {PROJECT_ROOT}/tools/setup.py")
                break
            elif choice == "6":
                print("Goodbye!")
                break
            else:
                print("Invalid choice. Please select 1-6.")
                
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()