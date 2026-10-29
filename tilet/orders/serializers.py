from .models import Order, OrderItem
from rest_framework import serializers
from store.models import ProductVariant
from accounts.models import Address



class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="variant.product.name", read_only=True)
    color = serializers.CharField(source = "variant.color.name", read_only=True)
    size = serializers.CharField(source="variant.size", read_only=True)

    class Meta:
        model = OrderItem
        fields = ["id", "variant", "product_name", "color", "size",    "quantity", "unit_price"]
        read_only_fields = ["id", "unit_price"]
      




class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    total = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = Order
        fields = ["id", "address", "status", "created_at", "items", "total"]
        read_only_fields = ["id", "status", "created_at"]


class CheckoutItemSerializer(serializers.Serializer):
    variant = serializers.PrimaryKeyRelatedField(queryset  = ProductVariant.objects.filter(product__is_active=True))
    quantity = serializers.IntegerField(min_value=1)


class CheckoutSerializer(serializers.Serializer):
    address = serializers.PrimaryKeyRelatedField(queryset=Address.objects.all())
    items = CheckoutItemSerializer(many=True, allow_empty=False)

    def validate_address(self, address):
        if address.user != self.context["request"].user:
            raise serializers.ValidationError("Invalid address")
        return address

    def validate_items(self, items):
        ids = [item['variant'].id for item in items]
        if len(ids) != len(set(ids)):
            raise serializers.ValidationError("Each variant may apear only once")
        return items
    



