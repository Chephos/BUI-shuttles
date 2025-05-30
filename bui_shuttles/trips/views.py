from django.utils.translation import gettext_lazy as _

from rest_framework import views, permissions
from rest_framework.response import Response
from rest_framework import filters, mixins, viewsets


from bui_shuttles.trips import (
    serializers,
    models,
    workers,
    permissions as trip_permissions,
    exceptions,
)
from bui_shuttles.users import permissions as user_permissions, choices as user_choices


class Route(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    queryset = models.Route.objects.all().prefetch_related("trips")
    serializer_class = serializers.Route
    permission_classes = [permissions.AllowAny]

    def get_serializer_class(self):
        if self.action == "retrieve":
            return serializers.RouteDetail
        return serializers.Route

    def get_serializer_context(self):
        context = super().get_serializer_context()
        if self.action == "retrieve":
            route = self.get_object()
            filtered_trips = workers.Route.get_route_trips(route)
            context["filtered_trips"] = filtered_trips
        return context

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            self.permission_classes = [permissions.AllowAny]
        self.permission_classes = [user_permissions.IsDriver]
        return super().get_permissions()


class Trip(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = serializers.Trips
    queryset = models.Trip.objects.all()
    permission_classes = [permissions.AllowAny]
    filter_backends = [filters.SearchFilter]
    search_fields = ["route__stops"]

    def get_serializer_class(self):
        if self.action in ["retrieve", "list"]:
            return serializers.Trips
        elif self.action == "update":
            return serializers.TripUpdate
        elif self.action == "create":
            return serializers.TripCreate

    def get_serializer_context(self):
        context = super().get_serializer_context()
        if self.action == "create":
            context["driver_routes"] = [
                value["id"]
                for value in workers.Route.get_driver_routes(
                    self.request.user.driver
                ).values()
            ]
        if self.action == "update":
            context["trip"] = self.get_object()
        return context

    def get_permissions(self):
        if self.action in ["retrieve", "list"]:
            self.permission_classes = [permissions.AllowAny]
        elif self.action == "create":
            self.permission_classes = [user_permissions.IsDriver]
        elif self.action == "update":
            self.permission_classes = [trip_permissions.IsOwner]

        return super().get_permissions()

    def get_queryset(self):
        user = self.request.user
        if self.action == "list":
            if user.is_authenticated:
                if user.account_type == user_choices.AccountType.driver.value:
                    return workers.Trip.get_driver_trips(user.driver)
            return workers.Trip.get_available_trips()
        return super().get_queryset()

    def perform_create(self, serializer):
        if not self.request.user.driver.vehicle:
            raise exceptions.VehicleRequired

        try:
            workers.Trip.create_trip(
                route_id=serializer.validated_data["route"],
                driver=self.request.user.driver,
                available_seats=self.request.user.driver.vehicle.capacity,
                take_off_time=serializer.validated_data["take_off_time"],
            )
        except ValueError as e:
            raise exceptions.TimeBookedForATrip


class DriverRoutes(views.APIView):  # when driver wants to create trips
    permission_classes = [user_permissions.IsDriver]

    def get(self, request, *args, **kwargs):
        routes = workers.Route.get_driver_routes(request.user.driver)
        return Response(routes)
