from decimal import Decimal, ROUND_HALF_UP


class PricingEngine:
    def __init__(
        self,
        tier_config=None,
        festival_discount=0,
        member_discount_percent=0,
        member_discount_cap=0,
        convenience_fee_per_ticket=0,
        gst_percent=0
    ):
        self.tier_config = tier_config or {}
        self.festival_discount = self._money(festival_discount)
        self.member_discount_percent = Decimal(str(member_discount_percent))
        self.member_discount_cap = self._money(member_discount_cap)
        self.convenience_fee_per_ticket = self._money(
            convenience_fee_per_ticket
        )
        self.gst_percent = Decimal(str(gst_percent))

    def _money(self, value):
        return Decimal(
            str(value)
            .replace(",", "")
            .replace("₹", "")
            .strip()
        ).quantize(
            Decimal("0.01"),
            rounding=ROUND_HALF_UP
        )

    def import_price_list(self, price_list):
        """
        Clean a messy seat-class price list.

        Returns:
        {
            "cleaned_prices": {...},
            "imported": [...],
            "deduplicated": [...],
            "rejected": [...]
        }
        """

        cleaned_prices = {}
        imported = []
        deduplicated = []
        rejected = []

        for row in price_list:

            if not isinstance(row, dict):
                rejected.append({
                    "row": row,
                    "reason": "Invalid row format"
                })
                continue

            raw_name = row.get("name", "")
            raw_price = row.get("price", "")

            name = str(raw_name).strip().lower()

            if not name:
                rejected.append({
                    "row": row,
                    "reason": "Blank seat class name"
                })
                continue

            if raw_price is None or str(raw_price).strip() == "":
                rejected.append({
                    "row": row,
                    "reason": "Blank price"
                })
                continue

            try:
                price = self._money(raw_price)
            except (ValueError, TypeError, ArithmeticError):
                rejected.append({
                    "row": row,
                    "reason": "Invalid price format"
                })
                continue

            if price < 0:
                rejected.append({
                    "row": row,
                    "reason": "Negative price"
                })
                continue

            if name in cleaned_prices:
                deduplicated.append({
                    "row": row,
                    "seat_class": name,
                    "reason": "Duplicate seat class"
                })
                continue

            cleaned_prices[name] = {
                "price": price,
                "available": row.get("available", 0)
            }

            imported.append({
                "seat_class": name,
                "price": price
            })

        return {
            "cleaned_prices": cleaned_prices,
            "imported": imported,
            "deduplicated": deduplicated,
            "rejected": rejected
        }

    def calculate_bill(self, booking, is_member=False):
        """
        Calculate the bill without changing seat availability.
        """

        ticket_subtotal = Decimal("0.00")
        total_tickets = 0
        ticket_lines = []

        for tier, quantity in booking.items():

            if tier not in self.tier_config:
                raise ValueError(
                    f"Invalid ticket tier: {tier}"
                )

            if (
                not isinstance(quantity, int)
                or isinstance(quantity, bool)
                or quantity <= 0
            ):
                raise ValueError(
                    f"Quantity for {tier} must be a positive integer"
                )

            price = self._money(
                self.tier_config[tier]["price"]
            )

            available = self.tier_config[tier]["available"]

            if quantity > available:
                raise ValueError(
                    f"Only {available} {tier} ticket(s) are available"
                )

            line_total = self._money(
                price * quantity
            )

            ticket_subtotal += line_total
            total_tickets += quantity

            ticket_lines.append({
                "tier": tier,
                "quantity": quantity,
                "price_per_ticket": price,
                "line_total": line_total
            })

        ticket_subtotal = self._money(ticket_subtotal)

        # Festival discount
        festival_discount = min(
            self.festival_discount,
            ticket_subtotal
        )

        after_festival = self._money(
            ticket_subtotal - festival_discount
        )

        # Member discount
        member_discount = Decimal("0.00")

        if is_member and after_festival > 0:

            calculated_member_discount = self._money(
                after_festival
                * self.member_discount_percent
                / Decimal("100")
            )

            member_discount = min(
                calculated_member_discount,
                self.member_discount_cap,
                after_festival
            )

        after_discounts = self._money(
            after_festival - member_discount
        )

        # Convenience fee
        convenience_fee = self._money(
            self.convenience_fee_per_ticket
            * total_tickets
        )

        # Taxable amount
        taxable_amount = self._money(
            after_discounts + convenience_fee
        )

        # GST
        gst = self._money(
            taxable_amount
            * self.gst_percent
            / Decimal("100")
        )

        # Final amount
        final_total = self._money(
            taxable_amount + gst
        )

        return {
            "tickets": ticket_lines,
            "total_tickets": total_tickets,
            "ticket_subtotal": ticket_subtotal,
            "festival_discount": festival_discount,
            "member_discount": member_discount,
            "subtotal_after_discounts": after_discounts,
            "convenience_fee": convenience_fee,
            "taxable_amount": taxable_amount,
            "gst": gst,
            "final_total": final_total
        }

    def book_tickets(self, booking, is_member=False):
        """
        Book tickets and update remaining availability.

        The bill is calculated and all validations are completed first.
        Only after successful validation are the available seats reduced.
        """

        bill = self.calculate_bill(
            booking,
            is_member
        )

        # Update inventory only after successful calculation
        for tier, quantity in booking.items():
            self.tier_config[tier]["available"] -= quantity

        return bill