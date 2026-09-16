# Solution Reasoning

## 1. Problem Understanding

The project is a reusable multiplex ticket pricing and billing system.

The system supports multiple ticket tiers and calculates the final bill after applying applicable discounts, convenience fees, and GST.

The main requirements handled by the pricing engine are:

- Multiple ticket tiers
- Ticket price and seat availability
- Ticket quantity validation
- Seat availability validation
- Festival discount
- Member percentage discount
- Member discount cap
- Per-ticket convenience fee
- GST calculation
- Accurate monetary calculations
- Detailed billing information

## 2. Project Architecture

The project separates the pricing logic from the user interface.

### `pricing_engine.py`

This file contains the `PricingEngine` class and all core pricing and validation logic.

### `app.py`

This provides the command-line version of the application.

### `web_app.py`

This provides the Flask-based web interface and uses the same pricing engine.

### `templates/index.html`

This contains the structure of the web interface.

### `static/style.css`

This contains the styling and responsive layout.

### `tests/test_pricing.py`

This contains automated unit tests for the pricing engine.

## 3. Pricing Calculation Flow

The pricing engine follows this sequence:

```text
Ticket Subtotal
       ↓
Festival Discount
       ↓
Member Discount
       ↓
Amount After Discounts
       ↓
Convenience Fee
       ↓
Taxable Amount
       ↓
GST
       ↓
Final Total