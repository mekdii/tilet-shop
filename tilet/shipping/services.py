

from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone
from orders.models import Order
from orders.services import restore_stock
from payments.models import Payment
from .models import Shipment
from rest_framework.exceptions import ValidationError


def ship_order(* , order_id, carrier, tracking_number=""):
    """Staff handed a paid order to a courier or our own rider"""
    with transaction.atomic():
        order = get_object_or_404(Order.objects.select_for_update(), pk=order_id)

        if order.status  != Order.Status.PAID:
            raise ValidationError(
                f'Only paid orders can be shipped (this order is {order.status})'

            )
        Shipment.objects.create(
            order = order , carrier= carrier, tracking_number=tracking_number
        )
        order.status = Order.Status.SHIPPED
        order.save(update_fields=["status"])

    return order


def mark_delivered(*, order_id):
    """The customer has the dress"""

    with transaction.atomic():
        order =  get_object_or_404(Order.objects.select_for_update(), pk=order_id)
        if order.status != Order.Status.SHIPPED:
            raise ValidationError(
                f"Only shipped orders can be delivered (this order is {order.status})"
            )

        shipment = order.shipments.get(status=Shipment.Status.IN_TRANSIT)
        shipment.status = Shipment.Status.DELIVERED
        shipment.delivered_at = timezone.now()
        shipment.save(update_fields=["status", "delivered_at"])

        order.status = Order.Status.DELIVERED
        order.save(update_fields=["status"])
    return order



# def mark_delivered(*, order_id):
#     """the custemer has the dress"""
#     with transaction.atomic():
#         order = get_object_or_404(Order.objects.select_for_update(), pk=order_id)

#         if order.status != Order.Status.SHIPPED:
#             raise ValidationError(
#                 f"Only shipped orders can be delivered (this order is {order.status})"
#             )
#         shipment  = order.shipment.get(status= Shipment.Status.IN_TRANSIT)
#         shipment.status = Shipment.Status.DELIVERED
#         shipment.delivered_at = timezone.now()
#         shipment.save(update_fields= ["status", "delivered_at"])
#         order.status = Order.Status.DELIVERED
#         order.save(update_fields=["status"])

#     return order


def mark_returned(*, order_id, outcome, reason=""):
    """The package physically came back to us.
    outcome "reship": the order goes back to paid so it can be sent again.
    outcome "refund": the order is cancelled, stock restored, payment flagged for refund."""

    with transaction.atomic():
        order = get_object_or_404(Order.objects.select_for_update(), pk=order_id)
        if order.status != Order.Status.SHIPPED:
            raise ValidationError(
                f"Only shipped orders can be returned (this order is {order.status})"
            )

        shipment = order.shipments.get(status=Shipment.Status.IN_TRANSIT)
        shipment.status = Shipment.Status.RETURNED
        shipment.return_reason = reason 
        shipment.save(update_fields=["status", "return_reason"])

        if outcome== "refund":
            restore_stock(order)
            order.status = Order.Status.CANCELLED
            Payment.objects.filter(
                order = order , status= Payment.Status.SUCCEEDED
            ).update(status=Payment.Status.REFUND_PENDING)

        else:
            order.status = Order.Status.PAID

        order.save(update_fields=["status"])

    return order

        
        
