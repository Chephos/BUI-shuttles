from django.utils.translation import gettext_lazy as _
from django.db import models


class AccountType(models.TextChoices):
    student = "student", _("Student")
    admin = "admin", _("Admin")
    driver = "driver", _("Driver")

class VehicleType(models.TextChoices):
    cab = "cab", _("Cab")
    sienna = "sienna", _("Sienna")
    bus = "bus", _("Bus")


