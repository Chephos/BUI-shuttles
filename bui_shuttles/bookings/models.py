from django.db import models

from bui_shuttles.utils.constants import TimeStampModel
from bui_shuttles.bookings import choices
from bui_shuttles.users import models as user_models

# Create your models here.


class Booking(TimeStampModel):
    booker = models.ForeignKey(
        user_models.Student, on_delete=models.CASCADE, related_name="bookings"
    )
    trip = models.ForeignKey(
        "trips.Trip", on_delete=models.CASCADE, related_name="bookings"
    )
    amount = models.IntegerField(default=0)
    status = models.CharField(
        max_length=255,
        choices=choices.BookingStatus.choices,
        default=choices.BookingStatus.pending.value,
    )
