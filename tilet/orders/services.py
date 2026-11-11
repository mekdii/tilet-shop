from django.db import transaction
from .models import Order, OrderItem
from store.models import ProductVariant
from rest_framework.exceptions import ValidationError
from store.models import ProductVariant
from django.db.models import F

def place_order(*, user, address, items):
    """items a list of {variant : <productVariant>, "quantity": int}"""
    ids = sorted({item["variant"].id for item in items})

    with transaction.atomic():
        order = Order.objects.create(user=user , address=address)

        variants = (ProductVariant.objects.select_for_update(of=("self",)).select_related("product", "color")).in_bulk(ids)
        for item in items:
            variant = variants[item["variant"].id]
            qty = item["quantity"]

            if not variant.product.is_active:
                raise ValidationError(f"{variant.product.name} is no longer available")

            if variant.stock < qty:
                raise ValidationError(f"Not enough stock for {variant}. Only {variant.stock} left")

            variant.stock -= qty
            variant.save(update_fields=["stock"])

            OrderItem.objects.create(order=order,
                                     variant=variant,
                                     quantity = qty,
                                     unit_price=variant.product.price)


    return order


def restore_stock(order):
    for item in order.items.order_by("variant_id"):
        ProductVariant.objects.filter(pk=item.variant_id).update(
            stock= F("stock") + item.quantity
        )