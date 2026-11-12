from django.db import models
import math
from decimal import Decimal
from django.core.exceptions import ValidationError
from django_countries.fields import CountryField

# Create your models here.
class Shipment(models.Model):
    class Status(models.TextChoices):
        IN_TRANSIT = "in_transit", "In transit"
        DELIVERED = "delivered", "Delivered"
        RETURNED = "returned", "Returned"

    order = models.ForeignKey("orders.Order", on_delete=models.PROTECT, related_name="shipments")
    carrier = models.CharField(max_length=50)
    tracking_number = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default= Status.IN_TRANSIT)
    return_reason = models.CharField(max_length=255, blank=True)
    shipped_at = models.DateTimeField(auto_now_add=True)
    delivered_at = models.DateTimeField(null=True, blank=True)


    class Meta:
        ordering = ["-shipped_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["order"],
                condition= ~models.Q(status="returned"),
                name="one_active_shipment_per_order",
            )
        ]

    def __str__(self):
        return f"{self.carrier} {self.tracking_number} (order {self.order_id})"



class ShippingZone(models.Model):
    name = models.CharField(max_length=100, unique=True)
    countries = CountryField(multiple=True, blank=True)
    city = models.CharField(max_length=100, blank=True)
    is_fallback = models.BooleanField(default=False)
    base_fee = models.DecimalField(max_digits=10, decimal_places=2)
    extra_per_kg =  models.DecimalField(max_digits=10, decimal_places=2, default=0)
    free_over = models.DecimalField(max_digits=10, decimal_places=2, null = True, blank = True)
    delivery_estimate = models.CharField(max_length=50, blank=True)
    is_active = models.BooleanField(default=True)
    currency = models.ForeignKey("store.Currency", on_delete=models.PROTECT, related_name="zones")


    class Meta:
        constraints= [
            models.UniqueConstraint(
                fields=["is_fallback"],
                condition=models.Q(is_fallback=True),
                name = "only_one_fallback_zone"
            )
        ]
    def clean(self):
        """A country may appear is one zone (per city)"""
        if self.is_fallback:
            return 
        mine = {c.code for c in self.countries}
        others = ShippingZone.objects.exclude(pk=self.pk).filter(
            is_fallback= False , city__iexact=self.city
        )
        for other in others:
            overlap = mine & {c.code for c in other.countries}
            if overlap:
                raise ValidationError(
                    f"{sorted(overlap)} already belong to the zone '{other.name}'"
                )

    def fee_for(self, subtotal , weight_grams):
        if self.free_over is not None and subtotal >= self.free_over:
            return Decimal("0.00")
        extra_kg = max(0, math.ceil((weight_grams - 1000)/ 1000))
        return self.base_fee + self.extra_per_kg * extra_kg

    def __str__(self):
        return self.name
