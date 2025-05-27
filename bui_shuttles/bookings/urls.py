from rest_framework import routers

from . import views

router = routers.DefaultRouter()
router.register("", views.Bookings, basename="bookings")

app_name = "bookings"
urlpatterns = router.urls