from django.db import models

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