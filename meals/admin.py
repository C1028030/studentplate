from django.contrib import admin
from .models import Meal

# Register your models here.
@admin.register(Meal)
class MealAdmin(admin.ModelAdmin):
    # Columns displayed in the admin meal list
    list_display = (
        "name",
        "category",
        "dietary_type",
        "price",
        "prep_time",
        "is_available",
    )

    # Filters to the side of the admin page
    list_filter = (
        "category",
        "dietary_type",
        "is_available",
    )

    # Search bar
    search_fields = (
        "name",
        "description",
    )