from rest_framework import serializers

from bui_shuttles.users.models import User
from bui_shuttles.users.choices import AccountType


class UserDetail(serializers.ModelSerializer[User]):
    class Meta:
        model = User
        fields = ["first_name","last_name", "email", "phone_number", "matric_number", "account_type"]
        read_only_fields = ["email", "phone_number", "matric_number", "account_type"]


class GenerateOTP(serializers.Serializer):
    email = serializers.EmailField(required=True)
    matriculation_number = serializers.CharField()
    account_type = serializers.ChoiceField(choices=AccountType.choices, required=True)

    def validate(self, attrs):
        account_type = attrs.get("account_type")
        if account_type == AccountType.student.value:
            if not attrs.get("matriculation_number"):
                raise serializers.ValidationError(
                    "Matriculation number is required for students."
                )
        return super().validate(attrs)


class VerifyOTP(serializers.Serializer):
    email = serializers.EmailField(required=True)
    otp = serializers.CharField(required=True)

    def validate(self, attrs):
        otp = attrs.get("otp")
        if not otp.isdigit() or len(otp) != 6:
            raise serializers.ValidationError("OTP must be a 6-digit number.")
        return super().validate(attrs)


class Register(serializers.ModelSerializer):
    confirm_password = serializers.CharField(write_only=True)
    otp_code = serializers.CharField(required=True)

    class Meta:
        model = User
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
        if password != confirm_password:
            raise serializers.ValidationError("Passwords do not match.")
        return super().validate(attrs)

    def create(self, validated_data):
        validated_data.pop("confirm_password")
        user = User.objects.create_user(
            email=validated_data["email"],
            password=validated_data["password"],
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
            phone_number=validated_data["phone_number"],
            matric_number=validated_data["matric_number"],
            account_type=validated_data["account_type"],
        )
        return user


class Login(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, write_only=True)
