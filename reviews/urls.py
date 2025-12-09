from django.urls import path
from .views import add_review

app_name = "reviews"

urlpatterns = [
    path("<slug:slug>/add/", add_review, name="add"),
]
