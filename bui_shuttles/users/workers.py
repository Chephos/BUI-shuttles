import random
import redis

from django.conf import settings
from django.core.mail import send_mail

from rest_framework.authtoken import models as token_models

from bui_shuttles.users import models


REDIS = redis.from_url(settings.REDIS_URL, decode_responses=True)


class OTP:

    @classmethod
    def _create_user_otp_id(cls, email):
        return f"otp:{email}"

    @classmethod
    def create_otp(cls, **kwargs):
        # Generate 6-digit OTP
        otp = str(random.randint(100000, 999999))
        user_otp_id = cls._create_user_otp_id(kwargs["email"])
        REDIS.hset(user_otp_id, mapping={**kwargs, "otp": otp, "is_validated": 0})
        REDIS.expire(user_otp_id, 300)  # Set expiration time to 5 minutes
        return otp

    @classmethod
    def get_otp(cls, email):
        user_otp_id = cls._create_user_otp_id(email)
        return REDIS.hgetall(user_otp_id)

    @classmethod
    def delete_otp(cls, email):
        user_otp_id = cls._create_user_otp_id(email)
        REDIS.delete(user_otp_id)

    @classmethod
    def verify_otp(cls, email, otp):
        user_otp_id = cls._create_user_otp_id(email)
        stored_otp = REDIS.hget(user_otp_id, "otp")
        if stored_otp == otp:
            REDIS.hset(user_otp_id, "is_validated", 1)
            return cls.get_otp(email)
        return False

    @classmethod
    def send_otp(cls, email):
        otp = cls.create_otp(email=email)
        # send otp to email

        send_mail(
            "OTP Verification",
            f"Your OTP is {otp}.",
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
        user_otp_id = cls._create_user_otp_id(email)
        if REDIS.hexists(user_otp_id, "is_validated"):
            if REDIS.hget(user_otp_id, "is_validated") == "1":
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