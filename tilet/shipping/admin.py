from django.contrib import admin

from .models import Shipment
from .models import ShippingZone


@admin.register(Shipment)
class ShipmentAdmin(admin.ModelAdmin):
    list_display = ("id", "order", "carrier", "tracking_number", "status", "shipped_at")
    list_filter = ("status", "carrier")

@admin.register(ShippingZone)
class ShippingZoneAdmin(admin.ModelAdmin):
    list_display = ("name", "city", "is_fallback", "base_fee", "extra_per_kg",
                    "free_over", "delivery_estimate", "is_active")