from django.contrib import admin
from .models import Currency


@admin.register(Currency)
class CurrencyAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "decimals", "etb_per_unit", "markup_percent")


from django.contrib import admin

from .models import Category, Color, Ocassion, Product, ProductImage, ProductVariant


class VariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1


class ImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "price", "is_active")
    list_filter = ("category", "ocasions", "is_active")
    search_fields = ("name",)
    inlines = [VariantInline, ImageInline]


admin.site.register(Category)
admin.site.register(Ocassion)
admin.site.register(Color)