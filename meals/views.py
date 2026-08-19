from django.shortcuts import render

# Homepage
def home(request):
    return render(request, "meals/home.html")

# Displays available meals
def meal_list(request):
    # Temporary sample data for first prototype
    meals = [
        {
            "name": "Chicken and vegetable rice bowl",
            "category": "High protein",
            "description": "A filling meal made with chicken, rice and vegetables.",
            "price": 2.35,
            "prep_time": 25,
        },
        {
            "name": "Spiced chickpea wraps",
            "category": "Vegetarian",
            "description": "Quick wraps containing chickpeas, salad and yoghurt.",
            "price": 1.65,
            "prep_time": 15,
        },
        {
            "name": "Tuna tomato pasta",
            "category": "Under £2",
            "description": "An affordable pasta meal containing tuna and tomatoes",
            "price": 1.90,
            "prep_time": 20,
        },
        {
            "name": "Banana overnight oats",
            "category": "Breakfast",
            "description": "A simple breakfast that can be prepared the night before",
            "price": 0.95,
            "prep_time": 5,
        },
    ]

    # Passes the list to the HTML template
    context = {
        "meals": meals,
    }

    return render(request, "meals/meal_list.html", context)