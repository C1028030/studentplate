from django.db.models import Q
from django.shortcuts import get_object_or_404, render 
from .models import Meal


# Displays the homepage
def home(request):
    return render(request, "meals/home.html")


# Displays the meals stored in the database
def meal_list(request):
    # Read the search query from the page URL
    query = request.GET.get("q", "").strip()

    # Begin with every available meal
    meals = Meal.objects.filter(is_available=True)

    # Search the name and description when a query is provided
    if query:
        meals = meals.filter(
            Q(name__icontains=query)
            | Q(description__icontains=query)
        )

    # Display the cheapest meals first
    meals = meals.order_by("price")

    context = {
        "meals": meals,
        "query": query,
    }

    return render(request, "meals/meal_list.html", context)

# Displays complete information for one meal
def meal_detail(request, meal_id):
    meal = get_object_or_404(
        Meal,
        id=meal_id,
        is_available=True,
    )

    context = {
        "meal": meal,
    }

    return render(request, "meals/meal_detail.html", context)

# Displays the weekly budget calculator
def budget(request):
    return render(request, "meals/budget.html")