
from .models import Cart, CartItem
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db import transaction
from rest_framework.exceptions import ValidationError
from rest_framework import status
from django.shortcuts import get_object_or_404
from orders.services import place_order

from orders.serializers import OrderSerializer
from .serializer import CartItemSerializer, CartCheckoutSerializer, CartSerializer, AddToCartSerializer, UpdateCartItemSerializer


def load_cart(user):
    """get or create the user's cart , with everything the serializer needs"""
    Cart.objects.get_or_create(user=user)
    return Cart.objects.prefetch_related("items__variant__product" , "items__variant__color").get(user=user)



class CartView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(CartSerializer(load_cart(request.user)).data)

    def delete(self , request):
        CartItem.objects.filter(cart__user=request.user).delete()
        return Response(CartSerializer(load_cart(request.user)).data)


class AddCartItemView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = AddToCartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        variant= serializer.validated_data["variant"]
        qty = serializer.validated_data["quantity"]

        cart, _ = Cart.objects.get_or_create(user=request.user)
        with transaction.atomic():
            item, _ = CartItem.objects.get_or_create(
                cart=cart , variant=variant, defaults={"quantity": 0}
            )
            new_qty = item.quantity + qty
            if new_qty > variant.stock:
                raise ValidationError(
                    f"Only {variant.stock} available. you already have {item.quantity}"
                )
            item.quantity = new_qty
            item.save(update_fields=["quantity"])

        return Response(CartSerializer(load_cart(request.user)).data, status= status.HTTP_201_CREATED)



class CartItemDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_items(self, request, pk):
        # filtering by the user first means somone elses item is 404

        return get_object_or_404(
            CartItem.objects.select_related("variant"),
            pk=pk, cart__user=request.user,
        )

    def patch(self, request , pk):
        item= self.get_items(request, pk)
        serializer = UpdateCartItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        qty = serializer.validated_data["quantity"]

        if qty > item.variant.stock:
            raise ValidationError(f"Only {item.variant.stock} available")

        item.quantity = qty
        item.save(update_fields= ["quantity"])
        return Response(CartSerializer(load_cart(request.user)).data)

    def delete(self, request, pk):
        self.get_item(request, pk).delete()
        return Response(CartSerializer(load_cart(request.user)).data)


class CartCheckoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = CartCheckoutSerializer(data=request.data, context= {"request": request})
        serializer.is_valid(raise_exception=True)

        with transaction.atomic():
            cart = get_object_or_404(Cart.objects.select_for_update(), user=request.user)
            items = [
                {"variant": ci.variant, "quantity": ci.quantity}
                for ci in cart.items.select_related("variant")
            ]
            if not items:
                raise ValidationError("your cart is empty")

            order = place_order(
                user=request.user,
                address=serializer.validated_data["address"],
                items= items,
            )
            cart.items.all().delete()

        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)
