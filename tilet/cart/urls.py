from django.urls import path
from .views import AddCartItemView , CartCheckoutView, CartItemDetailView, CartView


urlpatterns = [
    path("cart/" , CartView.as_view()),
    path("cart/items/", AddCartItemView.as_view()),
    path("cart/items/<int:pk>/", CartItemDetailView.as_view()),
    path("cart/checkout/", CartCheckoutView.as_view())
]
