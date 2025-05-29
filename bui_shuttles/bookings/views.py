from rest_framework import viewsets, mixins
from rest_framework.response import Response

from bui_shuttles.bookings import serializers, exceptions, workers, permissions
from bui_shuttles.trips import workers as trip_workers, exceptions as trip_exceptions
from bui_shuttles.users import permissions as user_permissions, choices as user_choices
from bui_shuttles.wallets import workers as wallet_workers, choices as wallet_choices

# Create your views here.


class Bookings(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = serializers.BookingCreate
    permission_classes = [user_permissions.IsStudent]

    def get_permissions(self):
        if self.action == "list":
            self.permission_classes = [
                user_permissions.IsDriver | user_permissions.IsStudent
            ]
        elif self.action == "retrieve":
            self.permission_classes = [permissions.IsBooker | permissions.IsBookee]
        else:
            self.permission_classes = [user_permissions.IsStudent]
        return super().get_permissions()

    def get_queryset(self):
        user = self.request.user
        if user.account_type == user_choices.AccountType.student.value:
            return workers.Booking.get_bookings_by_student(user.student)
        elif user.account_type == user_choices.AccountType.driver.value:
            return workers.Booking.get_bookings_for_driver(user.driver)

    def get_serializer_class(self):
        if self.action == "retrieve":
            return serializers.Booking
        elif self.action == "list":
            return serializers.BookingList

        return serializers.BookingCreate

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        response = self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(response, status=201, headers=headers)

    def perform_create(self, serializer):
        trip = trip_workers.Trip.get_bookable_trip(serializer.data["trip"])
        you_booked_already = workers.Booking.get_booking_for_student_by_trip(
            student=self.request.user.student, trip=trip
        )
        if you_booked_already:
            raise exceptions.AlreadyBooked
        if not trip:
            raise trip_exceptions.InvalidTrip
        booking = workers.Booking.create_booking(
            booker=self.request.user.student, trip=trip, amount=trip.driver.price
        )
        transaction = wallet_workers.Transaction.create_transaction(
            amount=trip.driver.price,
            type=wallet_choices.TransactionType.debit.value,
            owner=self.request.user,
            booking=booking,
        )
        return {
            "amount": transaction.amount,
            "transaction_reference": transaction.transaction_reference,
            "payment_link": transaction.payment_link,
        }
