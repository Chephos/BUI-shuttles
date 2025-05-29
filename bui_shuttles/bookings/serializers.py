from rest_framework import serializers

from bui_shuttles.bookings import models
from bui_shuttles.bookings import choices


class BookingCreate(serializers.ModelSerializer):
    class Meta:
        model = models.Booking
        fields = ["trip"]


class Booking(serializers.ModelSerializer):
    student = serializers.SerializerMethodField()
    amount = serializers.IntegerField()
    status = serializers.ChoiceField(choices=choices.BookingStatus.choices)

    class Meta:
        model = models.Booking
        fields = ["id", "trip", "amount", "status", "student"]

    def get_student(self, obj):

        return {
            "id": obj.booker.id,
            "name": obj.booker.user.first_name + " " + obj.booker.user.last_name,
            "email": obj.booker.user.email,
        }


class BookingList(serializers.ModelSerializer):
    class Meta:
        model = models.Booking
        fields = ["id", "trip", "amount", "status"]
