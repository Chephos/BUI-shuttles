from rest_framework import serializers

from bui_shuttles.bookings.models import Booking
from bui_shuttles.bookings import choices


class BookingCreate(serializers.ModelSerializer):
    class Meta:
        model = Booking
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


class BookingList(Booking):
    student = None
