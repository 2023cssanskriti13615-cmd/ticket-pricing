from pricing_engine import PricingEngine


# Cinema configuration
TIER_CONFIG = {
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


# Pricing rules
engine = PricingEngine(
    tier_config=TIER_CONFIG,
    festival_discount=50,
    member_discount_percent=10,
    member_discount_cap=100,
    convenience_fee_per_ticket=20,
    gst_percent=18
)


def get_quantity(tier):
    while True:
        try:
            quantity = int(input(f"Enter number of {tier} tickets: "))

            if quantity < 0:
                print("Quantity cannot be negative.")
                continue

            return quantity

        except ValueError:
            print("Please enter a valid whole number.")


def main():
    print("\n===================================")
    print("       MULTIPLEX TICKET BILLING")
    print("===================================")

    print("\nAvailable Tickets:")

    for tier, details in TIER_CONFIG.items():
        print(
            f"{tier}: ₹{details['price']:.2f} "
            f"({details['available']} available)"
        )

    booking = {}

    for tier in TIER_CONFIG:
        quantity = get_quantity(tier)

        if quantity > 0:
            booking[tier] = quantity

    if not booking:
        print("\nNo tickets selected.")
        return

    while True:
        member_input = input("\nAre you a member? (yes/no): ").strip().lower()

        if member_input in ("yes", "y"):
            is_member = True
            break

        if member_input in ("no", "n"):
            is_member = False
            break

        print("Please enter yes/y or no/n.")

    try:
        bill = engine.calculate_bill(
            booking=booking,
            is_member=is_member
        )

        print("\n===================================")
        print("              BILL")
        print("===================================")

        for ticket in bill["tickets"]:
            print(
                f"{ticket['tier']:10} "
                f"x {ticket['quantity']:<3} "
                f"@ ₹{ticket['price_per_ticket']:.2f} "
                f"= ₹{ticket['line_total']:.2f}"
            )

        print("-----------------------------------")
        print(f"Ticket Subtotal       : ₹{bill['ticket_subtotal']:.2f}")
        print(f"Festival Discount     : -₹{bill['festival_discount']:.2f}")
        print(f"Member Discount       : -₹{bill['member_discount']:.2f}")
        print(f"After Discounts       : ₹{bill['subtotal_after_discounts']:.2f}")
        print(f"Convenience Fee       : ₹{bill['convenience_fee']:.2f}")
        print(f"GST                   : ₹{bill['gst']:.2f}")
        print("-----------------------------------")
        print(f"FINAL TOTAL           : ₹{bill['final_total']:.2f}")
        print("===================================")

    except ValueError as error:
        print(f"\nBooking failed: {error}")


if __name__ == "__main__":
    main()