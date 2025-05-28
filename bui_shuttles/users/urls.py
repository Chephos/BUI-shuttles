from django.urls import path

from rest_framework import routers
from . import views

router = routers.DefaultRouter()
router.register(
    r"vehicles",
    views.Vehicle,
)
router.register(r"user_profile", views.UserProfile, "user_profile")

app_name = "users"
urlpatterns = [
    path("~redirect/", view=views.user_redirect_view, name="redirect"),
    path("~update/", view=views.user_update_view, name="update"),
    # path("", view=views.user_detail_view, name="detail"),
    path("add-bank/", views.AddBank.as_view(), name="add_bank"),
    path("generate-otp/", view=views.GenerateOTP.as_view(), name="generate_otp"),
    path("verify-otp/", view=views.VerifyOTP.as_view(), name="verify_otp"),
    path("register/", view=views.Register.as_view(), name="register"),
    path("login/", view=views.Login.as_view(), name="login"),
    path("logout/", view=views.Logout.as_view(), name="logout"),
]

urlpatterns += router.urls
