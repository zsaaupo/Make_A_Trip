"""
Optional helper: populates the database with demo data so you can explore
the app immediately (an admin account, a customer account, a hotel + room,
a bus, a car, a tour package, and a coupon).

Run with:  python manage.py shell < scripts/seed_data.py
"""
import datetime
from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from django.utils import timezone

from accounts.models import Profile
from hotels.models import Amenity, Hotel, Room
from transportation.models import Bus, Car
from packages.models import Package
from coupons.models import Coupon
from core.constants import ApprovalStatus, DiscountType

import io
from PIL import Image


def fake_image(name):
    buf = io.BytesIO()
    Image.new('RGB', (480, 320), color=(15, 110, 110)).save(buf, format='PNG')
    buf.seek(0)
    return ContentFile(buf.read(), name=name)


# --- Admin account --------------------------------------------------------
if not User.objects.filter(username='admin@makeatrip.local').exists():
    admin = User.objects.create_superuser('admin@makeatrip.local', 'admin@makeatrip.local', 'Admin@12345')
    Profile.objects.create(user=admin, full_name='Site Admin', gender='other', phone='0000000000', is_email_verified=True)
    print("Created admin login: admin@makeatrip.local / Admin@12345")

# --- Demo customer ----------------------------------------------------------
if not User.objects.filter(username='customer@example.com').exists():
    cust = User.objects.create_user('customer@example.com', 'customer@example.com', 'Customer@123', is_active=True)
    Profile.objects.create(user=cust, full_name='Jordan Customer', gender='other', phone='1234567890', is_email_verified=True)
    print("Created demo customer login: customer@example.com / Customer@123")

# --- Amenities ---------------------------------------------------------------
for name in ['Balcony', 'Wi-Fi', 'Breakfast', 'Pool', 'Parking']:
    Amenity.objects.get_or_create(name=name)

# --- Hotel + room --------------------------------------------------------------
hotel, _ = Hotel.objects.get_or_create(
    name="Seabreeze Resort", location="Cox's Bazar",
    defaults={'description': 'Beachfront resort with sea-facing rooms.', 'status': ApprovalStatus.APPROVED},
)
if not hotel.rooms.exists():
    room = Room.objects.create(
        hotel=hotel,
        check_in_date=timezone.now().date(),
        check_out_date=timezone.now().date() + datetime.timedelta(days=90),
        photo=fake_image('room1.png'),
        bed_type=Room.BED_DOUBLE,
        climate_control='ac',
        total_availability=5,
        price_per_night=85,
    )
    room.amenities.set(Amenity.objects.filter(name__in=['Wi-Fi', 'Breakfast', 'Pool']))

# --- Bus -----------------------------------------------------------------------
if not Bus.objects.exists():
    Bus.objects.create(
        name="Green Line Express",
        trip_date=timezone.now() + datetime.timedelta(days=3),
        photo=fake_image('bus1.png'),
        climate_control='ac',
        route_origin='Dhaka',
        route_destination="Cox's Bazar",
        total_seats=36,
        price_per_seat=22,
        status=ApprovalStatus.APPROVED,
    )

# --- Car -----------------------------------------------------------------------
if not Car.objects.exists():
    Car.objects.create(
        name="Toyota Noah (Intercity)",
        trip_date=timezone.now() + datetime.timedelta(days=5),
        photo=fake_image('car1.png'),
        climate_control='ac',
        capacity=4,
        trip_type='intercity_one_way',
        price=60,
        status=ApprovalStatus.APPROVED,
    )

# --- Package -----------------------------------------------------------------
if not Package.objects.exists():
    Package.objects.create(
        name="Cox's Bazar Beach Getaway",
        date=(timezone.now() + datetime.timedelta(days=10)).date(),
        location="Cox's Bazar",
        type='couple',
        duration='3 Days 2 Nights',
        hotel=hotel,
        inclusions='Hotel stay, breakfast, beach tour',
        exclusions='Lunch & dinner, personal expenses',
        photo=fake_image('package1.png'),
        price=150,
        status=ApprovalStatus.APPROVED,
    )

# --- Coupon ---------------------------------------------------------------------
Coupon.objects.get_or_create(
    code='WELCOME10',
    defaults={
        'discount_type': DiscountType.PERCENTAGE,
        'discount_value': 10,
        'expiry_date': (timezone.now() + datetime.timedelta(days=365)).date(),
        'min_order_amount': 20,
        'max_usage_count': 1000,
        'is_global': True,
    },
)

print("Seed data ready.")
