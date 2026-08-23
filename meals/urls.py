from django.urls import path
from . import views

urlpatterns = [
    # Empty path is homepage
    path("", views.home, name="home"),

    # Displays the complete meal catalogue
    path("meals/", views.meal_list, name="meal_list"),

    # The meal ID identifies which meal should be displayed
    path(
        "meals/<int:meal_id>/",
        views.meal_detail,
        name="meal_detail",
    ),

    # Budget page
    path("budget/", views.budget, name="budget"),

    path("planner/", views.planner, name="planner"),

    path(
        "planner/add/<int:meal_id>/",
        views.add_to_planner,
        name="add_to_planner",
    ),

    path(
        "planner/remove/<int:meal_id>/",
        views.remove_from_planner,
        name="remove_from_planner",
    ),

    path("favourites/", views.favourites, name="favourites"),

    path("favourites/add/<int:meal_id>/", views.add_favourite, name="add_favourite"),

    path("favourites/remove/<int:meal_id>/", views.remove_favourite, name="remove_favourite"),

    path(
        "dashboard/",
        views.dashboard,
        name="dashboard",
    ),

    path(
        "preferences/",
        views.preferences,
        name="preferences",
    ),

    path(
        "recommendations/",
        views.recommendations,
        name="recommendations",
    ),
]