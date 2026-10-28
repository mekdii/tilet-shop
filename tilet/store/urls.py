
from rest_framework.routers import DefaultRouter
from .views import ProductViewSet
from django.urls import path, include
router = DefaultRouter()
router.register("store", ProductViewSet, basename="stores")

urlpatterns = [
    path("", include(router.urls)), 
    
]