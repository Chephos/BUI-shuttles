from django.db import models


class BookingStatus(models.TextChoices):
    """Booking status choices."""

    pending = "pending", "pending"
    completed = "completed", "completed"
    failed = "failed", "failed"
