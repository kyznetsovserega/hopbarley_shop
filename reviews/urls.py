from django.urls import path
from .views import add_review

app_name = "reviews"

urlpatterns = [
    path("add/<slug:slug>/", add_review, name="add"),
]
