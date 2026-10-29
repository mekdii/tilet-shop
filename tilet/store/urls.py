
from rest_framework.routers import DefaultRouter
from .views import ProductViewSet, CategoryViewSet, OcasionViewSet
from django.urls import path, include
router = DefaultRouter()
router.register("products", ProductViewSet, basename="product")
router.register("categories", CategoryViewSet, basename="category" )
router.register("occasions", OcasionViewSet, basename="occasion")

urlpatterns = [
    path("", include(router.urls)), 

    
]