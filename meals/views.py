from django.shortcuts import render
from .models import Meal


# Displays the homepage
def home(request):
    return render(request, "meals/home.html")


# Displays the meals stored in the database
def meal_list(request):
    # Retrieve available meals and order them from cheapest to most expensive
    meals = Meal.objects.filter(
        is_available=True
    ).order_by("price")

    context = {
        "meals": meals,
    }

    return render(request, "meals/meal_list.html", context)