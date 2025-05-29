from rest_framework import serializers

from bui_shuttles.wallets import models
from bui_shuttles.bookings.serializers import BookingList


class Paystack(serializers.Serializer):
    event = serializers.CharField(max_length=100, required=True)
    data = serializers.DictField(required=True)


class Transaction(serializers.ModelSerializer):
    booking = BookingList(read_only=True)

    class Meta:
        model = models.Transaction
        fields = [
            "id",
            "amount",
            "status",
            "type",
            "transaction_reference",
            "provider_reference",
            "payment_link",
            "owner",
            "booking",
            "created",
        ]


class TransactionList(serializers.ModelSerializer):
    class Meta:
        model = models.Transaction
        fields = [
            "id",
            "amount",
            "status",
            "type",
        ]
