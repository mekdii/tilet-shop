from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from .models import User , Address


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
        fields = ['id', 'street', 'apartment', 'city', 'country']
        read_only_fields = ['id']