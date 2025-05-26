from django.db import models

from bui_shuttles.wallets import choices
from bui_shuttles.users import models as user_models
from bui_shuttles.utils.constants import TimeStampModel

# Create your models here.
class Transaction(TimeStampModel):
    amount = models.IntegerField(default=0)
    status = models.CharField(
        max_length=10,
        choices=choices.TransactionStatus.choices,
        default=choices.TransactionStatus.pending.value,
    )
    type = models.CharField(
        max_length=20,
        choices=choices.TransactionType.choices,
    )
    transaction_reference = models.CharField(
        max_length=200, blank=True
    )  # Id for internal use
    provider_reference = models.CharField(
        max_length=200, blank=True
    )  # Reference from paystack
    payment_link = models.URLField(blank=True)
    owner = models.ForeignKey(
        user_models.User, on_delete=models.CASCADE, related_name="transactions", null=True
    )
    booking = models.ForeignKey(
        "bookings.Booking", on_delete=models.CASCADE, related_name="transactions", null=True
    )