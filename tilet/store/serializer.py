from .models import Category, Ocassion, Color, Product, ProductVariant, ProductImage
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


class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    ocasions = OcasionSerializer(many=True ,read_only=True)
    variants = ProductVariantSerializer(many=True ,read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    class Meta:
        model = Product
        fields = ["id", "name" , "variants", "images", "description", "price" , "is_active", "category", "ocasions"]



