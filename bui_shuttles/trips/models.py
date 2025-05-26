from django.db import models

from bui_shuttles.utils.constants import TimeStampModel
from bui_shuttles.trips import choices


# Create your models here.
class Route(TimeStampModel):
    name = models.CharField(max_length=255, unique=True)
    stops = models.JSONField()


class Trip(TimeStampModel):
    route = models.ForeignKey("Route", on_delete=models.CASCADE, related_name="trips")
    driver = models.ForeignKey(
        "users.Driver", on_delete=models.CASCADE, related_name="trips"
    )
    available_seats = models.IntegerField()
    status = models.CharField(
        max_length=255,
        choices=choices.TripStatus.choices,
        default=choices.TripStatus.not_started,
    )
    take_off_time = models.DateTimeField()
