from django.shortcuts import render
from rest_framework import viewsets
from .serializers import ReviewSerializer
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from .permissions import IsOwnerOrReadOnly
from .models import Review
from django_filters.rest_framework import DjangoFilterBackend

class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    queryset = Review.objects.select_related("user")
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["product", "rating"]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
