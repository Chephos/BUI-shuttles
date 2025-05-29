from django.db import transaction

from . import models
from bui_shuttles.users import models as user_models
from bui_shuttles.trips import models as trip_models, workers as trip_workers


class Booking:
    model = models.Booking
    @classmethod
    def create_booking(cls, booker: user_models.Student,  trip: trip_models.Trip, amount: int):
        booking = cls.model.objects.create(booker=booker,  trip=trip, amount=amount)
        trip_workers.Trip.occupy_or_free_seat(trip.id, "occupy")
        return booking
    
    @classmethod
    def get_booking_by_id(cls, booking_id):
        booking = cls.model.objects.filter(id=booking_id).first()
        if booking:
            return booking
        return None
    
    @classmethod
    def complete_booking(cls, booking_id, new_status):
        with transaction.atomic():
            booking = cls.get_booking_by_id(booking_id)
            if not booking:
                return None
            booking.status = new_status
            booking.save()
            return booking
        
    @classmethod
    def get_bookings_by_student(cls, student: user_models.Student):
        return cls.model.objects.filter(booker=student)
    
    @classmethod
    def get_bookings_for_driver(cls, driver: user_models.Driver):
        return cls.model.objects.filter(trip__driver=driver)
    
    @classmethod
    def get_booking_for_student_by_trip(cls, student: user_models.Student, trip: trip_models.Trip):
        return cls.model.objects.filter(booker=student, trip=trip).first()