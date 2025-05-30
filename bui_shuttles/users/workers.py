import random


from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone

from rest_framework.authtoken import models as token_models

from bui_shuttles.users import models


class OTP:
    model = models.OTP

    @classmethod
    def _create_user_otp_id(cls, email):
        return f"otp:{email}"

    @classmethod
    def create_otp(cls, **kwargs):
        # Generate 6-digit OTP
        email = kwargs.get("email")
        otp = cls.model.objects.filter(email=email).first()
        if otp:
            if otp.created < (timezone.now() - timezone.timedelta(minutes=5)):
                # If the OTP is older than 5 minutes, generate a new one
                otp.otp_code = str(random.randint(100000, 999999))
                otp.created = timezone.now()
                otp.save()
        else:
            otp_code = str(random.randint(100000, 999999))
            otp = cls.model.objects.create(email=email, otp_code=otp_code)
        return otp.otp_code

    @classmethod
    def get_otp(cls, email):
        otp = cls.model.objects.filter(email=email).first()
        return otp

    @classmethod
    def delete_otp(cls, email):
        cls.get_otp(email).delete()

    @classmethod
    def verify_otp(cls, email, otp):
        stored_otp = cls.get_otp(email)
        if stored_otp and stored_otp.created > (
            timezone.now() - timezone.timedelta(minutes=5)
        ):

            if stored_otp.otp_code == otp:
                stored_otp.is_verified = True
                stored_otp.save()
                return True
        return False

    @classmethod
    def send_otp(cls, email):
        otp = cls.create_otp(email=email)
        # send otp to email

        send_mail(
            "OTP Verification",
            f"omo your OTP is {otp}. please use it within 5 minutes, i saw shege while pushing to production.",
            "efosacharlesabu@gmail.com",
            [email],
            fail_silently=False,
        )
        return True

    @classmethod
    def validate_otp_action(cls, email: str) -> bool:
        """
        Unlinks otp if it is validated
        :param phone_number: str
        :return: bool
        """
        otp = cls.get_otp(email)
        if otp and otp.is_verified:
            otp.delete()
            return True

        return False


class User:

    @classmethod
    def user_exists(cls, email):
        if models.User.objects.filter(email=email).first():
            return True
        return False

    @classmethod
    def get_user_by_email(cls, email):
        user = models.User.objects.filter(email=email).first()
        if user:
            return user
        return None


class Token:
    @classmethod
    def create_token(cls, user):
        token, _ = token_models.Token.objects.get_or_create(user=user)
        return token.key

    @classmethod
    def delete_token(cls, user):
        try:
            token = token_models.Token.objects.get(user=user)
            token.delete()
        except Token.DoesNotExist:
            pass


class Driver:

    @classmethod
    def get_driver_by_id(cls, driver_id):
        driver = models.Driver.objects.filter(id=driver_id).first()
        if driver:
            return driver
        return None

    @classmethod
    def get_available_drivers(cls, route_id):
        return models.Driver.objects.filter(available=True)

    @classmethod
    def verify_bank_account(cls, user, bank_details: dict):
        """
        Verify bank account details
        """
        driver = user.driver
        bank_account_name = bank_details["bank_account_name"].lower()
        # Verify account name matches BVN name
        first, last = user.first_name.lower(), user.last_name.lower()
        for name in [first, last]:  # TODO: handle edgecase for names with hyphens

            if name not in bank_account_name and name != "":
                return False
        return True

    @classmethod
    def add_bank(cls, user, bank_details: dict):
        """
        Add bank details to a user
        """
        driver = user.driver
        driver.bank_code = bank_details["bank_code"]
        driver.bank_account_number = bank_details["bank_account_number"]
        driver.bank_account_name = bank_details["bank_account_name"]
        driver.save()
        return user
