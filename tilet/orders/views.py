from django.shortcuts import render
from rest_framework import viewsets, status
from .serializers import OrderSerializer, CheckoutSerializer
from .models import Order, OrderItem
from rest_framework.decorators import action
from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import ValidationError
from store.models import ProductVariant
from django.db.models import F
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

# Create your views here.
class OrderViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes= [IsAuthenticated]
    serializer_class = OrderSerializer

    def get_queryset(self):
        return Order.objects.filter(user= self.request.user).prefetch_related("items__variant__product", "items__variant__color")

    @action(detail=True, methods=["post"])
    def cancel(self, request , pk=None):
        with transaction.atomic():
            order = get_object_or_404(Order.objects.select_for_update().filter(user=request.user), pk=pk,)

            if order.status != Order.Status.PENDING:
                raise ValidationError(f"A {order.status} order can not be cancelled")

            for item in order.items.order_by("variant_id"):
                ProductVariant.objects.filter(pk=item.variant_id).update(stock=F("stock") + item.quantity)

            order.status = Order.Status.CANCELLED
            order.save(update_fields=["status"])

        order = self.get_queryset().get(pk=order.pk)
        return Response(OrderSerializer(order).data)


class CheckoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = CheckoutSerializer(data= request.data, context= {"request": request})
        serializer.is_valid(raise_exception=True)

        address = serializer.validated_data["address"]
        items = serializer.validated_data["items"]

        with transaction.atomic():
            order = Order.objects.create(user= request.user , address = address)

            ids  = sorted(item["variant"].id for item in items)
            variants = (ProductVariant.objects.select_for_update().select_related("product").in_bulk(ids))

            for item in items:
                variant  = variants[item["variant"].id]
                qty = item["quantity"]
                if variant.stock < qty:
                    raise ValidationError(f"not enough stock for {variant}. only {variant.stock} left ")

                variant.stock -=qty
                variant.save(update_fields=["stock"])

                OrderItem.objects.create(order=order, variant=variant, quantity=qty, unit_price= variant.product.price)

                return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)



