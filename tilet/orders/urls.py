from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import OrderViewSet, CheckoutView
router = DefaultRouter()
router.register("orders", OrderViewSet , basename="order")

urlpatterns = [
    path("", include(router.urls)), 
    path("checkout/", CheckoutView.as_view())
    
]