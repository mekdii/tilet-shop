from django.shortcuts import render
from rest_framework import viewsets
from .serializer import ProductSerializer, CategorySerializer, OcasionSerializer
from .models import Product , Category, Ocassion
from rest_framework.permissions import AllowAny
from .pagination import ProductPagination
from .filters import ProductFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
from django.db.models import Avg, Count

# Create your views here.
class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [AllowAny]
    serializer_class = ProductSerializer
    pagination_class = ProductPagination

    filter_backends = [DjangoFilterBackend, SearchFilter , OrderingFilter ]
    filterset_class = ProductFilter
    search_fields = ["name", "description"]
    ordering_fields = ["price", "name", "id"]
    ordering = ["-id"]

    def get_queryset(self):
        return (
            Product.objects.filter(is_active = True).select_related("category").prefetch_related("variants__color", "images", "ocasions").annotate(
                avg_rating=Avg("reviews__rating"),
                review_count=Count("reviews", distinct=True),
            ).distinct()
        )

class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [AllowAny]
    serializer_class = CategorySerializer
    queryset =  Category.objects.order_by("name")


class OcasionViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [AllowAny]
    serializer_class = OcasionSerializer
    queryset = Ocassion.objects.order_by("name")

