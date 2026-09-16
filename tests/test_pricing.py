import unittest
from decimal import Decimal

from pricing_engine import PricingEngine


class TestPricingEngine(unittest.TestCase):

    def setUp(self):
        self.tier_config = {
            "silver": {
                "price": 150,
                "available": 10
            },
            "gold": {
                "price": 250,
                "available": 5
            },
            "recliner": {
                "price": 400,
                "available": 2
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
        bill = self.engine.calculate_bill({
            "silver": 2
        })

        self.assertEqual(bill["total_tickets"], 2)
        self.assertEqual(bill["ticket_subtotal"], Decimal("300.00"))

    def test_multiple_tier_booking(self):
        bill = self.engine.calculate_bill({
            "silver": 2,
            "gold": 1
        })

        self.assertEqual(bill["total_tickets"], 3)
        self.assertEqual(bill["ticket_subtotal"], Decimal("550.00"))

    def test_no_discounts(self):
        engine = PricingEngine(
            tier_config=self.tier_config,
            convenience_fee_per_ticket=0,
            gst_percent=0
        )

        bill = engine.calculate_bill({
            "silver": 2
        })

        self.assertEqual(bill["final_total"], Decimal("300.00"))

    def test_festival_discount(self):
        bill = self.engine.calculate_bill({
            "silver": 2
        })

        self.assertEqual(
            bill["festival_discount"],
            Decimal("50.00")
        )

    def test_festival_discount_cannot_exceed_subtotal(self):
        engine = PricingEngine(
            tier_config=self.tier_config,
            festival_discount=1000
        )

        bill = engine.calculate_bill({
            "silver": 1
        })

        self.assertEqual(
            bill["festival_discount"],
            Decimal("150.00")
        )

    def test_member_discount(self):
        bill = self.engine.calculate_bill(
            {"silver": 2},
            is_member=True
        )

        self.assertEqual(
            bill["member_discount"],
            Decimal("25.00")
        )

    def test_member_discount_cap(self):
        engine = PricingEngine(
            tier_config=self.tier_config,
            member_discount_percent=50,
            member_discount_cap=20
        )

        bill = engine.calculate_bill(
            {"silver": 2},
            is_member=True
        )

        self.assertEqual(
            bill["member_discount"],
            Decimal("20.00")
        )

    def test_convenience_fee_is_per_ticket(self):
        bill = self.engine.calculate_bill({
            "silver": 3
        })

        self.assertEqual(
            bill["convenience_fee"],
            Decimal("60.00")
        )

    def test_invalid_tier(self):
        with self.assertRaises(ValueError):
            self.engine.calculate_bill({
                "platinum": 1
            })

    def test_invalid_quantity(self):
        with self.assertRaises(ValueError):
            self.engine.calculate_bill({
                "silver": -1
            })

    def test_zero_quantity(self):
        with self.assertRaises(ValueError):
            self.engine.calculate_bill({
                "silver": 0
            })

    def test_sold_out_or_insufficient_seats(self):
        with self.assertRaises(ValueError):
            self.engine.calculate_bill({
                "recliner": 3
            })

    # -----------------------------
    # TWIST: Messy Price List Tests
    # -----------------------------

    def test_import_clean_price_list(self):
        price_list = [
            {"name": "Silver", "price": "150"},
            {"name": "Gold", "price": "₹250.00"},
            {"name": "Recliner", "price": "400.00"}
        ]

        result = self.engine.import_price_list(price_list)

        self.assertEqual(
            result["cleaned_prices"]["silver"]["price"],
            Decimal("150.00")
        )

        self.assertEqual(
            result["cleaned_prices"]["gold"]["price"],
            Decimal("250.00")
        )

        self.assertEqual(
            result["cleaned_prices"]["recliner"]["price"],
            Decimal("400.00")
        )

    def test_duplicate_names_different_cases(self):
        price_list = [
            {"name": "Silver", "price": "150"},
            {"name": "silver", "price": "150"},
            {"name": "SILVER", "price": "150"}
        ]

        result = self.engine.import_price_list(price_list)

        self.assertEqual(
            len(result["cleaned_prices"]),
            1
        )

        self.assertEqual(
            len(result["deduplicated"]),
            2
        )

    def test_inconsistent_price_formats(self):
        price_list = [
            {"name": "Silver", "price": "₹150"},
            {"name": "Gold", "price": "250.5"},
            {"name": "Recliner", "price": "1,000"}
        ]

        result = self.engine.import_price_list(price_list)

        self.assertEqual(
            result["cleaned_prices"]["silver"]["price"],
            Decimal("150.00")
        )

        self.assertEqual(
            result["cleaned_prices"]["gold"]["price"],
            Decimal("250.50")
        )

        self.assertEqual(
            result["cleaned_prices"]["recliner"]["price"],
            Decimal("1000.00")
        )

    def test_blank_price_is_rejected(self):
        price_list = [
            {"name": "Silver", "price": ""},
            {"name": "Gold", "price": None}
        ]

        result = self.engine.import_price_list(price_list)

        self.assertEqual(
            len(result["rejected"]),
            2
        )

    def test_negative_price_is_rejected(self):
        price_list = [
            {"name": "Silver", "price": "-150"},
            {"name": "Gold", "price": "-₹250"}
        ]

        result = self.engine.import_price_list(price_list)

        self.assertEqual(
            len(result["rejected"]),
            2
        )

    def test_invalid_price_is_rejected(self):
        price_list = [
            {"name": "Silver", "price": "abc"},
            {"name": "Gold", "price": "hello"}
        ]

        result = self.engine.import_price_list(price_list)

        self.assertEqual(
            len(result["rejected"]),
            2
        )

    def test_blank_seat_class_is_rejected(self):
        price_list = [
            {"name": "", "price": "150"},
            {"name": "   ", "price": "250"}
        ]

        result = self.engine.import_price_list(price_list)

        self.assertEqual(
            len(result["rejected"]),
            2
        )

    def test_import_report(self):
        price_list = [
            {"name": "Silver", "price": "150"},
            {"name": "SILVER", "price": "150"},
            {"name": "Gold", "price": ""},
            {"name": "Recliner", "price": "-400"},
            {"name": "Gold Plus", "price": "300"}
        ]

        result = self.engine.import_price_list(price_list)

        self.assertEqual(len(result["imported"]), 2)
        self.assertEqual(len(result["deduplicated"]), 1)
        self.assertEqual(len(result["rejected"]), 2)


if __name__ == "__main__":
    unittest.main()