# Just-Ecommerce (Django)

A small, opinionated Django e-commerce starter built with Bootstrap for the UI and Paystack for payments. Includes products, a session-aware shopping cart (with Packet line items), order listing, and an easy-to-read template set.

## ⚡ Project Overview

- **Framework:** Django 5.0.x
- **Python:** 3.11+
- **Database:** PostgreSQL (tested), also works with SQLite for local dev
- **Payment:** Paystack (via included integration)
- **UI:** Bootstrap + simple inline CSS (templates live in `templates/`)

### Major Apps

- **products** — product model, list & detail views
- **cart** — cart model (Cart, Packet), add/remove/update, order listing
- **paystack** — payment integration and verification signal

This repo is intended as a compact starter you can extend (coupons, shipping, users, API, admin improvements, etc).

## Features

- Session-aware carts for anonymous visitors + automatic attach to authenticated user
- Packet intermediary: quantities and per-line sub_total
- Simple Paystack checkout button in cart summary
- Responsive Bootstrap product grid and product detail pages
- Small, modern UI tweaks (pill buttons, card shadows)

## Prerequisites

- Python 3.11+
- pip
- PostgreSQL (recommended) or SQLite for development
- Node/npm only if you want to build additional frontend assets (not required)

## Quickstart (Development)

```bash
# Clone
git clone <repo-url> just-ecommerce
cd just-ecommerce

# Create and activate venv (Windows)
python -m venv venv
venv\Scripts\activate

# Mac / Linux
# python -m venv venv
# source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env from example (see below)
cp .env.example .env
# Edit .env with real values

# Make migrations & migrate
python manage.py makemigrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run dev server
python manage.py runserver
```

Open http://127.0.0.1:8000/

## Environment Configuration

Create a `.env` file or set these environment variables in your system:

```env
DJANGO_SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost

# Database (example for PostgreSQL)
DATABASE_URL=postgres://dbuser:dbpass@localhost:5432/just_ecommerce_db

# Paystack
PAYSTACK_PUBLIC_KEY=pk_test_xxx
PAYSTACK_SECRET_KEY=sk_test_xxx
PAYSTACK_REF_LENGTH=12   # optional, default used by template tag

# Optional sentry/datadog keys if integrated
SENTRY_DSN=
DATADOG_API_KEY=
```

> **Note:** If you use `DATABASE_URL`, your project might be using `dj-database-url`; otherwise set `DATABASES` in `settings.py`.

## Paystack Setup

1. Create/obtain Paystack keys and paste into `.env`
2. The templates use a `paystack_button` template tag (in `paystack/templatetags`) which expects an amount, email, and ref
3. The project stores a `Cart.temp_id` (UUID or string) as payment ref — make sure your DB and Django model types align

## Getting Started

After completing the quickstart steps above, you can:

1. Access the Django admin at http://127.0.0.1:8000/admin/
2. Add products through the admin interface
3. Visit the frontend to browse products and test the cart functionality
4. Configure Paystack for payment processing

## Extending the Project

This starter is designed to be extended with additional features such as:

- User authentication and profiles
- Coupon/discount system
- Shipping calculations
- Product reviews
- API endpoints
- Enhanced admin interface
- Email notifications
- And more...

## Contributing

Feel free to submit issues and pull requests to improve this starter template.

## License

[Add your license here]