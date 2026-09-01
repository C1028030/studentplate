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
# Displays featured meals and the user's current progress
def home(request):
    # Display the three cheapest available meals
    featured_meals = Meal.objects.filter(
        is_available=True,
    ).order_by("price")[:3]

    # Retrieve the planner entries
    stored_entries = request.session.get(
        "meal_planner",
        [],
    )

    meal_ids = [
        entry["meal_id"]
        for entry in stored_entries
    ]

    available_planner_meals = Meal.objects.filter(
        id__in=meal_ids,
        is_available=True,
    )

    meals_by_id = {
        meal.id: meal
        for meal in available_planner_meals
    }

    valid_planner_entries = [
        entry
        for entry in stored_entries
        if entry["meal_id"] in meals_by_id
    ]

    # Each planner entry counts because the same meal
    # may appear on more than one day
    planned_cost = sum(
        (
            meals_by_id[entry["meal_id"]].price
            for entry in valid_planner_entries
        ),
        Decimal("0.00"),
    )

    # Count available favourites
    favourite_ids = request.session.get(
        "favourite_meals",
        [],
    )

    favourite_count = Meal.objects.filter(
        id__in=favourite_ids,
        is_available=True,
    ).count()

    # Retrieve the saved weekly budget
    saved_budget = request.session.get("weekly_budget")

    has_budget = False
    weekly_budget = Decimal("0.00")
    remaining_budget = Decimal("0.00")
    amount_over_budget = Decimal("0.00")
    is_over_budget = False

    if saved_budget:
        try:
            weekly_budget = Decimal(saved_budget)
            remaining_budget = weekly_budget - planned_cost
            has_budget = True
            is_over_budget = remaining_budget < 0
            amount_over_budget = abs(remaining_budget)

        except InvalidOperation:
            has_budget = False

    context = {
        "featured_meals": featured_meals,
        "planned_meals": len(valid_planner_entries),
        "planned_cost": planned_cost,
        "favourite_count": favourite_count,
        "has_budget": has_budget,
        "weekly_budget": weekly_budget,
        "remaining_budget": remaining_budget,
        "is_over_budget": is_over_budget,
        "amount_over_budget": amount_over_budget,
    }

    return render(request, "meals/home.html", context)


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
# Displays the complete information for one meal
def meal_detail(request, meal_id):
    meal = get_object_or_404(
        Meal,
        id=meal_id,
        is_available=True,
    )

    favourite_ids = request.session.get(
        "favourite_meals",
        [],
    )

    context = {
        "meal": meal,
        "days_of_week": DAYS_OF_WEEK,

        # Controls which favourite button is displayed
        "is_favourite": meal.id in favourite_ids,
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
# Displays the weekly planner and its calculated totals
def planner(request):
    # Retrieve the stored meal/day entries
    stored_entries = request.session.get(
        "meal_planner",
        [],
    )

    meal_ids = [
        entry["meal_id"]
        for entry in stored_entries
    ]

    available_meals = Meal.objects.filter(
        id__in=meal_ids,
        is_available=True,
    )

    # Make each meal accessible through its database ID
    meals_by_id = {
        meal.id: meal
        for meal in available_meals
    }

    planner_entries = []

    for entry in stored_entries:
        meal = meals_by_id.get(entry["meal_id"])

        if meal:
            planner_entries.append(
                {
                    "meal": meal,
                    "day": entry["day"],
                }
            )

    # Display meals in weekday order
    planner_entries.sort(
        key=lambda entry: DAYS_OF_WEEK.index(entry["day"])
    )

    # Calculate the totals for all planned meals
    total_cost = sum(
        (
            entry["meal"].price
            for entry in planner_entries
        ),
        Decimal("0.00"),
    )

    total_calories = sum(
        entry["meal"].calories
        for entry in planner_entries
    )

    total_protein = sum(
        entry["meal"].protein
        for entry in planner_entries
    )

    # Retrieve the saved budget, if one exists
    saved_budget = request.session.get("weekly_budget")

    has_budget = False
    weekly_budget = Decimal("0.00")
    remaining_budget = Decimal("0.00")
    amount_over_budget = Decimal("0.00")
    is_over_budget = False

    if saved_budget:
        try:
            weekly_budget = Decimal(saved_budget)
            has_budget = True

            remaining_budget = weekly_budget - total_cost

            if remaining_budget < 0:
                is_over_budget = True
                amount_over_budget = abs(remaining_budget)

        except InvalidOperation:
            # Ignore an invalid session value
            has_budget = False

    context = {
        "planner_entries": planner_entries,
        "total_cost": total_cost,
        "total_calories": total_calories,
        "total_protein": total_protein,
        "has_budget": has_budget,
        "weekly_budget": weekly_budget,
        "remaining_budget": remaining_budget,
        "amount_over_budget": amount_over_budget,
        "is_over_budget": is_over_budget,
    }

    return render(request, "meals/planner.html", context)


# Adds a selected meal and day to the planner
def add_to_planner(request, meal_id):
    meal = get_object_or_404(
        Meal,
        id=meal_id,
        is_available=True,
    )

    if request.method == "POST":
        selected_day = request.POST.get("day", "")

        if selected_day in DAYS_OF_WEEK:
            planner_entries = request.session.get(
                "meal_planner",
                [],
            )

            new_entry = {
                "meal_id": meal.id,
                "day": selected_day,
            }

            if new_entry not in planner_entries:
                planner_entries.append(new_entry)

                # Save the updated list into the session
                request.session["meal_planner"] = planner_entries
                request.session.modified = True

    return redirect("planner")

# Removes one meal/day entry from the planner
def remove_from_planner(request, meal_id):
    if request.method == "POST":
        selected_day = request.POST.get("day", "")

        planner_entries = request.session.get(
            "meal_planner",
            [],
        )

        # Keep every entry except the selected meal/day combination
        updated_entries = [
            entry
            for entry in planner_entries
            if not (
                entry.get("meal_id") == meal_id
                and entry.get("day") == selected_day
            )
        ]

        request.session["meal_planner"] = updated_entries
        request.session.modified = True

    return redirect("planner")

# Displays user's saved favourite meals
def favourites(request):
    favourite_ids = request.session.get(
        "favourite_meals",
        [],
    )

    available_meals = Meal.objects.filter(
        id__in=favourite_ids,
        is_available=True,
    )

    meals_by_id = {
        meal.id: meal
        for meal in available_meals
    }

    # Preserve the order in which meals were saved
    favourite_meals = [
        meals_by_id[meal_id]
        for meal_id in favourite_ids
        if meal_id in meals_by_id
    ]

    context = {
        "favourite_meals": favourite_meals,
    }

    return render(request, "meals/favourites.html", context)


# Adds one meal to the favourites session
def add_favourite(request, meal_id):
    meal = get_object_or_404(
        Meal,
        id=meal_id,
        is_available=True,
    )

    if request.method == "POST":
        favourite_ids = request.session.get(
            "favourite_meals",
            [],
        )

        if meal.id not in favourite_ids:
            favourite_ids.append(meal.id)

            request.session["favourite_meals"] = favourite_ids
            request.session.modified = True

    return redirect("meal_detail", meal_id=meal.id)


# Removes one meal from the favourites session
# Removes one meal from the favourites session
def remove_favourite(request, meal_id):
    if request.method == "POST":
        favourite_ids = request.session.get(
            "favourite_meals",
            [],
        )

        favourite_ids = [
            saved_id
            for saved_id in favourite_ids
            if saved_id != meal_id
        ]

        request.session["favourite_meals"] = favourite_ids
        request.session.modified = True

        # Decide which page to return to
        return_page = request.POST.get(
            "return_page",
            "meal_detail",
        )

        if return_page == "favourites":
            return redirect("favourites")

    return redirect("meal_detail", meal_id=meal_id)

# Displays a summary of the user's StudentPlate progress
def dashboard(request):
    stored_entries = request.session.get(
        "meal_planner",
        [],
    )

    meal_ids = [
        entry["meal_id"]
        for entry in stored_entries
    ]

    available_meals = Meal.objects.filter(
        id__in=meal_ids,
        is_available=True,
    )

    meals_by_id = {
        meal.id: meal
        for meal in available_meals
    }

    valid_entries = []

    for entry in stored_entries:
        meal = meals_by_id.get(entry["meal_id"])

        if meal:
            valid_entries.append(
                {
                    "meal": meal,
                    "day": entry["day"],
                }
            )

    # Calculate the planner totals
    total_cost = sum(
        (
            entry["meal"].price
            for entry in valid_entries
        ),
        Decimal("0.00"),
    )

    total_calories = sum(
        entry["meal"].calories
        for entry in valid_entries
    )

    total_protein = sum(
        entry["meal"].protein
        for entry in valid_entries
    )

    # Count the number of different planned days
    planned_days = len(
        {
            entry["day"]
            for entry in valid_entries
        }
    )

    # Count available favourite meals
    favourite_ids = request.session.get(
        "favourite_meals",
        [],
    )

    favourite_count = Meal.objects.filter(
        id__in=favourite_ids,
        is_available=True,
    ).count()

    # Compare spending against the saved budget
    saved_budget = request.session.get("weekly_budget")

    has_budget = False
    weekly_budget = Decimal("0.00")
    remaining_budget = Decimal("0.00")
    amount_over_budget = Decimal("0.00")
    is_over_budget = False

    if saved_budget:
        try:
            weekly_budget = Decimal(saved_budget)
            has_budget = True

            remaining_budget = weekly_budget - total_cost

            if remaining_budget < 0:
                is_over_budget = True
                amount_over_budget = abs(remaining_budget)

        except InvalidOperation:
            has_budget = False

    context = {
        "planned_meals": len(valid_entries),
        "planned_days": planned_days,
        "favourite_count": favourite_count,
        "total_cost": total_cost,
        "total_calories": total_calories,
        "total_protein": total_protein,
        "has_budget": has_budget,
        "weekly_budget": weekly_budget,
        "remaining_budget": remaining_budget,
        "amount_over_budget": amount_over_budget,
        "is_over_budget": is_over_budget,
    }

    return render(request, "meals/dashboard.html", context)

# Displays and saves the student's meal preferences
def preferences(request):
    # Default values used before preferences are saved
    saved_preferences = request.session.get(
        "meal_preferences",
        {
            "dietary_type": "any",
            "maximum_price": "3.00",
            "maximum_time": "30",
            "health_goal": "balanced",
            "cuisine_type": "any",
        },
    )

    preference_saved = False
    preference_errors = []

    if request.method == "POST":
        dietary_type = request.POST.get(
            "dietary_type",
            "any",
        )

        cuisine_type = request.POST.get(
            "cuisine_type",
            "any",
        )

        maximum_price = request.POST.get(
            "maximum_price",
            "",
        ).strip()

        maximum_time = request.POST.get(
            "maximum_time",
            "",
        ).strip()

        health_goal = request.POST.get(
            "health_goal",
            "balanced",
        )

        # Validate the dietary selection
        allowed_diets = {
            "any",
            "vegetarian",
            "vegan",
            "halal",
        }

        allowed_cuisines = {
            "any",
            "british",
            "italian",
            "mediterranean",
            "south_asian",
            "east_asian",
            "mexican",
            "international",
        }

        if cuisine_type not in allowed_cuisines:
            preference_errors.append(
                "Select a valid cuisine preference."
            )

        if dietary_type not in allowed_diets:
            preference_errors.append(
                "Select a valid dietary preference."
            )

        # Validate the health goal
        allowed_goals = {
            "balanced",
            "high_protein",
        }

        if health_goal not in allowed_goals:
            preference_errors.append(
                "Select a valid health goal."
            )

        # Validate the maximum price
        try:
            price_value = Decimal(maximum_price)

            if not Decimal("0.50") <= price_value <= Decimal("20.00"):
                preference_errors.append(
                    "Maximum price must be between £0.50 and £20."
                )

        except InvalidOperation:
            preference_errors.append(
                "Enter a valid maximum meal price."
            )

        # Validate the preparation time
        try:
            time_value = int(maximum_time)

            if not 5 <= time_value <= 120:
                preference_errors.append(
                    "Preparation time must be between 5 and 120 minutes."
                )

        except ValueError:
            preference_errors.append(
                "Enter a valid preparation time."
            )

        # Keep the submitted values visible if validation fails
        saved_preferences = {
            "dietary_type": dietary_type,
            "maximum_price": maximum_price,
            "maximum_time": maximum_time,
            "health_goal": health_goal,
            "cuisine_type": cuisine_type,
        }

        if not preference_errors:
            saved_preferences = {
                "dietary_type": dietary_type,
                "cuisine_type": cuisine_type,
                "maximum_price": f"{price_value:.2f}",
                "maximum_time": str(time_value),
                "health_goal": health_goal,
            }

            request.session["meal_preferences"] = saved_preferences
            request.session.modified = True

            preference_saved = True

    context = {
        "preferences": saved_preferences,
        "preference_saved": preference_saved,
        "preference_errors": preference_errors,
    }

    return render(request, "meals/preferences.html", context)

# Displays meals matching the student's saved preferences
def recommendations(request):
    saved_preferences = request.session.get(
        "meal_preferences"
    )

    # Display a setup message if preferences haven't been saved
    if not saved_preferences:
        context = {
            "has_preferences": False,
            "recommendations": [],
        }

        return render(
            request,
            "meals/recommendations.html",
            context,
        )

    try:
        maximum_price = Decimal(
            saved_preferences["maximum_price"]
        )

        maximum_time = int(
            saved_preferences["maximum_time"]
        )

    except (
        InvalidOperation,
        ValueError,
        KeyError,
    ):
        context = {
            "has_preferences": False,
            "recommendations": [],
        }

        return render(
            request,
            "meals/recommendations.html",
            context,
        )

    dietary_type = saved_preferences.get(
        "dietary_type",
        "any",
    )

    cuisine_type = saved_preferences.get(
        "cuisine_type",
        "any",
    )

    health_goal = saved_preferences.get(
        "health_goal",
        "balanced",
    )

    # Start with meals matching the price and time limits
    matching_meals = Meal.objects.filter(
        is_available=True,
        price__lte=maximum_price,
        prep_time__lte=maximum_time,
    )

    # Apply the dietary requirement
    if dietary_type == "vegetarian":
        matching_meals = matching_meals.filter(
            dietary_type__in=[
                "vegetarian",
                "vegan",
            ]
        )

    elif dietary_type == "halal":
        matching_meals = matching_meals.filter(
            is_halal=True
        )

    elif dietary_type == "vegan":
        matching_meals = matching_meals.filter(
            dietary_type="vegan"
        )

    # Apply preferred cuisine
    if cuisine_type != "any":
        matching_meals = matching_meals.filter(
            cuisine_type=cuisine_type
        )

    # A higher-protein goal requires at least 25g protein
    if health_goal == "high_protein":
        matching_meals = matching_meals.filter(
            protein__gte=25
        ).order_by(
            "-protein",
            "price",
        )

    else:
        # Balanced recommendations prioritise affordability
        matching_meals = matching_meals.order_by(
            "price",
            "-protein",
        )

    recommendations = []

    for meal in matching_meals:
        reasons = [
            f"Costs £{meal.price:.2f}",
            f"Ready in {meal.prep_time} minutes",
        ]

        if cuisine_type != "any":
            reasons.append(
                f"Matches your {meal.get_cuisine_type_display()} cuisine preference"
            )

        if meal.dietary_type == "vegetarian":
            reasons.append("Vegetarian")

        elif meal.dietary_type == "vegan":
            reasons.append("Vegan")

        if meal.is_halal:
            reasons.append("Halal-compatible")

        if meal.protein >= 25:
            reasons.append(
                f"{meal.protein}g protein"
            )

        recommendations.append(
            {
                "meal": meal,
                "reasons": reasons,
            }
        )

    context = {
        "has_preferences": True,
        "recommendations": recommendations,
        "preferences": saved_preferences,
        "maximum_price": maximum_price,
        "maximum_time": maximum_time,
        "dietary_type": dietary_type,
        "health_goal": health_goal,
        "cuisine_type": cuisine_type,
    }

    return render(
        request,
        "meals/recommendations.html",
        context,
    )