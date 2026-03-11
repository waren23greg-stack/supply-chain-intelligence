-- ================================
-- SUPPLY CHAIN INTELLIGENCE DB
-- ================================

CREATE DATABASE IF NOT EXISTS supply_chain;
USE supply_chain;

-- 1. SUPPLIERS
CREATE TABLE suppliers (
    supplier_id INT PRIMARY KEY AUTO_INCREMENT,
    supplier_name VARCHAR(100) NOT NULL,
    country VARCHAR(50),
    contact_email VARCHAR(100),
    rating DECIMAL(3,2),
    lead_time_days INT,
    created_at DATE
);

-- 2. PRODUCTS
CREATE TABLE products (
    product_id INT PRIMARY KEY AUTO_INCREMENT,
    product_name VARCHAR(100) NOT NULL,
    category VARCHAR(50),
    unit_price DECIMAL(10,2),
    reorder_level INT,
    supplier_id INT,
    FOREIGN KEY (supplier_id) REFERENCES suppliers(supplier_id)
);

-- 3. INVENTORY
CREATE TABLE inventory (
    inventory_id INT PRIMARY KEY AUTO_INCREMENT,
    product_id INT,
    warehouse_location VARCHAR(50),
    quantity_in_stock INT,
    last_updated DATE,
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);

-- 4. ORDERS
CREATE TABLE orders (
    order_id INT PRIMARY KEY AUTO_INCREMENT,
    product_id INT,
    supplier_id INT,
    order_date DATE,
    quantity_ordered INT,
    status VARCHAR(20) DEFAULT 'Pending',
    expected_delivery DATE,
    FOREIGN KEY (product_id) REFERENCES products(product_id),
    FOREIGN KEY (supplier_id) REFERENCES suppliers(supplier_id)
);

-- 5. SHIPMENTS
CREATE TABLE shipments (
    shipment_id INT PRIMARY KEY AUTO_INCREMENT,
    order_id INT,
    actual_delivery DATE,
    shipment_status VARCHAR(20),
    delay_days INT,
    carrier VARCHAR(50),
    FOREIGN KEY (order_id) REFERENCES orders(order_id)
);