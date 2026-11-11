from django.shortcuts import render
from rest_framework import serializers, viewsets
from rest_framework.filters import OrderingFilter
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from accounts.serializers import AddressSerializer
from orders.models import Order
from orders.serializers import OrderSerializer
from .serializers import ReturnShipmentSerializer , ShipOrderSerializer
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from .services import mark_delivered, mark_returned , ship_order




class StaffOrderSerializer(OrderSerializer):
    customer_name = serializers.SerializerMethodField()
    customer_phone = serializers.CharField(source="user.phone", read_only=True)
    ship_to = serializers.SerializerMethodField()


    class Meta(OrderSerializer.Meta):
        fields = OrderSerializer.Meta.fields + ["customer_name", "customer_phone", "ship_to"]


    def get_customer_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}".strip()


    def get_ship_to(self, obj):
        data = AddressSerializer(obj.address).data
        data["phone"] = data.get("phone") or obj.user.phone #fall back to the account phone
        return data


class StaffOrderViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAdminUser]
    serializer_class = StaffOrderSerializer
    filter_backends = [DjangoFilterBackend , OrderingFilter]
    filterset_fields = ["status"]
    ordering_fields = ["created_at" , "id"]

    def get_queryset(self):
        return (
            Order.objects.select_related("user", "address").prefetch_related
            ("shipments", "items__variant__product", "items__variant__color")
        )
    def _respond(self, pk):
        return Response(StaffOrderSerializer(self.get_queryset().get(pk=pk)).data)

    @action(detail=True, methods=["post"])
    def ship(self, request , pk=None):
        serializer = ShipOrderSerializer(data=request.data)      # carrier, tracking_number
        serializer.is_valid(raise_exception=True)
        ship_order(order_id=pk, **serializer.validated_data)
        return self._respond(pk)

    @action(detail=True, methods=["post"])
    def deliver(self, request, pk=None):
        mark_delivered(order_id=pk)
        return self._respond(pk)

    @action(detail=True, methods=["post"])
    def returned(self, request, pk=None):
        serializer = ReturnShipmentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        mark_returned(order_id=pk, **serializer.validated_data)
        return self._respond(pk)
