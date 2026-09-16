
### 4. `REASONING.md`

```markdown
# Reasoning and Design Decisions

## Problem Understanding

The goal is to build a reusable multiplex pricing engine that can calculate an accurate ticket bill for different seat tiers and booking situations.

The engine must handle:

- Different ticket prices
- Seat availability
- Festival discounts
- Member discounts
- Convenience fees
- GST
- Exact monetary calculations
- A messy real-world seat-class price list

## Architecture

The solution uses a `PricingEngine` class in `pricing_engine.py`.

The class has two main responsibilities:

1. Import and clean seat-class price data.
2. Calculate the final booking bill using the cleaned configuration.

## Messy Price List Cleaning

Real-world input may contain inconsistent data.

The importer therefore:

1. Removes whitespace from seat-class names.
2. Converts seat-class names to lowercase.
3. Converts supported money formats into `Decimal`.
4. Rejects blank prices.
5. Rejects invalid price values.
6. Rejects negative prices.
7. Detects duplicate seat-class names after normalization.
8. Produces a report containing imported, de-duplicated and rejected records.

## Duplicate Handling

Duplicate names are identified after case normalization.

For example:

- `Silver`
- `silver`
- `SILVER`

are treated as the same seat class.

The first valid occurrence is retained and later duplicates are reported as de-duplicated.

## Pricing Calculation

The calculation order is:

```text
Ticket Subtotal
        ↓
Festival Discount
        ↓
Member Discount
        ↓
Convenience Fee
        ↓
GST
        ↓
Final Total