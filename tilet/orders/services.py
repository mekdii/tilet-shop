from django.db import transaction
from .models import Order, OrderItem
from store.models import ProductVariant
from rest_framework.exceptions import ValidationError
from store.models import ProductVariant
from django.db.models import F
from decimal import Decimal
from django.conf import settings
from shipping.rates import get_zone


def place_order(*, user, address, items):
    """items a list of {variant : <productVariant>, "quantity": int}"""
    zone = get_zone(address)
    if zone is None:
        raise ValidationError("we do not deliver to this address yet.")
    
    currency = zone.currency
    ids = sorted({item["variant"].id for item in items})


    with transaction.atomic():
        order = Order.objects.create(user=user , address=address, currency=currency.code)

        variants = (ProductVariant.objects.select_for_update(of=("self",)).select_related("product", "color")).in_bulk(ids)
        subtotal = Decimal("0")
        weight = settings.PACKAGING_GRAMS
        for item in items:
            variant = variants[item["variant"].id]
            qty = item["quantity"]

            if not variant.product.is_active:
                raise ValidationError(f"{variant.product.name} is no longer available")

            if variant.stock < qty:
                raise ValidationError(f"Not enough stock for {variant}. Only {variant.stock} left")

            variant.stock -= qty
            variant.save(update_fields=["stock"])

            unit_price = currency.convert(variant.product.price)

            OrderItem.objects.create(order=order,
                                     variant=variant,
                                     quantity = qty,
                                     unit_price=unit_price)


            subtotal +=unit_price * qty
            weight += variant.product.weight_grams * qty

        order.shipping_fee = zone.free_for(subtotal, weight)
        order.save(update_fields=["shipping_fee"])
   
    return order


def restore_stock(order):
    for item in order.items.order_by("variant_id"):
        ProductVariant.objects.filter(pk=item.variant_id).update(
            stock= F("stock") + item.quantity
        )