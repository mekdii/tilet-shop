from .models import ShippingZone

def get_zone(address):
    """City zone first, then country zone, then the fallback, otherwise None."""

    code = address.country.code
    city = address.city.strip().lower()

    zones = list(ShippingZone.objects.filter(is_active=True).select_related("currency"))
    matching = [
        z for z in zones
        if not z.is_fallback and code in{c.code for c in z.countries}
    ]
    for zone in matching:
        if zone.city and zone.city.lower() == city:
            return zone
        for zone in matching:
            if not zone.city:
                return zone
        for zone in zones:
            if zone.is_fallback:
                return zone
        return None