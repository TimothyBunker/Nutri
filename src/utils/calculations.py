"""
Calculation utilities for fitness metrics
"""

from typing import Tuple


def calculate_1rm(weight: float, reps: int) -> float:
    """
    Calculate estimated 1RM using Epley formula
    
    Args:
        weight: Weight lifted
        reps: Number of repetitions
    
    Returns:
        Estimated 1 rep max
    """
    if reps == 1:
        return weight
    return weight * (1 + reps / 30)


def calculate_wilks_score(total: float, bodyweight: float, is_male: bool) -> float:
    """
    Calculate Wilks score for powerlifting
    
    Args:
        total: Total weight lifted (squat + bench + deadlift)
        bodyweight: Lifter's bodyweight in kg
        is_male: True if male, False if female
    
    Returns:
        Wilks score
    """
    if is_male:
        # Male coefficients
        a = -216.0475144
        b = 16.2606339
        c = -0.002388645
        d = -0.00113732
        e = 7.01863E-06
        f = -1.291E-08
    else:
        # Female coefficients
        a = 594.31747775582
        b = -27.23842536447
        c = 0.82112226871
        d = -0.00930733913
        e = 4.731582E-05
        f = -9.054E-08
    
    coefficient = 500 / (a + b * bodyweight + c * bodyweight**2 + 
                        d * bodyweight**3 + e * bodyweight**4 + f * bodyweight**5)
    
    return total * coefficient


def calculate_dots_score(total: float, bodyweight: float, is_male: bool) -> float:
    """
    Calculate DOTS score (newer alternative to Wilks)
    
    Args:
        total: Total weight lifted
        bodyweight: Lifter's bodyweight in kg
        is_male: True if male, False if female
    
    Returns:
        DOTS score
    """
    if is_male:
        denominator = -0.0000010930 * bodyweight**4 + 0.0007391293 * bodyweight**3 - 0.1918759221 * bodyweight**2 + 24.0900756 * bodyweight - 307.75076
    else:
        denominator = -0.0000010706 * bodyweight**4 + 0.0005158568 * bodyweight**3 - 0.1126655495 * bodyweight**2 + 13.6175032 * bodyweight - 57.96288
    
    return total * (500 / denominator)


def calculate_bmr(weight_kg: float, height_cm: float, age: int, is_male: bool) -> float:
    """
    Calculate Basal Metabolic Rate using Mifflin-St Jeor equation
    
    Args:
        weight_kg: Weight in kilograms
        height_cm: Height in centimeters
        age: Age in years
        is_male: True if male, False if female
    
    Returns:
        BMR in calories per day
    """
    if is_male:
        return 10 * weight_kg + 6.25 * height_cm - 5 * age + 5
    else:
        return 10 * weight_kg + 6.25 * height_cm - 5 * age - 161


def calculate_tdee(bmr: float, activity_level: str) -> float:
    """
    Calculate Total Daily Energy Expenditure
    
    Args:
        bmr: Basal Metabolic Rate
        activity_level: One of 'sedentary', 'light', 'moderate', 'active', 'very_active'
    
    Returns:
        TDEE in calories per day
    """
    multipliers = {
        'sedentary': 1.2,
        'light': 1.375,
        'moderate': 1.55,
        'active': 1.725,
        'very_active': 1.9
    }
    
    return bmr * multipliers.get(activity_level, 1.55)


def calculate_macro_calories(protein: float, carbs: float, fats: float) -> int:
    """
    Calculate total calories from macronutrients
    
    Args:
        protein: Grams of protein
        carbs: Grams of carbohydrates
        fats: Grams of fats
    
    Returns:
        Total calories
    """
    return int((protein * 4) + (carbs * 4) + (fats * 9))


def calculate_macro_percentages(protein: float, carbs: float, fats: float) -> Tuple[float, float, float]:
    """
    Calculate macro percentages from grams
    
    Args:
        protein: Grams of protein
        carbs: Grams of carbohydrates
        fats: Grams of fats
    
    Returns:
        Tuple of (protein%, carbs%, fats%)
    """
    total_calories = calculate_macro_calories(protein, carbs, fats)
    
    if total_calories == 0:
        return 0.0, 0.0, 0.0
    
    protein_pct = (protein * 4 / total_calories) * 100
    carbs_pct = (carbs * 4 / total_calories) * 100
    fats_pct = (fats * 9 / total_calories) * 100
    
    return protein_pct, carbs_pct, fats_pct


def parse_rep_range(rep_range: str) -> Tuple[int, int]:
    """
    Parse rep range string
    
    Args:
        rep_range: String like '8-10' or '8'
    
    Returns:
        Tuple of (min_reps, max_reps)
    """
    if '-' in rep_range:
        parts = rep_range.split('-')
        return int(parts[0]), int(parts[1])
    else:
        reps = int(rep_range)
        return reps, reps


def calculate_volume_load(sets: list) -> float:
    """
    Calculate total volume load from sets
    
    Args:
        sets: List of dicts with 'weight' and 'reps' keys
    
    Returns:
        Total volume load
    """
    return sum(s['weight'] * s['reps'] for s in sets)


def estimate_workout_calories(duration_minutes: int, workout_type: str = 'weights') -> int:
    """
    Estimate calories burned during workout
    
    Args:
        duration_minutes: Workout duration in minutes
        workout_type: Type of workout ('weights', 'cardio', 'hiit')
    
    Returns:
        Estimated calories burned
    """
    calories_per_minute = {
        'weights': 5,
        'cardio': 8,
        'hiit': 10,
        'yoga': 3,
        'walking': 4,
        'running': 12
    }
    
    return duration_minutes * calories_per_minute.get(workout_type, 5)