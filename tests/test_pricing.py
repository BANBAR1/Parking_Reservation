from datetime import timedelta
from decimal import Decimal

from parking_reservation.pricing import FreePricingRule


def test_free_rule_ignores_the_rate():
    rule = FreePricingRule()

    assert rule.calculate(rate=Decimal("2.50"), duration=timedelta(hours=3)) == Decimal("0.00")
