import re

from rest_framework import serializers
from django.core.validators import RegexValidator

from bui_shuttles.users import models, choices
from bui_shuttles.users.choices import AccountType

number_regex = re.compile(r"^[0-9]+$")


class UserDetail(serializers.Serializer):
    first_name = serializers.CharField(max_length=255)
    last_name = serializers.CharField(max_length=255)
    email = serializers.EmailField(max_length=255)
    phone_number = serializers.CharField(read_only=True)
    account_type = serializers.ChoiceField(
        choices=choices.AccountType.choices, read_only=True
    )


class GenerateOTP(serializers.Serializer):
    email = serializers.EmailField(required=True)
    # account_type = serializers.ChoiceField(choices=AccountType.choices, required=True)


class VerifyOTP(serializers.Serializer):
    email = serializers.EmailField(required=True)
    otp = serializers.CharField(required=True)

    def validate(self, attrs):
        otp = attrs.get("otp")
        if not otp.isdigit() or len(otp) != 6:
            raise serializers.ValidationError("OTP must be a 6-digit number.")
        return super().validate(attrs)


class Register(serializers.ModelSerializer):
    matric_number = serializers.CharField(required=False)
    confirm_password = serializers.CharField(write_only=True)
    otp_code = serializers.CharField(required=True)

    class Meta:
        model = models.User
        fields = [
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "password",
            "confirm_password",
            "matric_number",
            "account_type",
            "otp_code",
        ]

    def validate(self, attrs):
        password = attrs.get("password")
        confirm_password = attrs.get("confirm_password")
        account_type = attrs.get("account_type")
        if account_type == AccountType.student.value:
            if not attrs.get("matric_number"):
                raise serializers.ValidationError(
                    "Matriculation number is required for students."
                )
        if password != confirm_password:
            raise serializers.ValidationError("Passwords do not match.")

        return super().validate(attrs)

    def create(self, validated_data):
        validated_data.pop("confirm_password")
        user = models.User.objects.create_user(
            email=validated_data["email"],
            password=validated_data["password"],
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
            phone_number=validated_data["phone_number"],
            account_type=validated_data["account_type"],
        )
        if user.account_type == AccountType.student.value:
            models.Student.objects.create(
                user=user,
                matric_number=validated_data["matric_number"],
            )
        elif user.account_type == AccountType.driver.value:
            models.Driver.objects.create(
                user=user,
            )
        elif user.account_type == AccountType.admin.value:
            user.is_superuser = True
            user.save()
        return user


class Login(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, write_only=True)


class BankDetail(serializers.Serializer):
    bank_code = serializers.CharField(required=True, max_length=10)
    bank_account_number = serializers.CharField(
        required=True,
        max_length=11,
        validators=[
            RegexValidator(regex=number_regex, message="Invalid account number")
        ],
    )
    bank_account_name = serializers.CharField(required=True, max_length=100)


class Vehicle(serializers.ModelSerializer):

    class Meta:
        model = models.Vehicle
        fields = [
            "name",
            "capacity",
            "reg_number",
            "vehicle_type",
        ]

    def create(self, validated_data):
        context = self.context
        driver = context.get("request").user.driver
        if not driver:
            raise serializers.ValidationError("Only drivers can create vehicles.")
        vehicle = models.Vehicle.objects.filter(driver=driver).first()
        if vehicle:
            return super().update(vehicle, validated_data)
        new_vehicle = super().create(validated_data)
        driver.vehicle = new_vehicle
        driver.save()
        return new_vehicle


class DriverProfile(serializers.Serializer):
    first_name = serializers.SerializerMethodField()
    last_name = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()
    phone_number = serializers.SerializerMethodField()
    account_type = serializers.SerializerMethodField()
    is_available = serializers.BooleanField()
    vehicle = Vehicle()
    to_route = serializers.SerializerMethodField()
    from_route = serializers.SerializerMethodField()
    price = serializers.IntegerField(default=0)  # price in kobo per seat
    bank_account_number = serializers.CharField(read_only=True)
    bank_account_name = serializers.CharField(read_only=True)

    def get_to_route(self, obj):
        if not obj.to_route:
            return None
        return obj.to_route.name

    def get_from_route(self, obj):
        if not obj.from_route:
            return None
        return obj.from_route.name

    def get_first_name(self, obj):
        return obj.user.first_name

    def get_last_name(self, obj):
        return obj.user.last_name

    def get_email(self, obj):
        return obj.user.email

    def get_phone_number(self, obj):
        return obj.user.phone_number

    def get_account_type(self, obj):
        return obj.user.account_type


class VehicleDetail(Vehicle):
    driver = DriverProfile(read_only=True)

    class Meta:
        model = models.Vehicle
        fields = [
            "id",
            "name",
            "capacity",
            "reg_number",
            "vehicle_type",
            "driver",
        ]


class DriverProfileUpdate(serializers.ModelSerializer):
    first_name = serializers.CharField(max_length=255, required=False)
    last_name = serializers.CharField(max_length=255, required=False)
    is_available = serializers.BooleanField(required=False)

    class Meta:
        model = models.Driver
        fields = [
            "first_name",
            "last_name",
            "is_available",
            "to_route",
            "from_route",
            "price",
        ]

    def validate(self, attrs):
        to_route = attrs.get("to_route")
        from_route = attrs.get("from_route")
        if to_route == from_route:
            raise serializers.ValidationError("To and from routes cannot be the same.")
        return super().validate(attrs)


class StudentProfile(UserDetail):
    matric_number = serializers.CharField(read_only=True)
