from .models import Cart, CartItem
from rest_framework import serializers
from store.models import ProductVariant
from accounts.models import Address

class CartItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="variant.product.name", read_only=True)
    color = serializers.CharField(source = "variant.color.name", read_only=True)
    size = serializers.CharField(source="variant.size", read_only= True)
    unit_price = serializers.DecimalField(source="variant.product.price", max_digits=10, decimal_places=2, read_only=True)
    in_stock = serializers.IntegerField(source="variant.stock", read_only=True)
    subtotal= serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = CartItem
        fields = ["id", "variant", "product_name", "color", "size", "unit_price", "quantity", "in_stock", "subtotal"]


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = Cart
        fields = ["items", "total"]

class AddToCartSerializer(serializers.Serializer):
    variant = serializers.PrimaryKeyRelatedField(queryset=ProductVariant.objects.filter(product__is_active=True))
    quantity = serializers.IntegerField(min_value=1, default= 1)


class UpdateCartItemSerializer(serializers.Serializer):
    quantity = serializers.IntegerField(min_value= 1)

class CartCheckoutSerializer(serializers.Serializer):
    address = serializers.PrimaryKeyRelatedField(queryset= Address.objects.all())

    def validate_address(self, address):
        if address.user != self.context["request"].user:
            raise serializers.ValidationError("Invalid address.")
        return address