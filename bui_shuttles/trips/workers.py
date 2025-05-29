from django.utils import timezone

from bui_shuttles.trips import models, choices
from bui_shuttles.users import models as user_models, workers as user_workers


class Trip:
    model = models.Trip

    @classmethod
    def get_available_trips(cls):
        return cls.model.objects.filter(
            status=choices.TripStatus.not_started, take_off_time__gt=timezone.now()
        ).select_related("driver", "route")

    @classmethod
    def get_trip_by_id(cls, trip_id):
        trip = cls.model.objects.filter(id=trip_id).first()
        if trip:
            return trip
        return None

    @classmethod
    def get_bookable_trip(cls, trip_id):
        trip = cls.get_trip_by_id(trip_id)
    
        if not trip:
            return None
        if trip.status not in [
            choices.TripStatus.not_started,
            choices.TripStatus.not_started.value,
        ]:
            return None
        if trip.available_seats <= 0:
            return None
        if trip.take_off_time < timezone.now():
            return None
        
        return trip

    @classmethod
    def occupy_or_free_seat(cls, trip_id, action):
        trip = cls.get_trip_by_id(trip_id)
        if not trip:
            return None
        if action == "occupy":
            trip.available_seats -= 1
        elif action == "free":
            trip.available_seats += 1
        trip.save()
        return trip

    @classmethod
    def create_trip(
        cls, route_id, driver: user_models.Driver, available_seats, take_off_time
    ):
        if cls.model.objects.filter(take_off_time=take_off_time, driver=driver).first():
            # todo: cannot create trip for the same take off time twice
            raise ValueError()
        trip = cls.model.objects.create(
            route=route_id,
            driver=driver,
            available_seats=available_seats,
            take_off_time=take_off_time,
        )
        return trip

    @classmethod
    def get_driver_trips(cls, driver: user_models.Driver):
        return (
            cls.model.objects.filter(driver=driver)
            .select_related("route")
            .order_by("-take_off_time")
            .prefetch_related("bookings")
        )


class Route:
    model = models.Route

    @classmethod
    def get_driver_routes(cls, driver: user_models.Driver):
        driver_obj = user_models.Driver.objects.select_related(
            "to_route", "from_route"
        ).get(id=driver.id)
        routes = {
            "to_route": {
                "id": driver_obj.to_route.id,
                "name": driver_obj.to_route.name,
                "stops": driver_obj.to_route.stops,
            },
            "from_route": {
                "id": driver_obj.from_route.id,
                "name": driver_obj.from_route.name,
                "stops": driver_obj.from_route.stops,
            },
        }
        return routes

    @classmethod
    def get_route_trips(cls, route):
        return route.trips.filter(
            status=choices.TripStatus.not_started.value,
            take_off_time__gt=timezone.now(),
        )
