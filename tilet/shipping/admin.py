from django.contrib import admin

from .models import Shipment


@admin.register(Shipment)
class ShipmentAdmin(admin.ModelAdmin):
    list_display = ("id", "order", "carrier", "tracking_number", "status", "shipped_at")
    list_filter = ("status", "carrier")