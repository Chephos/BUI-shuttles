from rest_framework import serializers
from django.utils import timezone

from bui_shuttles.trips import models
from bui_shuttles.trips import choices
from bui_shuttles.bookings import serializers as booking_serializers

class Route(serializers.ModelSerializer):
    class Meta:
        model = models.Route
        fields = ["id", "name", "stops"]

class Trips(serializers.ModelSerializer):
    route = Route()
    bookings = booking_serializers.Booking(many=True, read_only=True)
    class Meta:
        model = models.Trip
        fields = ["id", "route", "driver", "available_seats", "status", "take_off_time", "bookings"]


class TripCreate(serializers.ModelSerializer):
    class Meta:
        model = models.Trip
        fields = ["route", "take_off_time"]

    def validate_take_off_time(self, value):
        if value < timezone.now():
            raise serializers.ValidationError("Take off time cannot be in the past.")
        return value
    
    def validate_route(self, value):
        driver_routes = self.context.get("driver_routes", [])
        if value.id not in driver_routes:
            raise serializers.ValidationError("You can only create trips for your routes.")
        return value


class TripUpdate(serializers.ModelSerializer):
    class Meta:
        model = models.Trip
        fields = ["status", "take_off_time"]

    def validate_take_off_time(self, value):
        if value < timezone.now():
            raise serializers.ValidationError("Take off time cannot be in the past.")
        return value

    def update(self, instance, validated_data):
        new_status = validated_data.get("status")
        if new_status not in choices.NEXT_STATUS_MAP[instance.status]:
            raise serializers.ValidationError(
                f"You cannot move from {instance.status} to {new_status}"
            )
        return super().update(instance, validated_data)





class Trip(serializers.ModelSerializer):
    class Meta:
        model = models.Trip
        fields = ["id", "driver", "available_seats", "status", "take_off_time"]


class RouteDetail(serializers.ModelSerializer):
    trips = Trip(many=True, read_only=True)

    class Meta:
        model = models.Route
        fields = ["id", "name", "stops", "trips"]

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        filtered_trips = self.context.get("filtered_trips")
        if filtered_trips is not None:
            rep["trips"] = Trip(filtered_trips, many=True).data
        return rep
