<p align="center">
  <strong>✈ Make A Trip</strong>
</p>

<p align="center">
  A full-stack tourism booking web application — hotels, buses, cars, and tour packages — with role-based access, coupon discounts, review moderation, and a transparent cancellation &amp; refund policy.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10--3.13-3776AB?logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/Django-5.2-092E20?logo=django&logoColor=white" alt="Django">
  <img src="https://img.shields.io/badge/DRF-3.17-A30000?logo=django&logoColor=white" alt="Django REST Framework">
  <img src="https://img.shields.io/badge/Database-MySQL-4479A1?logo=mysql&logoColor=white" alt="MySQL">
  <img src="https://img.shields.io/badge/License-MIT-green" alt="License">
</p>

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [One-Command Setup](#one-command-setup)
  - [Manual Setup](#manual-setup)
  - [Demo Data](#demo-data)
- [Configuration](#configuration)
  - [Payments](#payments)
  - [Cancellation Policy](#cancellation-policy)
  - [Session & Security](#session--security)
- [API Reference](#api-reference)
  - [Accounts](#accounts)
  - [Hotels](#hotels)
  - [Transportation](#transportation)
  - [Packages](#packages)
  - [Coupons](#coupons)
  - [Reviews](#reviews)
  - [Dashboard](#dashboard)
- [Management Commands](#management-commands)
- [User Roles & Permissions](#user-roles--permissions)
- [Design Decisions](#design-decisions)
- [Contributing](#contributing)
- [License](#license)

---

## Overview

**Make A Trip** is a full-stack tourism booking platform built with Django and Django REST Framework. The frontend uses Django templates with vanilla HTML, CSS, and JavaScript, communicating with the backend REST API via `fetch`. The entire application runs on SQLite with zero external service dependencies.

Built from a formal Software Requirements Specification (SRS) document, the project implements:

- **Four booking modules** — Hotels, Buses, Cars, and Tour Packages
- **Two user roles** — Customer and Administrator
- **End-to-end booking lifecycle** — from browsing, booking, and payment to admin approval, completion, and cancellation with tiered refunds
- **Coupon system, review moderation, and email notifications**

---

## Features

### Customer Features

| Feature | Description |
|---|---|
| **Registration & OTP** | Email-based signup with 6-digit OTP verification (configurable expiry) |
| **Hotel Booking** | Search hotels, view rooms with photos/amenities, check availability, and book |
| **Bus Booking** | Browse bus routes, view interactive seat maps, select seats, and book |
| **Car Booking** | Browse cars by trip type (hourly, one-way, round trip) and book |
| **Tour Packages** | Browse bundled packages (hotel + transport), view inclusions/exclusions |
| **Coupons** | Apply fixed or percentage discount codes at checkout |
| **Reviews** | Rate and comment on confirmed bookings (one review per booking) |
| **Booking History** | Unified cross-module booking history with status filtering |
| **Cancellation** | Cancel bookings with tiered refund based on time before service date |
| **Profile Management** | Edit name, gender, phone, photo, and change password |
| **Password Reset** | OTP-based forgot/reset password flow |

### Administrator Features

| Feature | Description |
|---|---|
| **Listing Management** | Full CRUD for hotels, rooms, buses, cars, and packages |
| **Approval Workflow** | Approve or decline listings and bookings |
| **Coupon Management** | Create/edit coupons — fixed/percentage, global or per-user assignment |
| **Review Moderation** | Approve or decline customer reviews before they appear publicly |
| **Dashboard & Analytics** | Aggregate statistics — bookings per module, revenue, pending approvals |
| **All Bookings View** | View all bookings system-wide with status filtering |

---

## Tech Stack

| Layer | Technology                                               |
|---|----------------------------------------------------------|
| **Backend** | Python 3.10–3.13, Django 5.2, Django REST Framework 3.17 |
| **Frontend** | Django Templates, HTML5, CSS3, Vanilla JavaScript (ES6+) |
| **Database** | MySQL                                                    |
| **Authentication** | Django Session Auth + CSRF                               |
| **Password Hashing** | bcrypt (BCryptSHA256) with PBKDF2 fallback               |
| **Image Processing** | Pillow                                                   |
| **Typography** | Google Fonts (Poppins, Inter)                            |

---

## Project Structure

```
Make_A_Trip/
├── makeatrip/                  # Django project settings & root URL config
│   ├── settings.py             # All configuration, business rules, email, DRF
│   ├── urls.py                 # API routes (/api/...) + page routes
│   ├── views.py                # Page view functions (template rendering)
│   └── wsgi.py / asgi.py       # WSGI / ASGI entry points
│
├── core/                       # Shared foundation layer
│   ├── constants.py            # BookingStatus, ApprovalStatus, PaymentMethod, etc.
│   ├── email_service.py        # Email function
│   ├── models.py               # BookingBase — abstract base for all booking types
│   ├── permissions.py          # IsAdminUser, IsAdminOrReadOnly, IsOwnerOrAdmin
│   ├── utils.py                # Invoice ID generation, refund calculation, email
│   ├── validators.py           # Image upload validator
│   └── management/commands/    # Custom management commands
│       └── mark_completed_bookings.py
│
├── accounts/                   # User registration, OTP, login/logout, profile
│   ├── models.py               # Profile model (extends Django User)
│   ├── serializers.py          # Registration, login, profile serializers
│   ├── views.py                # Auth API endpoints
│   └── urls.py                 # /api/accounts/...
│
├── hotels/                     # Hotel & room management + bookings
│   ├── models.py               # Hotel, Room, Amenity, HotelBooking
│   ├── serializers.py          # Listing + booking serializers
│   ├── views.py                # Discovery, admin CRUD, booking endpoints
│   └── urls.py                 # /api/hotels/...
│
├── transportation/             # Bus & car management + bookings
│   ├── models.py               # Bus, Car, BusBooking, CarBooking
│   ├── serializers.py          # Listing + booking serializers
│   ├── views.py                # Discovery, admin CRUD, booking endpoints
│   └── urls.py                 # /api/transport/...
│
├── packages/                   # Tour package management + bookings
│   ├── models.py               # Package (links Hotel + Bus/Car), PackageBooking
│   ├── serializers.py          # Listing + booking serializers
│   ├── views.py                # Discovery, admin CRUD, booking endpoints
│   └── urls.py                 # /api/packages/...
│
├── coupons/                    # Discount coupon system
│   ├── models.py               # Coupon (fixed/percentage, expiry, usage cap)
│   ├── serializers.py          # Coupon serializer
│   ├── views.py                # CRUD + validation endpoints
│   └── urls.py                 # /api/coupons/...
│
├── reviews/                    # Rating & review system with moderation
│   ├── models.py               # Review (generic relation to any service/booking)
│   ├── serializers.py          # Review serializer
│   ├── views.py                # Create, list, moderate endpoints
│   └── urls.py                 # /api/reviews/...
│
├── dashboard/                  # Cross-module booking history + admin stats
│   ├── views.py                # my_booking_history, admin_all_bookings, admin_stats
│   └── urls.py                 # /api/dashboard/...
│
├── templates/                  # All HTML templates
│   ├── base.html               # Site-wide layout (header, nav, footer)
│   ├── home.html               # Landing page
│   ├── accounts/               # Register, login, OTP, profile, password reset
│   ├── hotels/                 # Hotel list & detail pages
│   ├── transportation/         # Bus/car list, detail, and seat selection
│   ├── packages/               # Package list & detail pages
│   ├── dashboard/              # Customer & admin dashboards
│   └── bookings/               # Booking history page
│
├── static/
│   ├── css/style.css           # Single stylesheet for the entire site
│   └── js/                     # JavaScript modules
│       ├── api.js              # Shared fetch/CSRF helper
│       ├── admin_dashboard.js  # Admin dashboard logic
│       ├── booking_history.js  # Booking history logic
│       ├── hotel_detail.js     # Hotel detail & booking
│       ├── hotels_list.js      # Hotel listing & search
│       ├── bus_detail.js       # Bus detail & seat selection
│       ├── bus_list.js         # Bus listing
│       ├── car_detail.js       # Car detail & booking
│       ├── car_list.js         # Car listing
│       ├── package_detail.js   # Package detail & booking
│       └── packages_list.js    # Package listing
│
├── media/                      # User-uploaded files (photos, images)
├── scripts/
│   └── seed_data.py            # Optional demo data loader
│
├── manage.py                   # Django management entry point
├── requirements.txt            # Python dependencies
├── setup_and_run.bat           # One-command setup (Windows)
├── setup_and_run.sh            # One-command setup (macOS / Linux)
└── db.sqlite3                  # SQLite database (auto-created)
```

---

## Getting Started

### Check the deployed projcet: [**LIVE**](https://make-a-trip-bzbv.onrender.com/)

### Prerequisites

- **Python 3.10 – 3.13** (Django 5.2 does not support 3.9 or older)
- **pip** (comes with Python)

No other tools, databases, or external services are required.

### One-Command Setup

The quickest way to get running — creates a virtual environment, installs dependencies, runs migrations, optionally loads demo data, and starts the dev server.

**Windows:**
```bash
setup_and_run.bat
```

**macOS / Linux:**
```bash
chmod +x setup_and_run.sh && ./setup_and_run.sh
```

Then open **http://127.0.0.1:8000/** in your browser.

### Manual Setup

```bash
# 1. Clone the repository
git clone https://github.com/zsaaupo/Make_A_Trip
cd Make_A_Trip

# 2. Create a virtual environment
python -m venv venv

#3. Activate the virtual environment
source venv/bin/activate  #macOS/Linux        
venv\Scripts\activate     #Windows

# 4. Install dependencies
pip install -r requirements.txt

# 5. Apply database migrations
python manage.py migrate

# 6. Start the development server
python manage.py runserver
```

Then open **http://127.0.0.1:8000/**.

### User Data

| Role | Email | Password |
|---|---|---|
| **Admin** | `zsaaupo008@gmail.com` | `Admin@12345` |
| **Customer** | `appuser@user.com` | `Customer@123456` |

> **Note:** To create an admin manually, use `python manage.py createsuperuser`. Admins don't have a public registration flow — the `is_staff` flag must be set via the Django admin panel or CLI.

---

## Configuration

All configuration lives in [`makeatrip/settings.py`](makeatrip/settings.py). Key settings can be overridden via environment variables.

### Payments

SSLCommerz Sandbox is used for `Pay Now` bookings. Add these values to your local `.env`:

```env
SSLCOMMERZ_STORE_ID=your_sandbox_store_id
SSLCOMMERZ_STORE_PASSWORD=your_sandbox_store_password
SSLCOMMERZ_SANDBOX=True
SSLCOMMERZ_CURRENCY=BDT
SSLCOMMERZ_CALLBACK_BASE_URL=https://your-public-domain.example
```

For local browser testing, `SSLCOMMERZ_CALLBACK_BASE_URL` can be left empty and Django will build callback URLs from the current request. For deployed testing, set it to the public HTTPS domain so SSLCommerz can reach `/api/payments/sslcommerz/success/`, `/fail/`, `/cancel/`, and `/ipn/`.

### Cancellation Policy

Tiered refund rules are defined in `settings.py` and applied automatically:

| Cancelled Before Service | Refund |
|---|---|
| ≥ 48 hours | 80% |
| ≥ 24 hours | 50% |
| < 24 hours | 0% (no refund) |

```python
CANCELLATION_POLICY = [
    (48, 80),   # ≥48h → 80% refund
    (24, 50),   # ≥24h → 50% refund
    (0,  0),    # <24h → no refund
]
```

### Session & Security

| Setting | Value | Reference |
|---|---|---|
| Password Hashing | BCrypt (SHA256) | NFR-SEC-02 |
| Session Timeout | 30 minutes | NFR-SEC-05 |
| Login Rate Limit | 10 attempts/min/IP | Brute-force mitigation |
| OTP Expiry | 10 minutes | Configurable |
| Min Password Length | 6 characters | Django validator |
| CSRF Protection | Enabled on all unsafe requests | — |

---

## API Reference

All REST API endpoints are mounted under `/api/`. Authentication uses Django session cookies with CSRF tokens.

### Accounts

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/accounts/csrf/` | Retrieve CSRF token |
| `POST` | `/api/accounts/register/` | Register a new customer |
| `POST` | `/api/accounts/verify-otp/` | Verify email with OTP |
| `POST` | `/api/accounts/resend-otp/` | Resend OTP to email |
| `POST` | `/api/accounts/login/` | Log in |
| `POST` | `/api/accounts/logout/` | Log out |
| `GET/PUT` | `/api/accounts/profile/` | View / update profile |
| `POST` | `/api/accounts/password-reset/` | Request password reset OTP |
| `POST` | `/api/accounts/password-reset/confirm/` | Confirm password reset |

### Hotels

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/hotels/` | List approved hotels (search/filter) |
| `GET` | `/api/hotels/amenities/` | List all amenities |
| `GET` | `/api/hotels/<id>/` | Hotel details + rooms |
| `GET/POST` | `/api/hotels/admin/` | Admin: list/create hotels |
| `GET/PUT/DELETE` | `/api/hotels/admin/<id>/` | Admin: manage a hotel |
| `POST` | `/api/hotels/admin/<id>/status/<status>/` | Admin: approve/decline hotel |
| `GET/POST` | `/api/hotels/admin/<hotel_id>/rooms/` | Admin: list/create rooms |
| `GET/PUT/DELETE` | `/api/hotels/admin/rooms/<id>/` | Admin: manage a room |
| `GET/POST` | `/api/hotels/bookings/` | List/create hotel bookings |
| `GET` | `/api/hotels/bookings/<id>/` | Booking details |
| `POST` | `/api/hotels/bookings/<id>/cancel/` | Cancel a booking |
| `POST` | `/api/hotels/bookings/<id>/status/<status>/` | Admin: confirm/decline booking |

### Transportation

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/transport/buses/` | List approved buses |
| `GET` | `/api/transport/buses/<id>/` | Bus details + seat map |
| `GET/POST` | `/api/transport/admin/buses/` | Admin: list/create buses |
| `GET/PUT/DELETE` | `/api/transport/admin/buses/<id>/` | Admin: manage a bus |
| `POST` | `/api/transport/admin/buses/<id>/status/<status>/` | Admin: approve/decline bus |
| `GET` | `/api/transport/cars/` | List approved cars |
| `GET` | `/api/transport/cars/<id>/` | Car details |
| `GET/POST` | `/api/transport/admin/cars/` | Admin: list/create cars |
| `GET/PUT/DELETE` | `/api/transport/admin/cars/<id>/` | Admin: manage a car |
| `POST` | `/api/transport/admin/cars/<id>/status/<status>/` | Admin: approve/decline car |
| `GET/POST` | `/api/transport/bus-bookings/` | List/create bus bookings |
| `GET` | `/api/transport/bus-bookings/<id>/` | Bus booking details |
| `POST` | `/api/transport/bus-bookings/<id>/cancel/` | Cancel a bus booking |
| `POST` | `/api/transport/bus-bookings/<id>/status/<status>/` | Admin: confirm/decline |
| `GET/POST` | `/api/transport/car-bookings/` | List/create car bookings |
| `GET` | `/api/transport/car-bookings/<id>/` | Car booking details |
| `POST` | `/api/transport/car-bookings/<id>/cancel/` | Cancel a car booking |
| `POST` | `/api/transport/car-bookings/<id>/status/<status>/` | Admin: confirm/decline |

### Packages

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/packages/` | List approved packages |
| `GET` | `/api/packages/<id>/` | Package details |
| `GET/POST` | `/api/packages/admin/` | Admin: list/create packages |
| `GET/PUT/DELETE` | `/api/packages/admin/<id>/` | Admin: manage a package |
| `POST` | `/api/packages/admin/<id>/status/<status>/` | Admin: approve/decline |
| `GET/POST` | `/api/packages/bookings/` | List/create package bookings |
| `GET` | `/api/packages/bookings/<id>/` | Package booking details |
| `POST` | `/api/packages/bookings/<id>/cancel/` | Cancel a package booking |
| `POST` | `/api/packages/bookings/<id>/status/<status>/` | Admin: confirm/decline |

### Coupons

| Method | Endpoint | Description |
|---|---|---|
| `GET/POST` | `/api/coupons/` | Admin: list/create coupons |
| `GET` | `/api/coupons/mine/` | Customer: view assigned coupons |
| `POST` | `/api/coupons/validate/` | Validate a coupon code at checkout |
| `GET/PUT/DELETE` | `/api/coupons/<id>/` | Admin: manage a coupon |

### Reviews

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/reviews/` | List approved reviews (filterable) |
| `POST` | `/api/reviews/create/` | Submit a review for a confirmed booking |
| `GET` | `/api/reviews/pending/` | Admin: list pending reviews |
| `POST` | `/api/reviews/<id>/moderate/` | Admin: approve/decline a review |

### Dashboard

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/dashboard/my-bookings/` | Customer: full booking history |
| `GET` | `/api/dashboard/admin/all-bookings/` | Admin: all bookings system-wide |
| `GET` | `/api/dashboard/admin/stats/` | Admin: aggregate statistics |

### Payments

| Method | Endpoint | Description |
|---|---|---|
| `GET/POST` | `/api/payments/sslcommerz/success/` | SSLCommerz success callback; validates payment and confirms booking |
| `GET/POST` | `/api/payments/sslcommerz/fail/` | SSLCommerz failure callback; declines booking |
| `GET/POST` | `/api/payments/sslcommerz/cancel/` | SSLCommerz cancel callback; cancels booking |
| `POST` | `/api/payments/sslcommerz/ipn/` | SSLCommerz IPN callback; validates server-to-server notifications |

---

## Management Commands

| Command | Description |
|---|---|
| `python manage.py runserver` | Start the development server |
| `python manage.py migrate` | Apply database migrations |
| `python manage.py createsuperuser` | Create an admin account |

---

## User Roles & Permissions

| Role | How It's Created | Capabilities |
|---|---|---|
| **Customer** | Public registration (`/register/`) | Browse listings, make bookings, apply coupons, cancel bookings, submit reviews, manage profile |
| **Administrator** | `createsuperuser` or (`is_staff=True`) | All customer capabilities + create/edit/approve/decline listings, manage bookings, create coupons, moderate reviews, view analytics |

Permission enforcement is handled by three DRF permission classes:

- **`IsAdminUser`** — Requires `is_staff=True`
- **`IsAdminOrReadOnly`** — Anyone can read; only admins can write
- **`IsOwnerOrAdmin`** — Object-level: only the booking owner or an admin

---

## Design Decisions

The SRS was thorough, but some implementation details required assumptions:

| Decision | Rationale |
|---|---|
| **`Room.price_per_night` added** | Not in the SRS attributes table, but "sort hotels by price" is a requirement |
| **Admin = `is_staff` flag** | SRS specifies no public admin registration flow |
| **Car pricing: flat rate** | SRS says "calculated based on trip type and duration" but specifies no formula — admin sets the price |
| **Session-based auth** | Templates and API share an origin; CSRF tokens satisfy "secure token-based session management" without requiring JWT |
| **bcrypt password hashing** | Configured per NFR-SEC-02 |
| **Login rate limiting** | 10 attempts/min/IP as baseline brute-force mitigation |
| **Generic `Review` model** | One model backs all four service types via Django's ContentType framework; enforces one review per booking |
| **Coupon system** | Fixed/percentage discounts, expiry dates, min order amount, usage cap, global or per-user assignment |
| **Invoice ID format** | `<PREFIX>-<USR3>-<TIMESTAMP>` for human-readable, collision-resistant identifiers |

---

## Contributing

Contributions are welcome! To get started:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/your-feature`)
3. **Commit** your changes (`git commit -m "Add your feature"`)
4. **Push** to the branch (`git push origin feature/your-feature`)
5. **Open** a Pull Request

### Guidelines

- Follow PEP 8 for Python code
- Keep templates and JS files consistent with the existing structure
- Test your changes end-to-end before submitting
- Update this README if you add new features or endpoints

---

## License

This project is open source and available under the [MIT License](LICENSE).

---

<p align="center">
  Built with ❤️ for exploring the world, one booking at a time.
</p>
