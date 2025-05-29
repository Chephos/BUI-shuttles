from rest_framework.exceptions import APIException
class VehicleRequired(APIException):
    status_code = 400
    default_detail = "Vehicle is required for this operation"
    default_code = "vehicle_required"

class TimeBookedForATrip(APIException):
    status_code = 400
    default_detail = "Time has already been booked for a trip"
    default_code = "time_booked_for_a_trip"

class InvalidTrip(APIException):
    status_code = 400
    default_detail = "Invalid trip"
    default_code = "invalid_trip"