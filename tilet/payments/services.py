import logging
from django.db import transaction
from .models import Payment
from django.utils import timezone
from orders.models import Order
from decimal import Decimal , InvalidOperation
from . import chapa
logger = logging.getLogger(__name__)

def mark_payment_succeeded(payment_id):
    with transaction.atomic():
        payment = Payment.objects.select_for_update().get(pk=payment_id)

        if payment.status == Payment.Status.SUCCEEDED:
            return payment
        payment.status = Payment.Status.SUCCEEDED
        payment.paid_at = timezone.now()
        payment.save(update_fields=["status", "paid_at"])
        order = Order.objects.select_for_update().get(pk=payment.order_id)
        if order.status == Order.Status.PENDING:
            order.status = Order.Status.PAID
            order.save(update_fields=["status"])

        else:
            logger.warning("Payment %s succeeded but order %s is %s: refund needed ", payment.pk, order.pk, order.status )

    return payment


def confirm_chapa_payment(payment):
    """ ask directly wheather this payment really succeded."""

    result = chapa.verify(payment.reference)
    data = result.get("data") or {}

    try:
        paid_amount = Decimal(str(data.get("amount")))
    except InvalidOperation:
        paid_amount = None

    if(
        result.get("status") == "success"
        and data.get("status") == "success"
        and paid_amount == payment.amount
        and str(data.get("currency", "")).upper() == payment.currency

    ):
        mark_payment_succeeded(payment.pk)
    return Payment.objects.get(pk=payment.pk)

