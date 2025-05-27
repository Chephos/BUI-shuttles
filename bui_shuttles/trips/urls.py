from rest_framework import routers
from django.urls import path

from . import views

router = routers.DefaultRouter()
router.register("routes", views.Route, basename="route")
router.register("", views.Trip, basename="trip")

app_name = "trips"
urlpatterns = [
    path(
        "driver/<int:driver_id>/routes/",
        views.DriverRoutes.as_view(),
        name="driver_routes",
    ),
]

urlpatterns += router.urls
