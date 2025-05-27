from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import QuerySet
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import RedirectView
from django.views.generic import UpdateView
from rest_framework import (
    views,
    permissions,
    status,
    response,
    mixins,
    viewsets,
)

from bui_shuttles.users.models import User
from bui_shuttles.users import (
    serializers,
    workers,
    exceptions,
    permissions as user_permissions,
    models,
    choices,
)


# class UserDetailView(views.APIView):
#     serializer_class = serializers.User
#     permission_classes = [permissions.IsAuthenticated]

#     def get(self, request):
#         user = request.user
#         serializer = self.serializer_class(user)
#         return Response(serializ er.data, status=200)


# user_detail_view = UserDetailView.as_view()


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
        return response.Response({"message": "OTP sent successfully"}, status=200)


class VerifyOTP(views.APIView):
    serializer_class = serializers.VerifyOTP
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        otp_verified = workers.OTP.verify_otp(**serializer.validated_data)
        if not otp_verified:
            return response.Response({"message": "Invalid OTP"}, status=400)
        return response.Response({"message": "OTP verified successfully"}, status=200)


class Register(views.APIView):
    serializer_class = serializers.Register
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        if workers.OTP.validate_otp_action(request.data["email"]):

            user = serializer.save()
            token = workers.Token.create_token(user)
            return response.Response({"token": token}, status=201)
        else:
            raise exceptions.OTPVerificationFailed


class Login(views.APIView):
    serializer_class = serializers.Login
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = workers.User.get_user_by_email(email=serializer.validated_data["email"])
        if user:
            if user.check_password(serializer.validated_data["password"]):
                token = workers.Token.create_token(user)
                return response.Response({"token": token}, status=200)
            else:
                return response.Response({"message": "Invalid password"}, status=400)


class Logout(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        workers.Token.delete_token(request.user)
        return response.Response({"message": "Logout successful"}, status=200)


class AddBank(views.APIView):
    serializer_class = serializers.BankDetail
    permission_classes = [user_permissions.IsDriver]

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        workers.Driver.add_bank(request.user, serializer.validated_data)
        return response.Response(
            status=status.HTTP_200_OK,
            data={"detail": "Bank details added successfully"},
        )


class Vehicle(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    permission_classes = [user_permissions.IsDriver]
    queryset = models.Vehicle.objects.all()

    def get_serializer_class(self):
        if self.action == "retrieve":
            return serializers.VehicleDetail
        return serializers.Vehicle

    def get_permissions(self):
        if self.request.method == "GET":
            self.permission_classes = [permissions.IsAuthenticated]
        elif self.request.method in ["PUT", "PATCH"]:
            self.permission_classes = [user_permissions.IsDriver]
        return super().get_permissions()






class UserProfile(mixins.RetrieveModelMixin, mixins.UpdateModelMixin, viewsets.GenericViewSet):
    queryset = models.User.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.request.user.account_type == choices.AccountType.student.value:
            return serializers.StudentProfile
        elif self.request.user.account_type == choices.AccountType.driver.value:
            if self.request.method == "GET":
                return serializers.DriverProfile
            return serializers.DriverProfileUpdate
        return serializers.UserDetail
