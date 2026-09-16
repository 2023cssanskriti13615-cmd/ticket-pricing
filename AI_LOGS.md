# AI DEVELOPMENT CONVERSATION

## Multiplex Ticket Pricing Engine — Auriga IT Round 2 AIR

> **Note:** This is a reconstructed development conversation based on the actual development process. It is organized from the beginning of the project through implementation, testing, documentation, and GitHub submission.

---

### PROJECT START

**User:**

I have my Auriga IT Round 2 AIR assessment. The task is to build a multiplex ticket pricing engine. I have created a GitHub Codespaces project called `ticket-pricing`.

I want to do it step by step. First understand the project, then we will implement it and test everything properly.

**AI:**

Sure. We should approach this in a structured way so we don't break working code.

The basic project should have a pricing engine that handles:

* Silver, Gold and Recliner ticket tiers
* Different prices
* Seat availability
* Festival discount
* Member discount with a cap
* Convenience fee per ticket
* GST
* Exact paisa-level calculations
* Clear line-by-line bill breakup

First, let's inspect the existing project structure and code before making changes.

---

### UNDERSTANDING THE PROJECT

**User:**

My project currently has these files:

```text
ticket-pricing/
├── app.py
├── web_app.py
├── pricing_engine.py
├── requirements.txt
├── templates/
│   └── index.html
├── static/
│   └── style.css
├── tests/
│   └── test_pricing.py
├── README.md
├── REASONING.md
├── AI_LOGS.md
└── .gitignore
```

**AI:**

Good. The structure is already suitable.

The important part is `pricing_engine.py`, because that contains the actual business logic.

The other files have different responsibilities:

* `pricing_engine.py` → pricing logic
* `app.py` → command-line usage
* `web_app.py` → Flask application
* `templates/index.html` → web page
* `static/style.css` → styling
* `tests/test_pricing.py` → automated tests
* `README.md` → project documentation
* `REASONING.md` → design decisions and reasoning
* `AI_LOGS.md` → AI-assisted development log
* `.gitignore` → ignores generated Python files

We should avoid changing unrelated files unless necessary.

---

### REVIEWING `pricing_engine.py`

**User:**

Here is my current `pricing_engine.py`.

```python
from decimal import Decimal, ROUND_HALF_UP


class PricingEngine:
    def __init__(
        self,
        tier_config,
        festival_discount=0,
        member_discount_percent=0,
        member_discount_cap=0,
        convenience_fee_per_ticket=0,
        gst_percent=0
    ):
        self.tier_config = tier_config
        self.festival_discount = self._money(festival_discount)
        self.member_discount_percent = Decimal(str(member_discount_percent))
        self.member_discount_cap = self._money(member_discount_cap)
        self.convenience_fee_per_ticket = self._money(convenience_fee_per_ticket)
        self.gst_percent = Decimal(str(gst_percent))

    def _money(self, value):
        return Decimal(str(value)).quantize(
            Decimal("0.01"),
            rounding=ROUND_HALF_UP
        )

    def calculate_bill(self, booking, is_member=False):
        ticket_subtotal = Decimal("0.00")
        total_tickets = 0
        ticket_lines = []

        for tier, quantity in booking.items():
            if tier not in self.tier_config:
                raise ValueError(f"Invalid ticket tier: {tier}")

            if not isinstance(quantity, int) or quantity <= 0:
                raise ValueError(
                    f"Quantity for {tier} must be a positive integer"
                )

            price = self._money(self.tier_config[tier]["price"])
            available = self.tier_config[tier]["available"]

            if quantity > available:
                raise ValueError(
                    f"Only {available} {tier} ticket(s) are available"
                )

            line_total = self._money(price * quantity)

            ticket_subtotal += line_total
            total_tickets += quantity

            ticket_lines.append({
                "tier": tier,
                "quantity": quantity,
                "price_per_ticket": price,
                "line_total": line_total
            })

        ticket_subtotal = self._money(ticket_subtotal)

        festival_discount = min(
            self.festival_discount,
            ticket_subtotal
        )

        after_festival = self._money(
            ticket_subtotal - festival_discount
        )

        member_discount = Decimal("0.00")

        if is_member and after_festival > 0:
            calculated_member_discount = self._money(
                after_festival * self.member_discount_percent / Decimal("100")
            )

            member_discount = min(
                calculated_member_discount,
                self.member_discount_cap,
                after_festival
            )

        after_discounts = self._money(
            after_festival - member_discount
        )

        convenience_fee = self._money(
            self.convenience_fee_per_ticket * total_tickets
        )

        taxable_amount = self._money(
            after_discounts + convenience_fee
        )

        gst = self._money(
            taxable_amount * self.gst_percent / Decimal("100")
        )

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
```

**AI:**

The current pricing logic is clear.

The calculation flow is:

```text
Ticket subtotal
      ↓
Festival discount
      ↓
Member discount
      ↓
Convenience fee
      ↓
GST
      ↓
Final total
```

Using `Decimal` and `ROUND_HALF_UP` is appropriate because the requirement says the total should be accurate to the exact paisa.

The existing code also correctly validates ticket tiers, quantities, and availability.

Before changing anything, let's run the existing tests.

---

### EXISTING TESTS

**User:**

I ran:

```bash
python -m unittest discover -s tests -v
```

It says:

```text
Ran 12 tests in 0.002s

OK
```

**AI:**

Perfect. The existing pricing functionality is passing all 12 tests.

We should preserve these tests while implementing the additional requirement.

---

### DOCUMENTATION

**User:**

I also want the README and reasoning document to look proper for the assessment.

**AI:**

Yes. The README should explain:

* What the project does
* Main features
* Project structure
* Pricing flow
* How to run the application
* How to run tests
* Money handling
* Architecture

`REASONING.md` should explain why the pricing calculation is structured this way, why `Decimal` is used, how validation works, and why the engine is reusable for different cinema counters.

We should keep the documentation factual and based on the actual implementation.

---

### GIT CHECK

**User:**

Initially, Git was only tracking the README and several project files were untracked.

**AI:**

That's okay. After the project files are finalized, we can stage them together.

Also, `.gitignore` should contain:

```text
__pycache__/
*.pyc
```

so generated Python cache files aren't committed.

---

# THE TWIST

**User:**

I found another part of the assignment:

> The solution must also import a messy seat-class price list — with duplicate names (in different cases), prices in inconsistent formats, blank values, and negative prices. Clean it into a correct price list and report what was imported, de-duplicated, and rejected.

Does my current system satisfy this?

**AI:**

No.

This is an important missing requirement.

Currently the pricing engine expects something like:

```python
{
    "silver": {
        "price": 150,
        "available": 10
    }
}
```

That is already-clean data.

The current code does not handle:

* `Silver` vs `silver` vs `SILVER`
* prices like `₹150`
* prices containing commas such as `1,000`
* blank prices
* negative prices
* invalid price values
* duplicate records
* an import report

So we need to add this functionality.

---

### DECIDING WHETHER TO CREATE A NEW FILE

**User:**

Can we do this in the old code itself? I don't want too many new files.

**AI:**

Yes.

We can add an `import_price_list()` method inside the existing `PricingEngine` class.

That keeps the project simple:

```text
pricing_engine.py

PricingEngine
│
├── import_price_list()
├── _money()
└── calculate_bill()
```

The importer and bill calculation remain separate methods, even though they are in the same file.

---

### IMPORTER DESIGN

**User:**

Explain how the messy list will work in simple terms.

**AI:**

Suppose the input is:

```python
[
    {"name": "Silver", "price": "150"},
    {"name": "silver", "price": "₹150"},
    {"name": "GOLD", "price": "250.50"},
    {"name": "Recliner", "price": "1,000"},
    {"name": "Gold", "price": ""},
    {"name": "VIP", "price": "-500"}
]
```

The system cleans it.

Names are normalized:

```text
Silver → silver
silver → silver
GOLD → gold
Recliner → recliner
```

Prices are normalized:

```text
150 → 150.00
₹150 → 150.00
250.50 → 250.50
1,000 → 1000.00
```

Blank and negative prices are rejected.

Duplicate normalized names are reported as de-duplicated.

The result contains:

```python
{
    "cleaned_prices": ...,
    "imported": ...,
    "deduplicated": ...,
    "rejected": ...
}
```

---

### DUPLICATE RULE

**User:**

What should happen if Silver appears multiple times?

**AI:**

Since the assignment says to de-duplicate but doesn't specify a conflict-resolution rule, we can use a simple deterministic rule:

The first valid occurrence is retained, and later occurrences of the same normalized seat class are reported as duplicates.

For example:

```text
Silver 150
silver 150
SILVER 150
```

becomes:

```text
silver → 150
```

and the other two records are reported as de-duplicated.

---

# IMPLEMENTATION

**User:**

Okay, give me the complete code for the files that need changing.

**AI:**

We'll keep the existing project structure and update only the necessary files:

* `pricing_engine.py`
* `tests/test_pricing.py`
* `README.md`
* `REASONING.md`

`requirements.txt` remains:

```text
Flask
```

`.gitignore` remains:

```text
__pycache__/
*.pyc
```

The existing pricing functionality should remain intact.

---

### TESTING THE NEW IMPLEMENTATION

**User:**

I updated the files. What should I run?

**AI:**

Run:

```bash
python -m unittest discover -s tests -v
```

This should test both the original pricing requirements and the new messy price-list functionality.

---

### FINAL TEST RESULT

**User:**

I ran it and got:

```text
test_blank_price_is_rejected ... ok
test_blank_seat_class_is_rejected ... ok
test_convenience_fee_is_per_ticket ... ok
test_duplicate_names_different_cases ... ok
test_festival_discount ... ok
test_festival_discount_cannot_exceed_subtotal ... ok
test_import_clean_price_list ... ok
test_import_report ... ok
test_inconsistent_price_formats ... ok
test_invalid_price_is_rejected ... ok
test_invalid_quantity ... ok
test_invalid_tier ... ok
test_member_discount ... ok
test_member_discount_cap ... ok
test_multiple_tier_booking ... ok
test_negative_price_is_rejected ... ok
test_no_discounts ... ok
test_single_tier_booking ... ok
test_sold_out_or_insufficient_seats ... ok
test_zero_quantity ... ok

----------------------------------------------------------------------
Ran 20 tests in 0.003s

OK
```

**AI:**

Excellent.

All 20 tests are passing.

That means the automated test suite currently covers:

* Original ticket pricing
* Availability
* Discounts
* Discount cap
* Convenience fee
* GST
* Money precision
* Messy price import
* Duplicate handling
* Inconsistent price formats
* Blank values
* Negative values
* Invalid values
* Import reporting

---

# FINAL GIT CHECK

**User:**

I ran:

```bash
git status
```

and got:

```text
On branch main
Your branch is up to date with 'origin/main'.

Changes not staged for commit:
        modified: README.md
        modified: REASONING.md
        modified: pricing_engine.py
        modified: tests/test_pricing.py
```

**AI:**

That's expected because these four files have been modified locally.

Before committing, let's check the diff.

Run:

```bash
git diff --stat
```

and:

```bash
git diff --check
```

---

### DIFF CHECK

**User:**

`git diff --stat` showed:

```text
README.md             |  39 +++++++-------
REASONING.md          |  87 ++++++++++++++++---------------
pricing_engine.py     | 119 +++++++++++++++++++++++++++++++++++++++---
tests/test_pricing.py | 293 +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++---------------------------------
4 files changed
```

Then `git diff --check` gave no output.

**AI:**

Good.

`git diff --check` showing no output means there are no whitespace errors detected in the changes.

The modified files are also the expected ones.

---

# COMMIT

**User:**

I ran:

```bash
git add .
git commit -m "Complete ticket pricing engine and messy price import"
```

and got:

```text
[main ecff971] Complete ticket pricing engine and messy price import
4 files changed, 377 insertions(+), 161 deletions(-)
```

**AI:**

Good. The changes have been committed successfully.

---

# PUSH TO GITHUB

**User:**

Then I ran:

```bash
git push origin main
```

and got:

```text
To https://github.com/2023cssanskriti13615-cmd/ticket-pricing
   67c934b..ecff971  main -> main
```

**AI:**

That confirms the latest commit was successfully pushed to the GitHub `main` branch.

The updated implementation is now on the repository.

---

# FINAL PROJECT UNDERSTANDING

**User:**

Explain the whole project to me once in an easy way so I understand what I built.

**AI:**

Think of the project as a multiplex ticket counter.

First, the system gets seat-class prices.

If the price list is messy, the importer cleans it:

```text
Messy price list
      ↓
Normalize names
      ↓
Normalize prices
      ↓
Reject blank/invalid/negative values
      ↓
Remove duplicates
      ↓
Clean price list + report
```

Then a customer makes a booking.

For example:

```text
2 Silver + 1 Gold
```

The pricing engine:

```text
Ticket subtotal
      ↓
Festival discount
      ↓
Member discount
      ↓
Convenience fee
      ↓
GST
      ↓
Final total
```

Finally, it returns a detailed bill containing the individual ticket lines and all charges/discounts.

The important files are:

* `pricing_engine.py` → brain of the application
* `app.py` → command-line interface
* `web_app.py` → Flask web interface
* `index.html` → webpage
* `style.css` → webpage styling
* `test_pricing.py` → automated checker
* `README.md` → project explanation
* `REASONING.md` → design decisions
* `AI_LOGS.md` → AI-assisted development record

The project currently has 20 passing automated tests and the latest changes have been pushed to GitHub.
