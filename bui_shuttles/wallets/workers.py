import hmac
import json
import uuid
import hashlib

import redis
from django.conf import settings
from django.db import transaction

from bui_shuttles.wallets import models, choices
from bui_shuttles.services.paystack import PaystackService
from bui_shuttles.bookings import workers as booking_workers, choices as booking_choices
from bui_shuttles.users import workers as user_workers
from bui_shuttles.trips import workers as trip_workers


REDIS = redis.from_url(settings.REDIS_URL, decode_responses=True)
ONE_DAY_IN_SECONDS = 60 * 60 * 24


class Transaction:
    model = models.Transaction

    @classmethod
    def generate_reference(cls) -> str:
        """
        Generates transaction reference
        :return: unique reference string
        """
        return uuid.uuid4().hex

    @classmethod
    def create_transaction(cls, amount, type, owner, booking, for_driver=False):

        ref = cls.generate_reference()
        if not for_driver:
            paystack_payment = PaystackService().initialize_transaction(
                amount,
                owner.email,
                ref,
                metadata={
                    "transaction_type": type,
                    "driver": booking.trip.driver.user.email,
                    "booking_id": booking.id,
                },
            )

            return cls.model.objects.create(
                amount=amount,
                type=type,
                transaction_reference=ref,
                owner=owner,
                provider_reference=paystack_payment.reference,
                payment_link=paystack_payment.authorization_url,
                booking=booking,
            )
        return cls.model.objects.create(
            amount=amount,
            type=type,
            transaction_reference=ref,
            status=choices.TransactionStatus.successful.value,
            owner=owner,
            booking=booking,
        )

    @classmethod
    def complete_transaction(cls, transaction_ref: str, new_status: str):
        with transaction.atomic():
            trans = cls.model.objects.get(transaction_reference=transaction_ref)
            trans.status = new_status
            trans.save()
            return trans

    @classmethod
    def get_transactions(cls, user):
        """
        Get all transactions for a user
        :param user: User object
        :return: QuerySet of transactions
        """
        return (
            cls.model.objects.filter(owner=user)
            .order_by("-created")
            .select_related("booking")
        )


class Paystack:
    @staticmethod
    def generate_signature(request_body: bytes) -> str:
        """
        Generates a hash based on the request body and the paystack secret key
        :param request_body: request body from paystack webhook
        :return: A hash string
        """
        key = settings.PAYSTACK_SECRET_KEY.encode("utf-8")
        digest = hmac.new(key, request_body, digestmod=hashlib.sha512)
        return digest.hexdigest()

    @classmethod
    def get_banks(cls) -> list:
        """
        Get a list of all bank names, codes and slugs
        :return: bank code
        """
        banks = REDIS.get("banks")
        if banks:
            return json.loads(banks)
        else:
            banks_data = PaystackService().get_banks()
            banks = [
                {"name": bank["name"], "code": bank["code"], "slug": bank["slug"]}
                for bank in banks_data
            ]
            REDIS.set("banks", json.dumps(banks))
            REDIS.expire("banks", ONE_DAY_IN_SECONDS)
            return banks

    @classmethod
    def get_account_name(cls, account_number: str, bank_code: str) -> str:
        """
        Get account name from account number and bank code
        :param account_number: account number
        :param bank_code: bank code
        :return: account name
        """
        account_name = REDIS.get(f"{account_number}:{bank_code}")
        if account_name:
            return account_name
        else:
            account_name = PaystackService().get_account_name(account_number, bank_code)
            REDIS.set(f"{account_number}:{bank_code}", account_name)
            REDIS.expire(f"{account_number}:{bank_code}", ONE_DAY_IN_SECONDS)
            return account_name

    @staticmethod
    def process_charge_event(event: str, data: dict) -> None:
        """
        Process charge event from paystack.
        :param event:
        :param data:
        :return:
        """
        if event in ["charge.success"]:

            Transaction.complete_transaction(
                data["reference"], choices.TransactionStatus.successful.value
            )
            Transaction.create_transaction(
                data["amount"],
                choices.TransactionType.credit.value,
                user_workers.User.get_user_by_email(data["metadata"]["driver"]),
                booking_workers.Booking.get_booking_by_id(
                    data["metadata"]["booking_id"]
                ),
                for_driver=True,
            )
            booking_workers.Booking.complete_booking(
                data["metadata"]["booking_id"],
                booking_choices.BookingStatus.completed.value,
            )

        elif event in ["transfer.failed", "transfer.reversed"]:
            try:
                Transaction.complete_transaction(
                    data["reference"], choices.TransactionStatus.failed.value
                )
                failed_booking = booking_workers.Booking.complete_booking(
                    data["metadata"]["booking_id"],
                    booking_choices.BookingStatus.failed.value,
                )
                trip_workers.Trip.occupy_or_free_seat(failed_booking.trip.id, "free")

            except models.Transaction.DoesNotExist:
                pass
