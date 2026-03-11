# ================================
# SUPPLY CHAIN DATA GENERATOR
# ================================

import pandas as pd
from faker import Faker
import mysql.connector
import random
from datetime import datetime, timedelta

fake = Faker()
random.seed(42)

# ================================
# DB CONNECTION
# ================================
conn = mysql.connector.connect(
    host="localhost",
    user="root",          # change if different
    password="yourpassword",  # change to your password
    database="supply_chain"
)
cursor = conn.cursor()

# ================================
# 1. GENERATE SUPPLIERS (50 rows)
# ================================
countries = ["USA", "China", "Germany", "India", "Brazil", "UK", "Japan"]
suppliers = []

for i in range(50):
    suppliers.append((
        fake.company(),
        random.choice(countries),
        fake.email(),
        round(random.uniform(2.5, 5.0), 2),
        random.randint(3, 30),
        fake.date_between(start_date="-3y", end_date="-1y")
    ))

cursor.executemany("""
    INSERT INTO suppliers (supplier_name, country, contact_email, rating, lead_time_days, created_at)
    VALUES (%s, %s, %s, %s, %s, %s)
""", suppliers)
conn.commit()
print("✅ Suppliers inserted")

# ================================
# 2. GENERATE PRODUCTS (200 rows)
# ================================
categories = ["Electronics", "Packaging", "Raw Materials", "Machinery", "Chemicals"]
products = []

for i in range(200):
    products.append((
        fake.bs().title(),
        random.choice(categories),
        round(random.uniform(5.0, 500.0), 2),
        random.randint(10, 100),
        random.randint(1, 50)
    ))

cursor.executemany("""
    INSERT INTO products (product_name, category, unit_price, reorder_level, supplier_id)
    VALUES (%s, %s, %s, %s, %s)
""", products)
conn.commit()
print("✅ Products inserted")

# ================================
# 3. GENERATE INVENTORY (200 rows)
# ================================
warehouses = ["Warehouse A", "Warehouse B", "Warehouse C", "Warehouse D"]
inventory = []

for i in range(1, 201):
    inventory.append((
        i,
        random.choice(warehouses),
        random.randint(0, 500),
        fake.date_between(start_date="-6m", end_date="today")
    ))

cursor.executemany("""
    INSERT INTO inventory (product_id, warehouse_location, quantity_in_stock, last_updated)
    VALUES (%s, %s, %s, %s)
""", inventory)
conn.commit()
print("✅ Inventory inserted")

# ================================
# 4. GENERATE ORDERS (5000 rows)
# ================================
statuses = ["Pending", "Delivered", "Cancelled", "In Transit"]
orders = []

for i in range(5000):
    order_date = fake.date_between(start_date="-2y", end_date="today")
    lead = random.randint(3, 30)
    expected = order_date + timedelta(days=lead)
    orders.append((
        random.randint(1, 200),
        random.randint(1, 50),
        order_date,
        random.randint(1, 100),
        random.choice(statuses),
        expected
    ))

cursor.executemany("""
    INSERT INTO orders (product_id, supplier_id, order_date, quantity_ordered, status, expected_delivery)
    VALUES (%s, %s, %s, %s, %s, %s)
""", orders)
conn.commit()
print("✅ Orders inserted")

# ================================
# 5. GENERATE SHIPMENTS (4000 rows)
# ================================
carriers = ["FedEx", "DHL", "UPS", "Maersk", "DB Schenker"]
shipments = []

for i in range(1, 4001):
    delay = random.randint(-2, 15)
    shipments.append((
        i,
        fake.date_between(start_date="-2y", end_date="today"),
        random.choice(["On Time", "Delayed", "Early"]),
        max(0, delay),
        random.choice(carriers)
    ))

cursor.executemany("""
    INSERT INTO shipments (order_id, actual_delivery, shipment_status, delay_days, carrier)
    VALUES (%s, %s, %s, %s, %s)
""", shipments)
conn.commit()
print("✅ Shipments inserted")

cursor.close()
conn.close()
print("\n🚀 All data generated successfully!")
print("   50 suppliers | 200 products | 200 inventory | 5000 orders | 4000 shipments")