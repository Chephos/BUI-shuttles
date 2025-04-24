from rest_framework import serializers

from bui_shuttles.users.models import User
from bui_shuttles.users.choices import AccountType


class UserSerializer(serializers.ModelSerializer[User]):
    class Meta:
        model = User
        fields = ["name", "url"]

        extra_kwargs = {
            "url": {"view_name": "api:user-detail", "lookup_field": "pk"},
        }

class GenerateOTP(serializers.Serializer):
    email = serializers.EmailField(required=True)
    matriculation_number = serializers.CharField()
    account_type = serializers.ChoiceField(choices=AccountType.choices, required=True)

    def validate(self, attrs):
        account_type = attrs.get("account_type")
        if account_type == AccountType.student.value:
            if not attrs.get("matriculation_number"):
                raise serializers.ValidationError("Matriculation number is required for students.")
        return super().validate(attrs)