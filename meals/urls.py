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
]