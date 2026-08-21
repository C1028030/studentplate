from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render 
from .models import Meal
from decimal import Decimal, InvalidOperation

# Days available in weekly planner
DAYS_OF_WEEK = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday,"
]

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
        "days_of_week": DAYS_OF_WEEK,
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

# Displays the meals saved in the weekly planner
def planner(request):
    saved_entries = request.session.get(
        "planner_entries",
        [],
    )

    # Retrieve the relevant meals in one database query
    meal_ids = [
        entry["meal_id"]
        for entry in saved_entries
    ]

    meals = Meal.objects.filter(
        id__in=meal_ids,
        is_available=True,
    )

    # Create a dictionary so meals can be found by their IDs
    meal_lookup = {
        meal.id: meal
        for meal in meals
    }

    planner_entries = []

    # Combine each saved day with its complete meal record
    for entry in saved_entries:
        meal = meal_lookup.get(entry["meal_id"])

        if meal:
            planner_entries.append(
                {
                    "day": entry["day"],
                    "meal": meal,
                }
            )

    # Display entries in weekday order
    planner_entries.sort(
        key=lambda entry: DAYS_OF_WEEK.index(entry["day"])
    )

    context = {
        "planner_entries": planner_entries,
    }

    return render(request, "meals/planner.html", context)


# Adds a meal to a selected day
def add_to_planner(request, meal_id):
    if request.method == "POST":
        meal = get_object_or_404(
            Meal,
            id=meal_id,
            is_available=True,
        )

        selected_day = request.POST.get("day", "")

        # Only accept one of the recognised weekday values
        if selected_day in DAYS_OF_WEEK:
            planner_entries = request.session.get(
                "planner_entries",
                [],
            )

            new_entry = {
                "meal_id": meal.id,
                "day": selected_day,
            }

            # Prevent the same meal being added twice to the same day
            if new_entry not in planner_entries:
                planner_entries.append(new_entry)
                request.session["planner_entries"] = planner_entries
                request.session.modified = True

    return redirect("planner")


# Removes one meal from one day
def remove_from_planner(request, meal_id):
    if request.method == "POST":
        selected_day = request.POST.get("day", "")

        planner_entries = request.session.get(
            "planner_entries",
            [],
        )

        entry_to_remove = {
            "meal_id": meal_id,
            "day": selected_day,
        }

        if entry_to_remove in planner_entries:
            planner_entries.remove(entry_to_remove)
            request.session["planner_entries"] = planner_entries
            request.session.modified = True

    return redirect("planner")