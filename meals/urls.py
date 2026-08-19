from django.urls import path
from . import views

urlpatterns = [
    # Empty path is homepage
    path("", views.home, name="home"),
]