from rest_framework import serializers

from bui_shuttles.bookings import models
from bui_shuttles.bookings import choices


class BookingCreate(serializers.ModelSerializer):
    class Meta:
        model = models.Booking
        fields = ["trip"]


class Booking(serializers.Serializer):
    student = serializers.SerializerMethodField()
    trip = serializers.IntegerField()
    amount = serializers.IntegerField()
    status = serializers.ChoiceField(choices=choices.BookingStatus.choices)

    def get_student(self, obj):
        return {
            "id": obj.booker.id,
            "name": obj.booker.name,
            "email": obj.booker.email,
        }


class BookingList(serializers.ModelSerializer):
    class Meta:
        model = models.Booking
        fields = ["id", "trip", "amount", "status"]
