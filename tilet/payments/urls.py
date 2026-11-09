from django.urls import path
from .views import(ChapaIntiateView, ChapaVerifyView, ChapaWebhookView, StripeIntiateView, StripeWebhookView)


urlpatterns = [
    path("payments/chapa/initiate/", ChapaIntiateView.as_view()),
    path("payments/chapa/verify/", ChapaVerifyView.as_view()),
    path("payments/chapa/webhook/", ChapaWebhookView.as_view()),
    path("payments/stripe/initiate/", StripeIntiateView.as_view()),
    path("payments/stripe/webhook/", StripeWebhookView.as_view())
]
