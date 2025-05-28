# Premade recipes with ingredients and quantities

PREMADE_RECIPES = {
    # Breakfast recipes
    "scrambled_eggs_toast": {
        "name": "Scrambled Eggs with Toast",
        "category": "breakfast",
        "ingredients": [
            {"item": "eggs", "quantity": 2, "unit": "large"},
            {"item": "whole wheat bread", "quantity": 2, "unit": "slices"},
            {"item": "butter", "quantity": 1, "unit": "tablespoon"},
            {"item": "milk", "quantity": 2, "unit": "tablespoons"},
            {"item": "salt", "quantity": 0.25, "unit": "teaspoon"},
            {"item": "black pepper", "quantity": 0.125, "unit": "teaspoon"}
        ]
    },
    "oatmeal_berries": {
        "name": "Oatmeal with Berries",
        "category": "breakfast",
        "ingredients": [
            {"item": "rolled oats", "quantity": 0.5, "unit": "cup"},
            {"item": "water", "quantity": 1, "unit": "cup"},
            {"item": "blueberries", "quantity": 0.5, "unit": "cup"},
            {"item": "strawberries", "quantity": 0.5, "unit": "cup"},
            {"item": "honey", "quantity": 1, "unit": "tablespoon"},
            {"item": "cinnamon", "quantity": 0.25, "unit": "teaspoon"}
        ]
    },
    "greek_yogurt_parfait": {
        "name": "Greek Yogurt Parfait",
        "category": "breakfast",
        "ingredients": [
            {"item": "greek yogurt", "quantity": 1, "unit": "cup"},
            {"item": "granola", "quantity": 0.25, "unit": "cup"},
            {"item": "mixed berries", "quantity": 0.5, "unit": "cup"},
            {"item": "honey", "quantity": 1, "unit": "tablespoon"},
            {"item": "chia seeds", "quantity": 1, "unit": "teaspoon"}
        ]
    },
    "avocado_toast": {
        "name": "Avocado Toast",
        "category": "breakfast",
        "ingredients": [
            {"item": "whole grain bread", "quantity": 2, "unit": "slices"},
            {"item": "avocado", "quantity": 1, "unit": "medium"},
            {"item": "lemon juice", "quantity": 1, "unit": "teaspoon"},
            {"item": "salt", "quantity": 0.25, "unit": "teaspoon"},
            {"item": "red pepper flakes", "quantity": 0.125, "unit": "teaspoon"},
            {"item": "olive oil", "quantity": 1, "unit": "teaspoon"}
        ]
    },
    
    # Lunch recipes
    "chicken_caesar_salad": {
        "name": "Chicken Caesar Salad",
        "category": "lunch",
        "ingredients": [
            {"item": "grilled chicken breast", "quantity": 4, "unit": "ounces"},
            {"item": "romaine lettuce", "quantity": 3, "unit": "cups"},
            {"item": "caesar dressing", "quantity": 2, "unit": "tablespoons"},
            {"item": "parmesan cheese", "quantity": 2, "unit": "tablespoons"},
            {"item": "croutons", "quantity": 0.25, "unit": "cup"},
            {"item": "lemon wedge", "quantity": 1, "unit": "piece"}
        ]
    },
    "turkey_sandwich": {
        "name": "Turkey Sandwich",
        "category": "lunch",
        "ingredients": [
            {"item": "whole wheat bread", "quantity": 2, "unit": "slices"},
            {"item": "sliced turkey", "quantity": 3, "unit": "ounces"},
            {"item": "cheddar cheese", "quantity": 1, "unit": "slice"},
            {"item": "lettuce", "quantity": 2, "unit": "leaves"},
            {"item": "tomato", "quantity": 2, "unit": "slices"},
            {"item": "mustard", "quantity": 1, "unit": "tablespoon"},
            {"item": "mayonnaise", "quantity": 1, "unit": "tablespoon"}
        ]
    },
    "quinoa_bowl": {
        "name": "Mediterranean Quinoa Bowl",
        "category": "lunch",
        "ingredients": [
            {"item": "cooked quinoa", "quantity": 1, "unit": "cup"},
            {"item": "chickpeas", "quantity": 0.5, "unit": "cup"},
            {"item": "cucumber", "quantity": 0.5, "unit": "cup"},
            {"item": "cherry tomatoes", "quantity": 0.5, "unit": "cup"},
            {"item": "feta cheese", "quantity": 2, "unit": "tablespoons"},
            {"item": "olive oil", "quantity": 1, "unit": "tablespoon"},
            {"item": "lemon juice", "quantity": 1, "unit": "tablespoon"},
            {"item": "fresh parsley", "quantity": 2, "unit": "tablespoons"}
        ]
    },
    "tuna_salad": {
        "name": "Tuna Salad",
        "category": "lunch",
        "ingredients": [
            {"item": "canned tuna", "quantity": 1, "unit": "can"},
            {"item": "celery", "quantity": 0.25, "unit": "cup"},
            {"item": "red onion", "quantity": 2, "unit": "tablespoons"},
            {"item": "mayonnaise", "quantity": 2, "unit": "tablespoons"},
            {"item": "dijon mustard", "quantity": 1, "unit": "teaspoon"},
            {"item": "mixed greens", "quantity": 2, "unit": "cups"},
            {"item": "whole wheat crackers", "quantity": 6, "unit": "pieces"}
        ]
    },
    
    # Dinner recipes
    "grilled_salmon": {
        "name": "Grilled Salmon with Vegetables",
        "category": "dinner",
        "ingredients": [
            {"item": "salmon fillet", "quantity": 6, "unit": "ounces"},
            {"item": "broccoli", "quantity": 1, "unit": "cup"},
            {"item": "brown rice", "quantity": 0.5, "unit": "cup"},
            {"item": "olive oil", "quantity": 1, "unit": "tablespoon"},
            {"item": "lemon", "quantity": 0.5, "unit": "piece"},
            {"item": "garlic", "quantity": 2, "unit": "cloves"},
            {"item": "salt", "quantity": 0.5, "unit": "teaspoon"},
            {"item": "black pepper", "quantity": 0.25, "unit": "teaspoon"}
        ]
    },
    "chicken_stir_fry": {
        "name": "Chicken Stir Fry",
        "category": "dinner",
        "ingredients": [
            {"item": "chicken breast", "quantity": 5, "unit": "ounces"},
            {"item": "mixed vegetables", "quantity": 2, "unit": "cups"},
            {"item": "soy sauce", "quantity": 2, "unit": "tablespoons"},
            {"item": "sesame oil", "quantity": 1, "unit": "tablespoon"},
            {"item": "ginger", "quantity": 1, "unit": "teaspoon"},
            {"item": "garlic", "quantity": 2, "unit": "cloves"},
            {"item": "brown rice", "quantity": 0.75, "unit": "cup"},
            {"item": "green onions", "quantity": 2, "unit": "stalks"}
        ]
    },
    "spaghetti_marinara": {
        "name": "Spaghetti with Marinara Sauce",
        "category": "dinner",
        "ingredients": [
            {"item": "whole wheat spaghetti", "quantity": 2, "unit": "ounces"},
            {"item": "marinara sauce", "quantity": 0.75, "unit": "cup"},
            {"item": "ground turkey", "quantity": 4, "unit": "ounces"},
            {"item": "parmesan cheese", "quantity": 2, "unit": "tablespoons"},
            {"item": "olive oil", "quantity": 1, "unit": "tablespoon"},
            {"item": "garlic", "quantity": 2, "unit": "cloves"},
            {"item": "italian seasoning", "quantity": 1, "unit": "teaspoon"},
            {"item": "fresh basil", "quantity": 2, "unit": "tablespoons"}
        ]
    },
    "beef_tacos": {
        "name": "Beef Tacos",
        "category": "dinner",
        "ingredients": [
            {"item": "lean ground beef", "quantity": 4, "unit": "ounces"},
            {"item": "corn tortillas", "quantity": 3, "unit": "small"},
            {"item": "shredded lettuce", "quantity": 0.5, "unit": "cup"},
            {"item": "diced tomatoes", "quantity": 0.25, "unit": "cup"},
            {"item": "shredded cheese", "quantity": 0.25, "unit": "cup"},
            {"item": "sour cream", "quantity": 2, "unit": "tablespoons"},
            {"item": "salsa", "quantity": 2, "unit": "tablespoons"},
            {"item": "taco seasoning", "quantity": 1, "unit": "tablespoon"}
        ]
    },
    
    # Snack recipes
    "hummus_veggies": {
        "name": "Hummus with Vegetables",
        "category": "snack",
        "ingredients": [
            {"item": "hummus", "quantity": 0.25, "unit": "cup"},
            {"item": "baby carrots", "quantity": 1, "unit": "cup"},
            {"item": "cucumber slices", "quantity": 0.5, "unit": "cup"},
            {"item": "bell pepper strips", "quantity": 0.5, "unit": "cup"}
        ]
    },
    "apple_peanut_butter": {
        "name": "Apple with Peanut Butter",
        "category": "snack",
        "ingredients": [
            {"item": "apple", "quantity": 1, "unit": "medium"},
            {"item": "peanut butter", "quantity": 2, "unit": "tablespoons"},
            {"item": "cinnamon", "quantity": 0.125, "unit": "teaspoon"}
        ]
    },
    "trail_mix": {
        "name": "Trail Mix",
        "category": "snack",
        "ingredients": [
            {"item": "almonds", "quantity": 0.25, "unit": "cup"},
            {"item": "cashews", "quantity": 0.25, "unit": "cup"},
            {"item": "raisins", "quantity": 2, "unit": "tablespoons"},
            {"item": "dark chocolate chips", "quantity": 1, "unit": "tablespoon"},
            {"item": "dried cranberries", "quantity": 1, "unit": "tablespoon"}
        ]
    },
    "protein_smoothie": {
        "name": "Protein Smoothie",
        "category": "snack",
        "ingredients": [
            {"item": "protein powder", "quantity": 1, "unit": "scoop"},
            {"item": "banana", "quantity": 1, "unit": "medium"},
            {"item": "almond milk", "quantity": 1, "unit": "cup"},
            {"item": "spinach", "quantity": 1, "unit": "cup"},
            {"item": "frozen berries", "quantity": 0.5, "unit": "cup"},
            {"item": "chia seeds", "quantity": 1, "unit": "tablespoon"}
        ]
    },
    "cheese_crackers": {
        "name": "Cheese and Crackers",
        "category": "snack",
        "ingredients": [
            {"item": "whole grain crackers", "quantity": 10, "unit": "pieces"},
            {"item": "cheddar cheese", "quantity": 2, "unit": "ounces"},
            {"item": "grapes", "quantity": 0.5, "unit": "cup"}
        ]
    }
}

def get_recipe(recipe_id):
    """Get a specific recipe by its ID."""
    return PREMADE_RECIPES.get(recipe_id)

def get_recipes_by_category(category):
    """Get all recipes in a specific category."""
    return {
        recipe_id: recipe 
        for recipe_id, recipe in PREMADE_RECIPES.items() 
        if recipe["category"] == category
    }

def get_all_recipe_names():
    """Get a dictionary of recipe IDs mapped to their display names."""
    return {
        recipe_id: recipe["name"] 
        for recipe_id, recipe in PREMADE_RECIPES.items()
    }

def get_categories():
    """Get all unique recipe categories."""
    return list(set(recipe["category"] for recipe in PREMADE_RECIPES.values()))