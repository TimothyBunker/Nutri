"""
Unit conversion utilities
"""

from typing import Union


# Conversion factors
CONVERSIONS = {
    'lbs_to_kg': 0.453592,
    'kg_to_lbs': 2.20462,
    'inches_to_cm': 2.54,
    'cm_to_inches': 0.393701,
    'miles_to_km': 1.60934,
    'km_to_miles': 0.621371,
    'feet_to_meters': 0.3048,
    'meters_to_feet': 3.28084,
}


class UnitConverter:
    """Handle metric/imperial conversions"""
    
    @staticmethod
    def convert_weight(value: float, from_unit: str, to_unit: str) -> float:
        """Convert weight between units"""
        if from_unit == to_unit:
            return value
        
        # Normalize unit names
        from_unit = from_unit.lower().rstrip('s')  # Remove plural
        to_unit = to_unit.lower().rstrip('s')
        
        if from_unit in ['lb', 'lbs', 'pound'] and to_unit in ['kg', 'kilogram']:
            return value * CONVERSIONS['lbs_to_kg']
        elif from_unit in ['kg', 'kilogram'] and to_unit in ['lb', 'lbs', 'pound']:
            return value * CONVERSIONS['kg_to_lbs']
        
        raise ValueError(f"Unknown weight conversion: {from_unit} to {to_unit}")
    
    @staticmethod
    def convert_height(value: float, from_unit: str, to_unit: str) -> float:
        """Convert height between units"""
        if from_unit == to_unit:
            return value
        
        from_unit = from_unit.lower()
        to_unit = to_unit.lower()
        
        if from_unit in ['inches', 'inch', 'in'] and to_unit in ['cm', 'centimeters']:
            return value * CONVERSIONS['inches_to_cm']
        elif from_unit in ['cm', 'centimeters'] and to_unit in ['inches', 'inch', 'in']:
            return value * CONVERSIONS['cm_to_inches']
        elif from_unit in ['feet', 'ft'] and to_unit in ['meters', 'm']:
            return value * CONVERSIONS['feet_to_meters']
        elif from_unit in ['meters', 'm'] and to_unit in ['feet', 'ft']:
            return value * CONVERSIONS['meters_to_feet']
        
        raise ValueError(f"Unknown height conversion: {from_unit} to {to_unit}")
    
    @staticmethod
    def convert_distance(value: float, from_unit: str, to_unit: str) -> float:
        """Convert distance between units"""
        if from_unit == to_unit:
            return value
        
        from_unit = from_unit.lower()
        to_unit = to_unit.lower()
        
        if from_unit in ['miles', 'mi'] and to_unit in ['km', 'kilometers']:
            return value * CONVERSIONS['miles_to_km']
        elif from_unit in ['km', 'kilometers'] and to_unit in ['miles', 'mi']:
            return value * CONVERSIONS['km_to_miles']
        
        raise ValueError(f"Unknown distance conversion: {from_unit} to {to_unit}")
    
    @staticmethod
    def feet_inches_to_inches(feet: int, inches: int) -> float:
        """Convert feet and inches to total inches"""
        return feet * 12 + inches
    
    @staticmethod
    def inches_to_feet_inches(total_inches: float) -> tuple:
        """Convert total inches to feet and inches"""
        feet = int(total_inches // 12)
        inches = int(total_inches % 12)
        return feet, inches
    
    @staticmethod
    def parse_height_string(height_str: str) -> float:
        """
        Parse height string and return value in inches
        Accepts formats: "5'10"", "5ft 10in", "70", "178cm"
        """
        import re
        
        # Check for feet and inches format
        feet_inches_pattern = r"(\d+)'?\s*(?:ft)?\s*(\d+)?\"?(?:in)?"
        match = re.match(feet_inches_pattern, height_str)
        if match:
            feet = int(match.group(1))
            inches = int(match.group(2)) if match.group(2) else 0
            return UnitConverter.feet_inches_to_inches(feet, inches)
        
        # Check for cm
        if 'cm' in height_str.lower():
            cm_value = float(re.findall(r'\d+\.?\d*', height_str)[0])
            return UnitConverter.convert_height(cm_value, 'cm', 'inches')
        
        # Check for meters
        if 'm' in height_str.lower() and 'cm' not in height_str.lower():
            m_value = float(re.findall(r'\d+\.?\d*', height_str)[0])
            return UnitConverter.convert_height(m_value * 100, 'cm', 'inches')
        
        # Assume inches if just a number
        try:
            return float(height_str)
        except ValueError:
            raise ValueError(f"Cannot parse height: {height_str}")
    
    @staticmethod
    def celsius_to_fahrenheit(celsius: float) -> float:
        """Convert Celsius to Fahrenheit"""
        return (celsius * 9/5) + 32
    
    @staticmethod
    def fahrenheit_to_celsius(fahrenheit: float) -> float:
        """Convert Fahrenheit to Celsius"""
        return (fahrenheit - 32) * 5/9
    
    @staticmethod
    def get_weight_unit(unit_system: str) -> str:
        """Get weight unit for unit system"""
        return 'kg' if unit_system == 'metric' else 'lbs'
    
    @staticmethod
    def get_height_unit(unit_system: str) -> str:
        """Get height unit for unit system"""
        return 'cm' if unit_system == 'metric' else 'inches'
    
    @staticmethod
    def get_distance_unit(unit_system: str) -> str:
        """Get distance unit for unit system"""
        return 'km' if unit_system == 'metric' else 'miles'