from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import QuerySet
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import RedirectView
from django.views.generic import UpdateView
from rest_framework import views, permissions
from rest_framework.response import Response

from bui_shuttles.users.models import User
from bui_shuttles.users import serializers, workers, exceptions


class UserDetailView(views.APIView):
    serializer_class = serializers.User
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        serializer = self.serializer_class(user)
        return Response(serializer.data, status=200)


user_detail_view = UserDetailView.as_view()


class UserUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = User
    fields = ["name"]
    success_message = _("Information successfully updated")

    def get_success_url(self) -> str:
        assert self.request.user.is_authenticated  # type guard
        return self.request.user.get_absolute_url()

    def get_object(self, queryset: QuerySet | None = None) -> User:
        assert self.request.user.is_authenticated  # type guard
        return self.request.user


user_update_view = UserUpdateView.as_view()


class UserRedirectView(LoginRequiredMixin, RedirectView):
    permanent = False

    def get_redirect_url(self) -> str:
        return reverse("users:detail", kwargs={"pk": self.request.user.pk})


user_redirect_view = UserRedirectView.as_view()


class GenerateOTP(views.APIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = serializers.GenerateOTP

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_exists = workers.User.user_exists(
            email=serializer.validated_data["email"],
        )
        if user_exists:
            raise exceptions.UserAlreadyExists
        otp_sent = workers.OTP.send_otp(serializer.validated_data["email"])
        if not otp_sent:
            raise exceptions.InvalidOTP
        return Response({"message": "OTP sent successfully"}, status=200)


class VerifyOTP(views.APIView):
    serializer_class = serializers.VerifyOTP
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        otp_verified = workers.OTP.verify_otp(**serializer.validated_data)
        if not otp_verified:
            return Response({"message": "Invalid OTP"}, status=400)
        return Response({"message": "OTP verified successfully"}, status=200)


class Register(views.APIView):
    serializer_class = serializers.Register
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        if workers.OTP.validate_otp_action(request.data["email"]):

            user = serializer.save()
            token = workers.Token.create_token(user)
            return Response({"token": token}, status=201)
        else:
            raise exceptions.OTPVerificationFailed


class Login(views.APIView):
    serializer_class = serializers.Login
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = workers.User.get_user_from_email(
            email=serializer.validated_data["email"]
        )
        if user:
            if user.check_password(serializer.validated_data["password"]):
                token = workers.Token.create_token(user)
                return Response({"token": token}, status=200)
            else:
                return Response({"message": "Invalid password"}, status=400)


class Logout(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        workers.Token.delete_token(request.user)
        return Response({"message": "Logout successful"}, status=200)
