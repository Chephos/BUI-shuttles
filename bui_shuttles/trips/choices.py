from django.utils.translation import gettext_lazy as _
from django.db import models


class TripStatus(models.TextChoices):
    not_started = "not_started", _("Not Started")
    started = "started", _("Started")
    finished = "finished", _("Finished")

NEXT_STATUS_MAP = {
    "not_started": ["started"],
    "started": ["finished"]
}
