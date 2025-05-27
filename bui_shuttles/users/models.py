from typing import ClassVar

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from .managers import UserManager
from bui_shuttles.users import choices
from bui_shuttles.utils.constants import TimeStampModel


class User(AbstractUser, TimeStampModel):
    """
    Default custom user model for BUI shuttles.
    If adding fields that need to be filled at user signup,
    check forms.SignupForm and forms.SocialSignupForms accordingly.
    """

    # First and last name do not cover name patterns around the globe
    # name = CharField(_("Name of User"), blank=True, max_length=255)
    email = models.EmailField(_("email address"), unique=True)
    username = None  # type: ignore[assignment]

    phone_number = models.CharField(max_length=11, unique=True, blank=True)
    account_type = models.CharField(
        _("account type"),
        max_length=25,
        choices=choices.AccountType.choices,
        default=choices.AccountType.student.value,
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects: ClassVar[UserManager] = UserManager()

    def get_absolute_url(self) -> str:
        """Get URL for user's detail view.

        Returns:
            str: URL for user detail.

        """
        return reverse("users:detail", kwargs={"pk": self.id})


class Student(TimeStampModel):
    matric_number = models.CharField(
        _("matric number"), blank=True, max_length=255, unique=True
    )
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="student", null=True
    )


class Driver(TimeStampModel):
    is_available = models.BooleanField(default=False)
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="driver", null=True
    )
    vehicle = models.OneToOneField(
        "Vehicle", on_delete=models.CASCADE, related_name="driver", null=True
    )
    to_route = models.ForeignKey(
        "trips.Route", on_delete=models.CASCADE, null=True, related_name="drivers_to"
    )
    from_route = models.ForeignKey(
        "trips.Route", on_delete=models.CASCADE, null=True, related_name="drivers_from"
    )
    price = models.IntegerField(default=0)  # price in kobo per seat

    # account details
    bank_code = models.CharField(max_length=10, null=True, blank=True)
    bank_account_number = models.CharField(max_length=11, null=True, blank=True)
    bank_account_name = models.CharField(max_length=100, null=True, blank=True)


class Vehicle(TimeStampModel):
    name = models.CharField(max_length=255, unique=True)
    capacity = models.PositiveIntegerField(default=0)
    reg_number = models.CharField(max_length=255, unique=True)
    vehicle_type = models.CharField(max_length=255, choices=choices.VehicleType.choices)


class OTP(TimeStampModel):
    otp_code = models.CharField(max_length=6)
    email = models.EmailField(unique=True)
    is_verified = models.BooleanField(default=False)
