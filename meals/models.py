from django.contrib import admin
from django.db import models

# Create your models here.
class Meal(models.Model):

    # Options used by the dietary-type field
    DIETARY_CHOICES = [
        ("standard", "No specific diet"),
        ("vegetarian", "Vegetarian"),
        ("vegan", "Vegan"),
    ]

    # Basic meal information
    name = models.CharField(max_length=150)
    category = models.CharField(max_length=50)

    dietary_type = models.CharField(
        max_length=20,
        choices=DIETARY_CHOICES,
        default="standard",
    )
    
    description = models.TextField()

    # Cost and preparation information
    price = models.DecimalField(
        max_digits=5,
        decimal_places=2
    )
    prep_time = models.PositiveBigIntegerField(
        help_text="Preparation time in minutes"
    )

    # Basic nutritional information
    calories = models.PositiveIntegerField()
    protein = models.PositiveIntegerField(
        help_text="Protein in grams"
    )

    # Ingredients are temporarily stored as one block of text
    ingredients = models.TextField()

    # Controls whether the meal appears quickly
    is_available = models.BooleanField(default=True)

    def __str__(self):
        # Controls how the meal is labelled in Django admin
        return self.name