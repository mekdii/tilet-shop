from rest_framework import serializers
from .models import Shipment

class ShipmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shipment
        fields = ["carrier", "tracking_number", "status", "return_reason", "shipped_at", "delivered_at"]



class ShipOrderSerializer(serializers.Serializer):
    carrier = serializers.CharField(max_length=50)
    tracking_number = serializers.CharField(max_length=100, required=False, allow_blank=True)


class ReturnShipmentSerializer(serializers.Serializer):
    outcome = serializers.ChoiceField(
        choices=[("reship", "Ship again"), ("refund", "Cancel and refund")]

    )
    reason = serializers.CharField(max_length=255 , required= False, allow_blank=True)
    