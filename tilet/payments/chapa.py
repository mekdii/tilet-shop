# payments/chapa.py
import logging

import requests
from django.conf import settings
from rest_framework.exceptions import APIException

logger = logging.getLogger(__name__)
BASE_URL = "https://api.chapa.co/v1"


class PaymentProviderError(APIException):
    status_code = 502
    default_detail = "The payment provider is unavailable. Please try again."


def _headers():
    return {"Authorization": f"Bearer {settings.CHAPA_SECRET_KEY}"}


def initialize(*, tx_ref, amount, user, return_url):
    body = {
        "amount": str(amount),
        "currency": "ETB",
        "email": settings.CHAPA_FALLBACK_EMAIL_DOMAIN,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "tx_ref": tx_ref,
        "return_url": return_url,
    }
    try:
        response = requests.post(
            f"{BASE_URL}/transaction/initialize", json=body, headers=_headers(), timeout=15
        )
        payload = response.json()
    except (requests.RequestException, ValueError):
        logger.exception("Chapa initialize failed")
        raise PaymentProviderError()

    if response.status_code != 200 or payload.get("status") != "success":
        logger.error("Chapa rejected initialize: %s", payload)
        raise PaymentProviderError()
    return payload["data"]["checkout_url"]


def verify(tx_ref):
    try:
        response = requests.get(
            f"{BASE_URL}/transaction/verify/{tx_ref}", headers=_headers(), timeout=15
        )
        return response.json()
    except (requests.RequestException, ValueError):
        logger.exception("Chapa verify failed")
        raise PaymentProviderError()