from django.urls import include , path
from rest_framework.routers import DefaultRouter

from .views import StaffOrderViewSet
from .views import ShippingQuateView, StaffOrderViewSet

router = DefaultRouter()
router.register("staff/orders", StaffOrderViewSet, basename="staff-order")


urlpatterns = [
    path("", include(router.urls)),
    path("shipping/quote/", ShippingQuateView.as_view())
]
