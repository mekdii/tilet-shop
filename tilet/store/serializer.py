from .models import Category, Ocassion, Color, Product, ProductVariant, ProductImage, Currency
from rest_framework import serializers



class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = ["id", "name"]



class OcasionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ocassion
        fields = [ "id", "name"]

class ColorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Color
        fields = ["id", "name"]



class ProductVariantSerializer(serializers.ModelSerializer):
    color = ColorSerializer(read_only=True)
    class Meta:
        model = ProductVariant
        fields = ["id", "color","size" , "stock"]

class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ["id", "image"]


class CurrencySerializer(serializers.ModelSerializer):
    class Meta:
        model = Currency
        fields= ["code", "name", "symbol", "decimals"]


class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    ocasions = OcasionSerializer(many=True ,read_only=True)
    variants = ProductVariantSerializer(many=True ,read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    avg_rating = serializers.FloatField(read_only=True)
    review_count = serializers.IntegerField(read_only=True)
    display_price = serializers.SerializerMethodField()
    display_currency = serializers.SerializerMethodField()
    class Meta:
        model = Product
        fields = ["id", "name" , "variants", "images", "description", "price" , "is_active", "category", "ocasions", "avg_rating", "review_count", "display_price", "display_currency"]
        ordering_fields = ["price", "name", "id", "avg_rating"]

    def get_display_price(self, obj):
        currency  = self.context.get("currency")
        return str(currency.convert(obj.price)) if currency else None

    def get_display_currency(self, obj):
        currency = self.context.get("currency")
        return currency.code if currency else None



