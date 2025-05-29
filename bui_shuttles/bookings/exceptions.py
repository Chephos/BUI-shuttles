from rest_framework.exceptions import APIException


class AlreadyBooked(APIException):
    status_code = 400
    default_detail = "You have already booked this trip"
    default_code = "already_booked"
