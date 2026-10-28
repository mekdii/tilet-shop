from django.shortcuts import render
from rest_framework import viewsets
from .serializer import ProductSerializer
from .models import Product

# Create your views here.
class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ProductSerializer

    def get_queryset(self):
        return (
            Product.objects.filter(is_active = True).select_related("category").prefetch_related("variants__color", "images", "ocasions")
        )