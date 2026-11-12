from django.shortcuts import render
from rest_framework import viewsets
from .serializer import ProductSerializer, CategorySerializer, OcasionSerializer, CurrencySerializer
from .models import Product , Category, Ocassion, Currency
from rest_framework.permissions import AllowAny
from .pagination import ProductPagination
from .filters import ProductFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
from django.db.models import Avg, Count
from django.conf import settings
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

    def get_serializer_context(self):
        context = super().get_serializer_context()
        code = self.request.query_params.get("currency", settings.BASE_CURRENCY).upper()
        context["currency"] = (
            Currency.objects.filter(code=code).first()
            or Currency.objects.filter(code=settings.BASE_CURRENCY).first()
        )
        return context

class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [AllowAny]
    serializer_class = CategorySerializer
    queryset =  Category.objects.order_by("name")


class OcasionViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [AllowAny]
    serializer_class = OcasionSerializer
    queryset = Ocassion.objects.order_by("name")



class CurrencyViewSet(viewsets.ReadOnlyModelViewSet):
    authentication_classes = []
    permission_classes = [AllowAny]
    serializer_class = CurrencySerializer
    queryset = Currency.objects.order_by("code")
