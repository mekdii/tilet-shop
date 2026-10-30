from django.db import models
from django.conf import settings



class Cart(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE , related_name="cart")
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def total(self):
        return sum(item.subtotal for item in self.items.all())

    def __str__(self):
        return f"Cart of {self.user}"


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name= "items")
    variant = models.ForeignKey("store.ProductVariant", on_delete=models.CASCADE, related_name="cart_items")
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['cart', 'variant'], name="one_row_per_variant_in_cart")

        ]

    @property
    def subtotal(self):
        return self.quantity * self.variant.product.price

    def __str__(self):
        return f"{self.quantity} x {self.variant}"

