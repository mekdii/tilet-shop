from rest_framework import serializers
from orders.models import Order



class IntiatePaymentSerializer(serializers.Serializer):
    order   = serializers.PrimaryKeyRelatedField(queryset=Order.objects.all())

    def validate_order(self, order):
        if order.user != self.context["request"].user:
            raise serializers.ValidationError("invalid Order.")
        if order.status != Order.Status.PENDING:
            raise serializers.ValidationError("this order can not be paid")

        return order