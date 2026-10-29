from .models import Review
from rest_framework import serializers
from store.models import Product
from orders.models import Order , OrderItem

class ReviewSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(queryset= Product.objects.filter(is_active=True))
    author = serializers.SerializerMethodField()

    class Meta:
        model = Review
        fields = ["id", "product", "author", "rating", "comment", "created_at"]
        read_only_fields  = ["id", "author", "created_at"]

    def get_author(self, obj):
        return obj.user.first_name or "Customer"

    def validate_product(self, product):
            if self.instance and product != self.instance.product:
                raise serializers.ValidationError("you can not change the product")
            return product

    def validate(self, attrs):
            if self.instance is None:
                user = self.context["request"].user
                product = attrs["product"]

                bought = OrderItem.objects.filter(order__user =  user, order__status = Order.Status.DELIVERED, variant__product= product).exists()
                if not bought:
                    raise serializers.ValidationError("you can only review products you have received")

                if Review.objects.filter(user=user, product= product).exists():
                    raise serializers.ValidationError("you have already reviewed this product")

            return attrs

