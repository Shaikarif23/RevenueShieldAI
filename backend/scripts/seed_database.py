"""
RevenueShieldAI realistic database seeder.

Usage from the backend directory:
    python -m scripts.seed_database

Optional environment variables:
    SEED_CUSTOMERS=10000
    SEED_RESTAURANTS=500
    SEED_DELIVERY_PARTNERS=1000
    SEED_ORDERS=50000
    SEED_BATCH_SIZE=1000
    SEED_RESET=true

The generator intentionally creates a small percentage of delivered orders
with missing/partial successful payments so the RevenueShield anomaly and
leakage dashboards have meaningful data to display.
"""

from __future__ import annotations

import os
import random
import string
from datetime import datetime, timedelta, timezone
from decimal import Decimal, ROUND_HALF_UP

from sqlalchemy import delete

from app.database import Base, SessionLocal, engine
from app.models import (
    Cancellation,
    Customer,
    DeliveryPartner,
    Menu,
    Order,
    OrderItem,
    OrderStatus,
    Payment,
    PaymentStatus,
    Restaurant,
    Review,
    Tracking,
    User,
)
from app.models.revenue import RevenueLeakage


SEED = int(os.getenv("SEED", "42"))
random.seed(SEED)

CUSTOMER_COUNT = int(os.getenv("SEED_CUSTOMERS", "10000"))
RESTAURANT_COUNT = int(os.getenv("SEED_RESTAURANTS", "500"))
DELIVERY_PARTNER_COUNT = int(os.getenv("SEED_DELIVERY_PARTNERS", "1000"))
ORDER_COUNT = int(os.getenv("SEED_ORDERS", "50000"))
BATCH_SIZE = int(os.getenv("SEED_BATCH_SIZE", "1000"))
RESET = os.getenv("SEED_RESET", "false").lower() == "true"

CITIES = [
    ("Hyderabad", 17.3850, 78.4867),
    ("Vijayawada", 16.5062, 80.6480),
    ("Visakhapatnam", 17.6868, 83.2185),
    ("Bengaluru", 12.9716, 77.5946),
    ("Chennai", 13.0827, 80.2707),
    ("Pune", 18.5204, 73.8567),
    ("Mumbai", 19.0760, 72.8777),
    ("Delhi", 28.6139, 77.2090),
]

RESTAURANT_PREFIXES = [
    "Spice", "Urban", "Royal", "Tasty", "Green", "Curry", "Fresh",
    "Annapurna", "Biryani", "Street", "Food", "Grand", "Flavours",
]
RESTAURANT_SUFFIXES = [
    "Kitchen", "Hub", "House", "Cafe", "Bites", "Restaurant", "Express",
    "Corner", "Foods", "Diner",
]
MENU_ITEMS = [
    ("Chicken Biryani", "Biryani", 280),
    ("Veg Biryani", "Biryani", 220),
    ("Paneer Butter Masala", "Main Course", 240),
    ("Butter Naan", "Breads", 55),
    ("Masala Dosa", "South Indian", 110),
    ("Idli Sambar", "South Indian", 80),
    ("Chicken Fried Rice", "Rice", 210),
    ("Veg Fried Rice", "Rice", 170),
    ("Chicken 65", "Starters", 190),
    ("Paneer Tikka", "Starters", 180),
    ("Veg Manchurian", "Starters", 160),
    ("Hakka Noodles", "Noodles", 170),
    ("Mango Lassi", "Beverages", 90),
    ("Cold Coffee", "Beverages", 120),
    ("Gulab Jamun", "Dessert", 80),
]

FIRST_NAMES = [
    "Arif", "Rahul", "Priya", "Sneha", "Kiran", "Aisha", "Ravi", "Anjali",
    "Suresh", "Neha", "Vikram", "Pooja", "Imran", "Divya", "Naveen",
    "Swathi", "Manoj", "Farhan", "Keerthi", "Akhil",
]


def money(value: float) -> float:
    return float(Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


def random_phone(i: int) -> str:
    return f"9{random.randint(100000000, 999999999)}"


def random_name() -> str:
    return f"{random.choice(FIRST_NAMES)} {random.choice(string.ascii_uppercase)}"


def random_point(city):
    _, lat, lon = city
    return round(lat + random.uniform(-0.08, 0.08), 6), round(lon + random.uniform(-0.08, 0.08), 6)


def clear_database(db):
    # Delete in dependency order. This is intentionally explicit because the
    # project currently has no dedicated production reset command.
    for model in (
        RevenueLeakage,
        Tracking,
        Cancellation,
        Review,
        Payment,
        OrderItem,
        Order,
        Menu,
        Customer,
        DeliveryPartner,
        Restaurant,
        User,
    ):
        db.execute(delete(model))
    db.commit()


def add_in_batches(db, objects):
    for start in range(0, len(objects), BATCH_SIZE):
        db.add_all(objects[start:start + BATCH_SIZE])
        db.commit()


def seed():
    db = SessionLocal()

    try:
        if RESET:
            print("Resetting existing application data...")
            clear_database(db)

        print("Creating database tables if necessary...")
        Base.metadata.create_all(bind=engine)

        # ----------------------------------------------------------
        # USERS + PROFILES
        # ----------------------------------------------------------
        print(f"Creating {CUSTOMER_COUNT} customers...")
        customer_users = []
        customers = []
        for i in range(1, CUSTOMER_COUNT + 1):
            city = random.choice(CITIES)
            lat, lon = random_point(city)
            user = User(
                name=random_name(),
                email=f"customer{i}@seed.revenueshield.local",
                password="SeedPass123!",
                phone=random_phone(i),
                role="CUSTOMER",
            )
            customer_users.append(user)
            # user_id is populated after flush below.
            customers.append((user, city, lat, lon))

        db.add_all(customer_users)
        db.flush()
        customer_rows = []
        for user, city, lat, lon in customers:
            customer_rows.append(
                Customer(
                    user_id=user.id,
                    default_address=f"{random.randint(1, 999)} Main Road, {city[0]}",
                    city=city[0],
                    latitude=lat,
                    longitude=lon,
                )
            )
        add_in_batches(db, customer_rows)

        print(f"Creating {RESTAURANT_COUNT} restaurants...")
        restaurant_users = []
        restaurants = []
        for i in range(1, RESTAURANT_COUNT + 1):
            city = random.choice(CITIES)
            lat, lon = random_point(city)
            user = User(
                name=f"Restaurant Admin {i}",
                email=f"restaurant{i}@seed.revenueshield.local",
                password="SeedPass123!",
                phone=random_phone(i),
                role="RESTAURANT",
            )
            restaurant_users.append(user)
            restaurants.append((user, city, lat, lon))

        db.add_all(restaurant_users)
        db.flush()
        restaurant_rows = []
        for i, (user, city, lat, lon) in enumerate(restaurants, 1):
            restaurant_rows.append(
                Restaurant(
                    user_id=user.id,
                    restaurant_name=f"{random.choice(RESTAURANT_PREFIXES)} {random.choice(RESTAURANT_SUFFIXES)} {i}",
                    address=f"{random.randint(1, 999)} Food Street, {city[0]}",
                    latitude=lat,
                    longitude=lon,
                    rating=round(random.uniform(3.2, 5.0), 1),
                )
            )
        add_in_batches(db, restaurant_rows)

        print(f"Creating {DELIVERY_PARTNER_COUNT} delivery partners...")
        partner_users = []
        partners = []
        for i in range(1, DELIVERY_PARTNER_COUNT + 1):
            city = random.choice(CITIES)
            lat, lon = random_point(city)
            user = User(
                name=f"Delivery Partner {i}",
                email=f"partner{i}@seed.revenueshield.local",
                password="SeedPass123!",
                phone=random_phone(i),
                role="DELIVERY_PARTNER",
            )
            partner_users.append(user)
            partners.append((user, city, lat, lon))

        db.add_all(partner_users)
        db.flush()
        partner_rows = []
        for i, (user, city, lat, lon) in enumerate(partners, 1):
            vehicle = random.choice(["BIKE", "SCOOTER", "BICYCLE"])
            partner_rows.append(
                DeliveryPartner(
                    user_id=user.id,
                    vehicle_type=vehicle,
                    vehicle_number=f"AP-{random.randint(10, 99)}-{random.choice(string.ascii_uppercase)}-{i:04d}",
                    current_status=random.choice(["AVAILABLE", "AVAILABLE", "BUSY", "OFFLINE"]),
                    current_latitude=lat,
                    current_longitude=lon,
                )
            )
        add_in_batches(db, partner_rows)

        # ----------------------------------------------------------
        # MENU
        # ----------------------------------------------------------
        print("Creating restaurant menus...")
        menu_rows = []
        for restaurant in restaurant_rows:
            selected = random.sample(MENU_ITEMS, k=random.randint(8, len(MENU_ITEMS)))
            for item_name, category, base_price in selected:
                price = money(base_price * random.uniform(0.85, 1.35))
                menu_rows.append(
                    Menu(
                        restaurant_id=restaurant.id,
                        item_name=item_name,
                        category=category,
                        price=price,
                        preparation_time=random.randint(8, 35),
                        ingredient_cost=money(price * random.uniform(0.28, 0.55)),
                        is_available="YES" if random.random() > 0.05 else "NO",
                    )
                )
        add_in_batches(db, menu_rows)

        # Index menu items by restaurant for fast order generation.
        menu_by_restaurant = {}
        for item in menu_rows:
            menu_by_restaurant.setdefault(item.restaurant_id, []).append(item)

        # ----------------------------------------------------------
        # ORDERS + CHILD DATA
        # ----------------------------------------------------------
        print(f"Creating {ORDER_COUNT} orders, payments, tracking and anomalies...")
        now = datetime.now(timezone.utc)
        customers_by_id = customer_rows
        orders = []

        for i in range(1, ORDER_COUNT + 1):
            customer = random.choice(customers_by_id)
            restaurant = random.choice(restaurant_rows)
            restaurant_menu = menu_by_restaurant[restaurant.id]

            # Delivered orders are deliberately dominant so the dashboard has
            # enough observations for leakage calculations.
            roll = random.random()
            if roll < 0.78:
                status = OrderStatus.DELIVERED
            elif roll < 0.86:
                status = OrderStatus.CANCELLED
            elif roll < 0.93:
                status = OrderStatus.ON_THE_WAY
            elif roll < 0.97:
                status = OrderStatus.PREPARING
            else:
                status = random.choice([
                    OrderStatus.PLACED,
                    OrderStatus.ACCEPTED,
                    OrderStatus.READY,
                    OrderStatus.PICKED_UP,
                ])

            partner = random.choice(partner_rows) if status not in (OrderStatus.PLACED, OrderStatus.CANCELLED) else None
            item_count = random.randint(1, 4)
            selected_items = random.choices(restaurant_menu, k=item_count)

            subtotal = 0.0
            for item in selected_items:
                subtotal += item.price * random.randint(1, 3)
            subtotal = money(subtotal)
            tax = money(subtotal * random.uniform(0.04, 0.12))
            delivery_charge = money(random.choice([20, 30, 40, 50, 60]))
            total = money(subtotal + tax + delivery_charge)

            created_at = now - timedelta(
                days=random.randint(0, 365),
                hours=random.randint(0, 23),
                minutes=random.randint(0, 59),
            )

            orders.append({
                "customer": customer,
                "restaurant": restaurant,
                "partner": partner,
                "status": status,
                "selected_items": selected_items,
                "subtotal": subtotal,
                "tax": tax,
                "delivery_charge": delivery_charge,
                "total": total,
                "created_at": created_at,
            })

        # Insert orders in batches, then use generated IDs for children.
        order_objects = []
        for data in orders:
            order_objects.append(
                Order(
                    customer_id=data["customer"].id,
                    restaurant_id=data["restaurant"].id,
                    delivery_partner_id=data["partner"].id if data["partner"] else None,
                    subtotal=data["subtotal"],
                    tax=data["tax"],
                    delivery_charge=data["delivery_charge"],
                    total_amount=data["total"],
                    status=data["status"],
                    created_at=data["created_at"],
                )
            )

        for start in range(0, len(order_objects), BATCH_SIZE):
            batch = order_objects[start:start + BATCH_SIZE]
            db.add_all(batch)
            db.flush()

            item_rows = []
            payment_rows = []
            tracking_rows = []
            cancellation_rows = []
            review_rows = []
            revenue_rows = []

            for order_obj, data in zip(batch, orders[start:start + BATCH_SIZE]):
                # Order items
                for item in data["selected_items"]:
                    quantity = random.randint(1, 3)
                    item_rows.append(
                        OrderItem(
                            order_id=order_obj.id,
                            menu_id=item.id,
                            quantity=quantity,
                            unit_price=item.price,
                            total_price=money(item.price * quantity),
                        )
                    )

                # Payment behavior is intentionally biased toward realistic
                # successful collection, with controlled leakage anomalies.
                total = data["total"]
                payment_status = PaymentStatus.SUCCESS
                amount = total

                if data["status"] == OrderStatus.DELIVERED:
                    anomaly_roll = random.random()
                    if anomaly_roll < 0.025:
                        # Full leakage: delivered but no successful collection.
                        payment_status = PaymentStatus.FAILED
                        amount = 0.0
                    elif anomaly_roll < 0.055:
                        # Partial collection.
                        payment_status = PaymentStatus.SUCCESS
                        amount = money(total * random.uniform(0.20, 0.85))
                    elif anomaly_roll < 0.07:
                        # Small but visible mismatch.
                        payment_status = PaymentStatus.SUCCESS
                        amount = money(total - random.uniform(1, min(150, total)))
                elif data["status"] == OrderStatus.CANCELLED:
                    payment_status = random.choice([PaymentStatus.REFUNDED, PaymentStatus.FAILED])
                    amount = 0.0 if payment_status == PaymentStatus.FAILED else total
                else:
                    payment_status = random.choice([
                        PaymentStatus.PENDING,
                        PaymentStatus.SUCCESS,
                    ])
                    amount = total if payment_status == PaymentStatus.SUCCESS else 0.0

                payment_rows.append(
                    Payment(
                        order_id=order_obj.id,
                        amount=amount,
                        payment_method=random.choice(["UPI", "CARD", "CASH", "WALLET", "NET_BANKING"]),
                        transaction_id=f"TXN-{order_obj.id}-{random.randint(100000, 999999)}",
                        status=payment_status,
                        created_at=data["created_at"] + timedelta(minutes=random.randint(1, 30)),
                    )
                )

                # Delivered orders get a tracking point; in-progress orders get
                # two points so delivery views have useful data without creating
                # hundreds of thousands of rows unnecessarily.
                tracking_rows.append(
                    Tracking(
                        order_id=order_obj.id,
                        status=data["status"].value,
                        latitude=data["restaurant"].latitude + random.uniform(-0.02, 0.02),
                        longitude=data["restaurant"].longitude + random.uniform(-0.02, 0.02),
                        updated_at=data["created_at"] + timedelta(minutes=random.randint(15, 90)),
                    )
                )

                if data["status"] == OrderStatus.CANCELLED:
                    refund = money(total * random.uniform(0.0, 1.0))
                    cancellation_rows.append(
                        Cancellation(
                            order_id=order_obj.id,
                            cancelled_by=random.choice(["CUSTOMER", "RESTAURANT", "SYSTEM"]),
                            reason=random.choice([
                                "Customer changed mind",
                                "Restaurant unavailable",
                                "Payment failure",
                                "Item unavailable",
                                "Delivery issue",
                            ]),
                            refund_amount=refund,
                            cancellation_fee=money(total * random.uniform(0, 0.10)),
                            cancelled_at=data["created_at"] + timedelta(minutes=random.randint(2, 60)),
                        )
                    )

                if data["status"] == OrderStatus.DELIVERED and random.random() < 0.45:
                    review_rows.append(
                        Review(
                            order_id=order_obj.id,
                            customer_id=data["customer"].id,
                            restaurant_id=data["restaurant"].id,
                            rating=random.choices([1, 2, 3, 4, 5], weights=[3, 4, 8, 25, 60])[0],
                            comment=random.choice([
                                "Good food and quick delivery.",
                                "Tasty and fresh.",
                                "Delivery was a little late.",
                                "Great experience.",
                                "Food quality was average.",
                            ]),
                            created_at=data["created_at"] + timedelta(hours=random.randint(1, 48)),
                        )
                    )

                # Populate the existing revenue model with cost information.
                ingredient_cost = money(data["subtotal"] * random.uniform(0.28, 0.55))
                labour_cost = money(data["subtotal"] * random.uniform(0.06, 0.14))
                packaging_cost = money(random.uniform(8, 30))
                utility_cost = money(random.uniform(2, 15))
                loss = money(
                    max(
                        ingredient_cost + labour_cost + packaging_cost + utility_cost
                        - data["subtotal"],
                        0,
                    )
                )
                revenue_rows.append(
                    RevenueLeakage(
                        order_id=order_obj.id,
                        ingredient_cost=ingredient_cost,
                        labour_cost=labour_cost,
                        packaging_cost=packaging_cost,
                        utility_cost=utility_cost,
                        cancellation_fee=0.0,
                        salvage_value=0.0,
                        loss_amount=loss,
                        created_at=data["created_at"],
                    )
                )

            db.add_all(item_rows)
            db.add_all(payment_rows)
            db.add_all(tracking_rows)
            db.add_all(cancellation_rows)
            db.add_all(review_rows)
            db.add_all(revenue_rows)
            db.commit()

            if (start + len(batch)) % (BATCH_SIZE * 5) == 0 or start + len(batch) == len(order_objects):
                print(f"  inserted {start + len(batch):,}/{len(order_objects):,} orders")

        print("\nSeed completed successfully.")
        print(f"Customers: {CUSTOMER_COUNT:,}")
        print(f"Restaurants: {RESTAURANT_COUNT:,}")
        print(f"Delivery partners: {DELIVERY_PARTNER_COUNT:,}")
        print(f"Orders: {ORDER_COUNT:,}")
        print("Seed login password: SeedPass123!")
        print("Customer email example: customer1@seed.revenueshield.local")
        print("Admin users are intentionally not created by this script.")

    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
