import django_filters
from .models import Product

class ProductFilter(django_filters.FilterSet):
    min_price = django_filters.NumberFilter(field_name="price", lookup_expr="gte")
    max_price = django_filters.NumberFilter(field_name="price", lookup_expr= "lte")
    category = django_filters.NumberFilter(field_name="category_id")
    ocasion = django_filters.NumberFilter(field_name="ocasions__id")
    color = django_filters.NumberFilter(field_name="variants__color_id")
    size = django_filters.CharFilter(field_name="variants__size", lookup_expr="iexact")
    in_stock = django_filters.BooleanFilter(method="filter_in_stock")


    class Meta:
        model = Product
        fields= []

    def filter_in_stock(self, queryset, name, value):
        if value:
            return queryset.filter(variants__stock__gt=0)
        return queryset.exclude(variants__stock__gt=0)