from django.db.models import Q
from django.shortcuts import get_object_or_404, render 
from .models import Meal
from decimal import Decimal, InvalidOperation


# Displays the homepage
def home(request):
    return render(request, "meals/home.html")


# Displays the meals stored in the database
def meal_list(request):
    # Read the selected values from the URL
    query = request.GET.get("q", "").strip()
    selected_category = request.GET.get("category", "").strip()
    maximum_price = request.GET.get("max_price", "").strip()
    maximum_time = request.GET.get("max_time", "").strip()

    # Begin with every available meal
    meals = Meal.objects.filter(is_available=True)

    # Retrieve the available categories before filtering the results
    categories = (
        meals.order_by("category")
        .values_list("category", flat=True)
        .distinct()
    )

    # Search by meal name or description
    if query:
        meals = meals.filter(
            Q(name__icontains=query)
            | Q(description__icontains=query)
        )

    # Filter by an exact category
    if selected_category:
        meals = meals.filter(category=selected_category)

    # Filter by maximum price
    if maximum_price:
        try:
            price_value = Decimal(maximum_price)

            if price_value >= 0:
                meals = meals.filter(price__lte=price_value) # The lte in "price__lte" means "less than or equal to"

        except InvalidOperation:
            # Ignore an invalid price instead of crashing
            pass

    # Filter by maximum preparation time
    if maximum_time:
        try:
            time_value = int(maximum_time)

            if time_value >= 0:
                meals = meals.filter(prep_time__lte=time_value)

        except ValueError:
            # Ignore an invalid time instead of crashing
            pass

    meals = meals.order_by("price")

    context = {
        "meals": meals,
        "categories": categories,
        "query": query,
        "selected_category": selected_category,
        "maximum_price": maximum_price,
        "maximum_time": maximum_time,
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
    # Use the saved session value, or £25 if none has been saved
    weekly_budget = request.session.get(
        "weekly_budget",
        "25.00",
    )

    budget_saved = False
    budget_error = ""

    # Process the form when the user selects Save budget
    if request.method == "POST":
        submitted_budget = request.POST.get(
            "weekly_budget",
            "",
        ).strip()

        # Keep the submitted value visible if validation fails
        weekly_budget = submitted_budget

        try:
            budget_value = Decimal(submitted_budget)

            # Only accept a sensible positive budget
            if Decimal("1.00") <= budget_value <= Decimal("500.00"):
                # Sessions cannot reliably store Decimal objects, so save the value as a string
                weekly_budget = f"{budget_value:.2f}"

                request.session["weekly_budget"] = weekly_budget

                budget_saved = True

            else:
                budget_error = (
                    "Enter a weekly budget between £1 and £500."
                )

        except InvalidOperation:
            budget_error = "Enter a valid weekly budget."

    context = {
        "weekly_budget": weekly_budget,
        "budget_saved": budget_saved,
        "budget_error": budget_error,
    }

    return render(request, "meals/budget.html", context)