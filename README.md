# Multiplex Ticket Pricing Engine

A reusable ticket pricing engine for a multiplex booking counter.

The system calculates ticket bills accurately while handling seat tiers, availability, discounts, convenience fees, GST, and messy real-world price lists.

## Features

- Silver, Gold and Recliner ticket tiers
- Seat availability validation
- Invalid tier and quantity validation
- Flat festival discount
- Member percentage discount with a maximum cap
- Per-ticket convenience fee
- GST calculation
- Exact money calculation using Python Decimal
- Line-by-line bill breakup
- Messy seat-class price list import
- Case-insensitive duplicate detection
- Price format normalization
- Blank and negative price rejection
- Import report showing imported, de-duplicated and rejected records
- CLI and Flask web interface
- Automated unit tests

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