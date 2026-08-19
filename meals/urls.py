from django.urls import path
from . import views

urlpatterns = [
    # Empty path is homepage
    path("", views.home, name="home"),

    # Displays the complete meal catalogue
    path("meals/", views.meal_list, name="meal_list"),
]