from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from .models import User , Address
import re


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])

    class Meta:
        model = User
        fields = ["phone", "password", "first_name", "last_name", "email"]

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)
        


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ['id', 'street', 'apartment', 'city', 'country', 'postal_code']
        read_only_fields = ['id']
        extra_kwargs = {"phone": {"required": True, "allow_blank": False}}

    def validate_phone(self, value):
        value = value.replace(" ", "")
        if not re.fullmatch(r"\+\d{8,15}", value):
            raise serializers.ValidationError("Use international format, e.g. +251911223344.")
        return value

    def validate(self, attrs):
        country = attrs.get("country", getattr(self.instance, "country", None))
        postal = attrs.get("postal_code", getattr(self.instance, "postal_code", ""))
        if country and str(country) != "ET" and not postal:
            raise serializers.ValidationError(
                {"postal_code": "A postal code is required for this country."}
            )
        return attrs