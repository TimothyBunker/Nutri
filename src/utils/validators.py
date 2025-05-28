"""
Input validation utilities
"""

from typing import Tuple, Optional, Union


# Validation ranges
VALIDATION_LIMITS = {
    'calories': (0, 10000),
    'weight_lbs': (0, 2000),
    'weight_kg': (0, 900),
    'reps': (1, 100),
    'rpe': (1, 10),
    'protein': (0, 500),
    'carbs': (0, 1000),
    'fats': (0, 300),
    'fiber': (0, 100),
    'sodium': (0, 10000),
    'body_fat': (1, 50),
    'height_inches': (36, 96),
    'height_cm': (90, 250),
    'age': (10, 120),
    'rest_seconds': (0, 600),
}


class Validator:
    """Input validation for all bot commands"""
    
    @staticmethod
    def validate_range(value: Union[int, float], range_key: str) -> Tuple[bool, Optional[str]]:
        """Validate if value is within acceptable range"""
        if range_key not in VALIDATION_LIMITS:
            return True, None
        
        min_val, max_val = VALIDATION_LIMITS[range_key]
        if min_val <= value <= max_val:
            return True, None
        
        return False, f"Value must be between {min_val} and {max_val}"
    
    @staticmethod
    def validate_positive(value: Union[int, float]) -> Tuple[bool, Optional[str]]:
        """Validate that value is positive"""
        if value > 0:
            return True, None
        return False, "Value must be positive"
    
    @staticmethod
    def validate_non_negative(value: Union[int, float]) -> Tuple[bool, Optional[str]]:
        """Validate that value is non-negative"""
        if value >= 0:
            return True, None
        return False, "Value cannot be negative"
    
    @staticmethod
    def validate_percentage(value: float) -> Tuple[bool, Optional[str]]:
        """Validate percentage (0-100)"""
        if 0 <= value <= 100:
            return True, None
        return False, "Percentage must be between 0 and 100"
    
    @staticmethod
    def validate_time_format(time_str: str) -> Tuple[bool, Optional[str]]:
        """Validate time format (HH:MM)"""
        import re
        pattern = r'^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$'
        
        if re.match(pattern, time_str):
            return True, None
        return False, "Time must be in HH:MM format (e.g., 14:30)"
    
    @staticmethod
    def validate_date_format(date_str: str) -> Tuple[bool, Optional[str]]:
        """Validate date format (YYYY-MM-DD)"""
        import re
        from datetime import datetime
        
        pattern = r'^\d{4}-\d{2}-\d{2}$'
        
        if not re.match(pattern, date_str):
            return False, "Date must be in YYYY-MM-DD format"
        
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
            return True, None
        except ValueError:
            return False, "Invalid date"
    
    @staticmethod
    def validate_email(email: str) -> Tuple[bool, Optional[str]]:
        """Validate email format"""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        if re.match(pattern, email):
            return True, None
        return False, "Invalid email format"


# Convenience functions for common validations
def validate_calories(calories: int) -> Tuple[bool, Optional[str]]:
    """Validate calorie input"""
    return Validator.validate_range(calories, 'calories')


def validate_weight(weight: float, unit: str = 'lbs') -> Tuple[bool, Optional[str]]:
    """Validate weight input"""
    key = f'weight_{unit}'
    if key not in VALIDATION_LIMITS:
        key = 'weight_lbs'  # Default to lbs
    return Validator.validate_range(weight, key)


def validate_reps(reps: int) -> Tuple[bool, Optional[str]]:
    """Validate repetition count"""
    return Validator.validate_range(reps, 'reps')


def validate_rpe(rpe: Optional[float]) -> Tuple[bool, Optional[str]]:
    """Validate RPE (Rate of Perceived Exertion)"""
    if rpe is None:
        return True, None
    
    # Allow .5 increments
    if rpe % 0.5 != 0:
        return False, "RPE must be in 0.5 increments (e.g., 7, 7.5, 8)"
    
    return Validator.validate_range(rpe, 'rpe')


def validate_macros(protein: float, carbs: float, fats: float) -> Tuple[bool, Optional[str]]:
    """Validate macronutrient values"""
    validations = [
        (protein, 'protein'),
        (carbs, 'carbs'),
        (fats, 'fats')
    ]
    
    for value, macro in validations:
        valid, error = Validator.validate_range(value, macro)
        if not valid:
            return False, f"{macro.capitalize()}: {error}"
    
    return True, None


def validate_body_composition(body_fat: Optional[float] = None, 
                            muscle_mass: Optional[float] = None) -> Tuple[bool, Optional[str]]:
    """Validate body composition measurements"""
    if body_fat is not None:
        valid, error = Validator.validate_range(body_fat, 'body_fat')
        if not valid:
            return False, f"Body fat: {error}"
    
    if muscle_mass is not None:
        valid, error = Validator.validate_percentage(muscle_mass)
        if not valid:
            return False, f"Muscle mass: {error}"
    
    # Validate that total doesn't exceed 100%
    if body_fat is not None and muscle_mass is not None:
        if body_fat + muscle_mass > 100:
            return False, "Body fat + muscle mass cannot exceed 100%"
    
    return True, None


def validate_height(height: float, unit: str = 'inches') -> Tuple[bool, Optional[str]]:
    """Validate height input"""
    key = f'height_{unit}'
    if key not in VALIDATION_LIMITS:
        key = 'height_inches'  # Default to inches
    return Validator.validate_range(height, key)


def validate_rest_time(seconds: int) -> Tuple[bool, Optional[str]]:
    """Validate rest time in seconds"""
    return Validator.validate_range(seconds, 'rest_seconds')


def validate_sets(sets: int) -> Tuple[bool, Optional[str]]:
    """Validate number of sets"""
    if 1 <= sets <= 20:
        return True, None
    return False, "Sets must be between 1 and 20"