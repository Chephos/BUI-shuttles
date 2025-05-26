from rest_framework import permissions

class IsBooker(permissions.IsAuthenticated):
    """
    Custom permission to only allow the booker of a booking to access it.
    """

    def has_object_permission(self, request, view, obj):
        return obj.booker == request.user.student
    
class IsBookee(permissions.IsAuthenticated):
    """
    Custom permission to only allow the bookee of a booking to access it.
    """

    def has_object_permission(self, request, view, obj):
        return obj.trip.driver == request.user.driver