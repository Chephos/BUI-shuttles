
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
    first_name = models.CharField(_("first name"), max_length=255)
    last_name = models.CharField(_("last name"), max_length=255)
    email = models.EmailField(_("email address"), unique=True)
    username = None  # type: ignore[assignment]
    matric_number = models.CharField(
        _("matric number"), blank=True, max_length=255, unique=True, null=True
    )
    phone_number = models.CharField(max_length=11, unique=True, blank=True, null=True)
    account_type = models.CharField(_("account type"), max_length=25, choices=choices.AccountType.choices)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects: ClassVar[UserManager] = UserManager()

    def get_absolute_url(self) -> str:
        """Get URL for user's detail view.

        Returns:
            str: URL for user detail.

        """
        return reverse("users:detail", kwargs={"pk": self.id})

class School(TimeStampModel):
    name = models.CharField(max_length=255, unique=True)

class Vehicle(TimeStampModel):
    name = models.CharField(max_length=255, unique=True)
    capacity = models.PositiveIntegerField(default=0)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="vehicles")
    driver = models.ForeignKey(User, on_delete=models.CASCADE, related_name="vehicles")
    reg_number = models.CharField(max_length=255, unique=True)
    vehicle_type = models.CharField(max_length=255, choices=choices.VehicleType.choices)