import unittest
from decimal import Decimal

from pricing_engine import PricingEngine


class TestPricingEngine(unittest.TestCase):

    def setUp(self):
        self.tier_config = {
            "Silver": {
                "price": 150,
                "available": 50
            },
            "Gold": {
                "price": 250,
                "available": 30
            },
            "Recliner": {
                "price": 400,
                "available": 10
            }
        }

        self.engine = PricingEngine(
            tier_config=self.tier_config,
            festival_discount=50,
            member_discount_percent=10,
            member_discount_cap=100,
            convenience_fee_per_ticket=20,
            gst_percent=18
        )

    def test_single_tier_booking(self):
        bill = self.engine.calculate_bill(
            {"Silver": 2},
            is_member=False
        )

        self.assertEqual(bill["ticket_subtotal"], Decimal("300.00"))
        self.assertEqual(bill["convenience_fee"], Decimal("40.00"))
        self.assertEqual(bill["final_total"], Decimal("342.20"))

    def test_multiple_tier_booking(self):
        bill = self.engine.calculate_bill(
            {
                "Silver": 2,
                "Gold": 1
            },
            is_member=False
        )

        self.assertEqual(bill["ticket_subtotal"], Decimal("550.00"))
        self.assertEqual(bill["total_tickets"], 3)

    def test_festival_discount(self):
        bill = self.engine.calculate_bill(
            {"Silver": 2},
            is_member=False
        )

        self.assertEqual(
            bill["festival_discount"],
            Decimal("50.00")
        )

    def test_member_discount(self):
        bill = self.engine.calculate_bill(
            {"Gold": 2},
            is_member=True
        )

        # Subtotal = 500
        # Festival discount = 50
        # Remaining = 450
        # 10% member discount = 45
        self.assertEqual(
            bill["member_discount"],
            Decimal("45.00")
        )

    def test_member_discount_cap(self):
        bill = self.engine.calculate_bill(
            {"Recliner": 10},
            is_member=True
        )

        # Member discount is capped at ₹100
        self.assertEqual(
            bill["member_discount"],
            Decimal("100.00")
        )

    def test_sold_out_or_insufficient_seats(self):
        with self.assertRaises(ValueError):
            self.engine.calculate_bill(
                {"Recliner": 11},
                is_member=False
            )

    def test_invalid_tier(self):
        with self.assertRaises(ValueError):
            self.engine.calculate_bill(
                {"Platinum": 1},
                is_member=False
            )

    def test_invalid_quantity(self):
        with self.assertRaises(ValueError):
            self.engine.calculate_bill(
                {"Silver": -1},
                is_member=False
            )

    def test_zero_quantity(self):
        with self.assertRaises(ValueError):
            self.engine.calculate_bill(
                {"Silver": 0},
                is_member=False
            )
    def test_no_discounts(self):
        engine = PricingEngine(
            tier_config=self.tier_config,
            festival_discount=0,
            member_discount_percent=0,
            member_discount_cap=0,
            convenience_fee_per_ticket=20,
            gst_percent=18
        )

        bill = engine.calculate_bill(
            {"Silver": 1},
            is_member=False
        )

        # Ticket = 150
        # Fee = 20
        # Taxable = 170
        # GST = 30.60
        # Total = 200.60
        self.assertEqual(
            bill["final_total"],
            Decimal("200.60")
        )

    def test_festival_discount_cannot_exceed_subtotal(self):
        engine = PricingEngine(
            tier_config=self.tier_config,
            festival_discount=1000,
            member_discount_percent=0,
            member_discount_cap=0,
            convenience_fee_per_ticket=20,
            gst_percent=18
        )

        bill = engine.calculate_bill(
            {"Silver": 1},
            is_member=False
        )

        self.assertEqual(
            bill["festival_discount"],
            Decimal("150.00")
        )

    def test_convenience_fee_is_per_ticket(self):
        bill = self.engine.calculate_bill(
            {
                "Silver": 2,
                "Gold": 3
            },
            is_member=False
        )

        # 5 tickets × ₹20
        self.assertEqual(
            bill["convenience_fee"],
            Decimal("100.00")
        )

if __name__ == "__main__":
    unittest.main()