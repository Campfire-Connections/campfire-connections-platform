from django.urls import path

from . import views

urlpatterns = [
    path("health/", views.healthcheck, name="healthcheck"),
    path("dashboard/", views.home, name="dashboard"),
]
