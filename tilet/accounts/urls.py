from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import LogoutView, RegisterView, AddressViewSet
from rest_framework.routers import DefaultRouter
router = DefaultRouter()
router.register("address", AddressViewSet, basename="address")

urlpatterns = [
    path("register/", RegisterView.as_view()),
    path("login/", TokenObtainPairView.as_view()),
    path("refresh/", TokenRefreshView.as_view()),
    path("logout/", LogoutView.as_view()),
    path("", include(router.urls)), 
    
]