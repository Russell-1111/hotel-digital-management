from app.reservations import compute_total


def test_compute_total_example():
    # Two nights at 100 => subtotal 200, service 20 (10%), tax 13.2 (6% of 220), total 233.2
    total = compute_total(100.0, 2, 0.10, 0.06)
    assert total == 233.2


def test_zero_nights():
    assert compute_total(120.0, 0, 0.10, 0.06) == 0.0
