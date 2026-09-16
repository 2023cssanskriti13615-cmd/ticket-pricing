# Multiplex Ticket Pricing Engine

A reusable ticket pricing and billing system for a multiplex cinema counter.

The application supports multiple ticket tiers, seat availability validation, festival and member discounts, per-ticket convenience fees, GST calculation, and a clear line-by-line bill.

The project includes both:
- A command-line application
- A simple web interface built using Flask

## Features

- Supports multiple ticket tiers:
  - Silver
  - Gold
  - Recliner
- Configurable ticket prices and seat availability
- Prevents booking more tickets than available
- Validates ticket tier and quantity
- Applies a flat festival discount
- Applies a percentage-based member discount with a maximum cap
- Adds convenience fee per ticket
- Calculates GST
- Uses `Decimal` for accurate monetary calculations
- Generates a clear line-by-line bill
- Responsive web interface
- Automated unit tests for pricing and validation logic

## Project Structure

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