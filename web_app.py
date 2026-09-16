
from flask import Flask, render_template, request
from pricing_engine import PricingEngine

app = Flask(__name__)


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


@app.route("/", methods=["GET", "POST"])
def home():
    bill = None
    error = None

    quantities = {
        "Silver": 0,
        "Gold": 0,
        "Recliner": 0
    }

    is_member = False

    if request.method == "POST":
        try:
            # Read ticket quantities
            for tier in TIER_CONFIG:
                quantities[tier] = int(
                    request.form.get(tier, 0)
                )

            # Read membership status
            member_value = request.form.get("member", "no")
            is_member = member_value == "yes"

            # Create booking dictionary
            booking = {
                tier: quantity
                for tier, quantity in quantities.items()
                if quantity > 0
            }

            # Make sure at least one ticket is selected
            if not booking:
                raise ValueError(
                    "Please select at least one ticket."
                )

            # Book tickets and update remaining availability
            bill = engine.book_tickets(
                booking=booking,
                is_member=is_member
            )

        except ValueError as e:
            error = str(e)

    return render_template(
        "index.html",
        tiers=TIER_CONFIG,
        quantities=quantities,
        is_member=is_member,
        bill=bill,
        error=error
    )


if __name__ == "__main__":
    app.run(debug=True)
