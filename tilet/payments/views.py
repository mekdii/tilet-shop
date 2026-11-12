import hashlib
import hmac
import json
import uuid
import stripe

from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from .serializers import IntiatePaymentSerializer
import uuid
from decimal import Decimal
from .models import Payment
from . import chapa
from django.conf import settings
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from rest_framework.exceptions import ValidationError
from store.models import Currency
from .services import confirm_chapa_payment, mark_payment_succeeded

stripe.api_key = settings.STRIPE_SECRET_KEY


#--------------------- Chapa -------------------

class ChapaIntiateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = IntiatePaymentSerializer(data=request.data , context={"request": request})
        serializer.is_valid(raise_exception=True)
        order = serializer.validated_data["order"]

        tx_reference = f"tilet-{order.id}-{uuid.uuid4().hex[:12]}"
        if order.currency != settings.BASE_CURRENCY:
            raise ValidationError("Orders in this currency are paid by card.")

        amount = Decimal(order.total).quantize(Decimal("0.01")) # the server decides

        payment = Payment.objects.create(order=order,  provider= Payment.Provider.CHAPA, 
                                         
                            reference= tx_reference, amount=amount, currency=order.currency,)

        try:
            checkout_url = chapa.initialize(
                tx_ref=tx_reference, amount=amount, user=request.user,
                return_url=f"{settings.FRONTEND_URL}/payment/return?reference={tx_reference}"
            )
        except Exception:
            payment.status = Payment.Status.FAILED
            payment.save(update_fields=["status"])
            raise
        return Response({"checkout_url": checkout_url, "reference": tx_reference}, status=201)




class ChapaVerifyView(APIView):
    """the front end calls this after the customer returns from chapa"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        payment = Payment.objects.select_related("order").filter(
            provider=Payment.Provider.CHAPA,
            reference = request.data.get("reference"),
            order__user=request.user
        ).first()

        if payment is None:
            raise NotFound("Payment not found")

        payment = confirm_chapa_payment(payment)
        payment.order.refresh_from_db()
        return Response({"payment_status": payment.status, "order_status": payment.order.status})


    
        



class ChapaWebhookView(APIView):
    authentication_classes = [] # public : security is the signature
    permission_classes = [AllowAny]

    def post(self, request):
        signature = request.headers.get("x-chapa-signature", "")
        expected = hmac.new(settings.CHAPA_SECRET_KEY.encode(), request.body, hashlib.sha256).hexdigest()

        if not signature or not hmac.compare_digest(signature, expected):
            return Response(status=400)

        try:
            reference = json.loads(request.body).get("tx_ref")
        except ValueError:
            return Response(status=400)

        paymnet= Payment.objects.filter(provider=Payment.Provider.CHAPA, reference= reference).first()

        if paymnet:
            confirm_chapa_payment(paymnet)
        return Response(status=200) 


# ----------------- Stripe------------------


class StripeIntiateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = IntiatePaymentSerializer(data=self.request.data , context={"request":self.request})
        serializer.is_valid(raise_exception=True)
        order = serializer.validated_data["order"]

        # usd = (Decimal(order.total)/ settings.ETB_PER_USD).quantize(Decimal("0.01"))
        # cents = int(usd * 100)
        if order.currency == settings.BASE_CURRENCY:
            raise ValidationError("Orders in ETB are paid with Chapa.")

        currency = Currency.objects.get(code=order.currency)
        amount = Decimal(order.total)


        session = stripe.checkout.Session.create(
        mode="payment",
        line_items=[{
            "quantity": 1,
            "price_data": {
                "currency": order.currency.lower(),
                "unit_amount": currency.to_minor_units(amount),
                "product_data": {"name": f"Tilet order #{order.id}"},
            },
        }],
        metadata={"order_id": str(order.id)},
        success_url=f"{settings.FRONTEND_URL}/payment/success?session_id={{CHECKOUT_SESSION_ID}}",
        cancel_url=f"{settings.FRONTEND_URL}/payment/cancelled",
    )
        Payment.objects.create(
            order=order, provider=Payment.Provider.STRIPE,
            reference=session.id, amount=amount, currency=order.currency,
        )
        
        
        return Response({"checkout_url": session.url, "reference": session.id}, status=201)



class StripeWebhookView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            event = stripe.Webhook.construct_event(
                request.body , 
                request.headers.get("Stripe-Signature", ""),
                settings.STRIPE_WEBHOOK_SECRET
            )
        except (ValueError, stripe.SignatureVerificationError):
            return Response(status=400)


        if event["type"] in (
            "checkout.session.completed",
            "checkout.session.async_payment_succeeded",
        ):
            session = event["data"]["object"]
            currency = Currency.objects.get(code=payment.currency)
            if session["payment_status"] == "paid":
                payment = Payment.objects.filter(provider=Payment.Provider.STRIPE, reference=session["id"]).first(

                )
                if(
                    payment and session["amount_total"] == currency.to_minor_units(payment.amount)
                    and  session["currency"].upper() == payment.currency
                ):
                    mark_payment_succeeded(payment.pk)

        return Response(status=200)
    