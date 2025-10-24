from __future__ import annotations

def compute_total(nightly_rate: float, nights: int, service_rate: float, tax_rate: float) -> float:
    if nights <= 0:
        return 0.0
    subtotal = nightly_rate * nights
    service = round(subtotal * service_rate, 2)
    tax_base = subtotal + service
    tax = round(tax_base * tax_rate, 2)
    total = round(subtotal + service + tax, 2)
    return total
