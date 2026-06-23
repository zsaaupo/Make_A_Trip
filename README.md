# Make a trip

A full-stack tourism booking web app built from the provided SRS + flowchart: hotel, bus, car and tour-package booking, with customer and admin roles, reviews, coupons, and a transparent cancellation/refund policy.

**Stack:** Django + Django REST Framework (API) + Django templates + vanilla HTML/CSS/JS (frontend talks to the API over `fetch`). SQLite database, no external services required to run it.

## 1. Quick start

### Easiest: one-command scripts
- **Windows:** double-click `setup_and_run.bat` (or run it from a terminal)
- **Mac/Linux:** `chmod +x setup_and_run.sh && ./setup_and_run.sh`

These create a virtual environment, install dependencies, run migrations, optionally load demo data, and start the server at **http://127.0.0.1:8000/**.

### Manual setup
Requires **Python 3.10–3.13** (Django 5.2 does not support 3.9 or older; not yet tested on 3.14+).

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Then open http://127.0.0.1:8000/.

### Demo data (optional but recommended)
Populates a sample hotel + room, bus, car, tour package, a coupon, and two ready-to-use logins:

```bash
python manage.py shell < scripts/seed_data.py
```

- **Admin:** `admin@makeatrip.local` / `Admin@12345`
- **Customer:** `customer@example.com` / `Customer@123`

Or skip the seed script and create your own admin with `python manage.py createsuperuser` (remember to also fill in their profile via `/django-admin/` since the public registration flow is customer-only, per the SRS).

## 2. How emails work locally
OTP codes and booking status emails are sent through Django's **console email backend** by default — they print straight to the terminal running `runserver` instead of actually being sent. This means registration/OTP/password-reset works out of the box with zero configuration.

To send real email, set environment variables before running the server (e.g. for Gmail, using an [app password](https://support.google.com/accounts/answer/185833)):

```bash
export EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
export EMAIL_HOST_USER=you@gmail.com
export EMAIL_HOST_PASSWORD=your-app-password
```

(`set` instead of `export` on Windows.)

## 3. Project structure
```
makeatrip/          Django project settings & root urls
core/                Shared constants, abstract booking model, invoice/refund helpers, permissions
accounts/            Registration, OTP email verification, login/logout, profile, password reset
hotels/              Hotel & Room models, search/booking API
transportation/      Bus (with seat map) & Car models, booking API
packages/            Tour package model (links a Hotel + a Bus/Car), booking API
coupons/             Fixed/percentage discount coupons
reviews/             Generic rating/review model shared by all four booking types, with moderation
dashboard/           Cross-module booking history + admin statistics endpoints
templates/           All page templates (extend templates/base.html)
static/css/style.css Single stylesheet for the whole site
static/js/           api.js (shared fetch/CSRF helper) + one file per page
scripts/seed_data.py Optional demo-data loader
```

Every Django app exposes its REST endpoints under `/api/...` (see each app's `urls.py`); page routes live in `makeatrip/urls.py` and render templates that call those endpoints with `fetch`.

## 4. Keeping booking statuses current
A booking moves to **Completed** once its service date has passed and it was previously Confirmed. Since that's time-based rather than triggered by a click, run this whenever you like (cron, Task Scheduler, or just manually while testing):

```bash
python manage.py mark_completed_bookings
```

## 5. Notable design decisions / assumptions
The SRS was very thorough, but a few implementation details weren't fully specified. Here's what was assumed, and why:

- **Room price field.** The Room attributes table didn't list a price, but "sort hotels by price" is a requirement — so `Room.price_per_night` was added.
- **Administrator accounts.** The SRS says admins don't have a public registration flow, so "admin" = Django's `is_staff` flag, set via `createsuperuser` or the seed script.
- **Car booking pricing.** The Car attributes table says price is "calculated based on trip type and duration" — implemented as a flat price the admin sets per listing (rather than a duration calculator), since no formula was specified.
- **Authentication.** Implemented with Django's session auth (the templates and API share an origin), with CSRF tokens on every unsafe request — this satisfies "secure token-based session management" without needing a separate JWT layer.
- **Password hashing.** bcrypt is configured as the primary hasher (NFR-SEC-02).
- **Brute-force mitigation.** The login endpoint is rate-limited (10 attempts/minute/IP). This is a baseline, not a complete brute-force defense system.
- **Coupons.** Implemented per spec (fixed/percentage, expiry, min order, usage cap, global or per-user assignment), applied at checkout via a coupon code field.
- **Reviews.** A single `Review` model (generic relation) backs hotels, buses, cars and packages, tied to a specific confirmed booking so a customer can't review something they didn't book, and capped at one review per booking.

## 6. Running tests manually
There's no automated test suite included, but the app has been exercised end-to-end (registration → OTP → login, hotel/bus/car/package booking with coupons, admin approve/decline, cancellation refund percentages, review submission + moderation) during development. If you'd like a pytest suite added, that's a reasonable next step.
