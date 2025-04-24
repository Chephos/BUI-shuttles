from django.urls import path

from . import views


app_name = "users"
urlpatterns = [
    path("~redirect/", view=views.user_redirect_view, name="redirect"),
    path("~update/", view=views.user_update_view, name="update"),
    path("", view=views.user_detail_view, name="detail"),
    path("generate-otp/", view=views.GenerateOTP.as_view(), name="generate_otp"),
    path("verify-otp/", view=views.VerifyOTP.as_view(), name="verify_otp"),
    path("register/", view=views.Register.as_view(), name="register"),
    path("login/", view=views.Login.as_view(), name="login"),
    path("logout/", view=views.Logout.as_view(), name="logout"),
]
