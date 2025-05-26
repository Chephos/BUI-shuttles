from rest_framework import serializers

class Paystack(serializers.Serializer):
    event = serializers.CharField(max_length=100, required=True)
    data = serializers.DictField(required=True)
