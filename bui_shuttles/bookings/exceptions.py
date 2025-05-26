from rest_framework.exceptions import APIException

class InvalidTrip(APIException):
    status_code = 400
    default_detail = "Invalid trip"
    default_code = "invalid_trip"
