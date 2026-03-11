CREATE DATABASE IF NOT EXISTS supply_chain_db;
USE supply_chain_db;
CREATE TABLE suppliers (
    supplier_id     INT PRIMARY KEY AUTO_INCREMENT,
    supplier_name   VARCHAR(100) NOT NULL,
    country         VARCHAR(50),
    contact_email   VARCHAR(100),
    lead_time_days  INT,           -- avg days from order to delivery
    reliability_score DECIMAL(3,2), -- 0.00 to 1.00
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP
);
SELECT * FROM  suppliers;

CREATE TABLE products (
    product_id      INT PRIMARY KEY AUTO_INCREMENT,
    product_name    VARCHAR(100) NOT NULL,
    category        VARCHAR(50),
    unit_cost       DECIMAL(10,2),
    unit_price      DECIMAL(10,2),
    reorder_level   INT,           -- trigger reorder when stock hits this
    supplier_id     INT,
    FOREIGN KEY (supplier_id) REFERENCES suppliers(supplier_id)
);
SELECT * FROM products;

CREATE TABLE inventory (
    inventory_id    INT PRIMARY KEY AUTO_INCREMENT,
    product_id      INT,
    warehouse       VARCHAR(50),
    quantity        INT,
    last_updated    DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);
SELECT *FROM inventory;

CREATE TABLE orders (
    order_id        INT PRIMARY KEY AUTO_INCREMENT,
    product_id      INT,
    supplier_id     INT,
    quantity        INT,
    order_date      DATE,
    expected_date   DATE,
    status          ENUM('Pending','Shipped','Delivered','Cancelled'),
    FOREIGN KEY (product_id) REFERENCES products(product_id),
    FOREIGN KEY (supplier_id) REFERENCES suppliers(supplier_id)
);
SELECT * FROM orders;

CREATE TABLE shipments (
    shipment_id INT PRIMARY KEY AUTO_INCREMENT,
    order_id INT,
    shipped_date DATE,
    delivered_date DATE,
    carrier VARCHAR(50),
    FOREIGN KEY (order_id) REFERENCES orders(order_id)
);

CREATE VIEW shipment_analysis AS
SELECT 
    sh.shipment_id,
    sh.order_id,
    sh.shipped_date,
    sh.delivered_date,
    sh.carrier,
    DATEDIFF(sh.delivered_date, sh.shipped_date) - s.lead_time_days AS delay_days
FROM shipments sh
JOIN orders o ON sh.order_id = o.order_id
JOIN suppliers s ON o.supplier_id = s.supplier_id;


INSERT INTO suppliers (supplier_name, country, contact_email, lead_time_days, reliability_score) VALUES
('FastTrack Logistics',     'USA',     'contact@fasttrack.com',   7,  0.95),
('GlobalParts Co.',         'China',   'sales@globalparts.cn',    21, 0.78),
('EuroSupply GmbH',         'Germany', 'info@eurosupply.de',      14, 0.89),
('AfriSource Ltd.',         'Kenya',   'ops@afrisource.co.ke',    10, 0.82),
('AsiaHub Trading',         'Vietnam', 'trade@asiahub.vn',        18, 0.74),
('PrimeMaterials Inc.',     'Canada',  'hello@primematerials.ca', 9,  0.91),
('QuickShip Express',       'UAE',     'qs@quickship.ae',         5,  0.97),
('SteadySupply Corp.',      'Brazil',  'info@steadysupply.br',    16, 0.80);

SELECT * FROM suppliers;
INSERT INTO products (product_name, category, unit_cost, unit_price, reorder_level, supplier_id) VALUES
('Industrial Bolt Set',       'Hardware',     12.50,  25.00,  100, 1),
('Steel Pipe 2inch',          'Raw Material', 45.00,  90.00,  50,  2),
('Circuit Board A1',          'Electronics',  88.00, 175.00,  30,  3),
('Rubber Seal Kit',           'Hardware',      8.75,  18.00,  200, 4),
('Hydraulic Pump',            'Machinery',   320.00, 640.00,  10,  5),
('Aluminum Sheet 1mm',        'Raw Material',  55.00, 110.00, 75,  6),
('Conveyor Belt 5m',          'Machinery',   210.00, 420.00,  15,  7),
('Electrical Cable 100m',     'Electronics',  95.00, 190.00,  40,  8),
('Safety Gloves (Pack 10)',   'Safety',        14.00,  28.00, 300, 1),
('Forklift Battery',          'Machinery',   450.00, 900.00,   8,  3);
SELECT * FROM products;

INSERT INTO inventory (product_id, warehouse, quantity) VALUES
(1,  'Nairobi Hub',      450),
(2,  'Nairobi Hub',       30),   -- below reorder level!
(3,  'Mombasa Port',      85),
(4,  'Nairobi Hub',      600),
(5,  'Kisumu Depot',       6),   -- below reorder level!
(6,  'Mombasa Port',     120),
(7,  'Nairobi Hub',       22),
(8,  'Kisumu Depot',      95),
(9,  'Nairobi Hub',      850),
(10, 'Mombasa Port',       5);  -- below reorder level!

SELECT * FROM inventory;
INSERT INTO orders (product_id, supplier_id, quantity, order_date, expected_date, status) VALUES
(1,  1, 500, '2024-11-01', '2024-11-08', 'Delivered'),
(2,  2, 100, '2024-11-05', '2024-11-26', 'Delivered'),
(3,  3,  50, '2024-11-10', '2024-11-24', 'Delivered'),
(4,  4, 300, '2024-11-12', '2024-11-22', 'Delivered'),
(5,  5,  20, '2024-11-15', '2024-12-03', 'Shipped'),
(6,  6, 200, '2024-11-18', '2024-11-27', 'Delivered'),
(7,  7,  30, '2024-11-20', '2024-11-25', 'Delivered'),
(8,  8,  80, '2024-11-22', '2024-12-08', 'Pending'),
(9,  1, 400, '2024-11-25', '2024-12-02', 'Shipped'),
(10, 3,  15, '2024-11-28', '2024-12-12', 'Pending'),
(2,  2, 150, '2024-12-01', '2024-12-22', 'Pending'),  -- restock order
(5,  5,  25, '2024-12-02', '2024-12-20', 'Pending');
SELECT * FROM orders;

INSERT INTO shipments (order_id, shipped_date, delivered_date, carrier) VALUES
(1, '2024-11-01', '2024-11-09', 'DHL'),
(2, '2024-11-05', '2024-11-28', 'China Post'),   -- 2 day delay
(3, '2024-11-10', '2024-11-23', 'FedEx'),         -- 1 day early
(4, '2024-11-12', '2024-11-24', 'AfriExpress'),   -- 2 day delay
(6, '2024-11-18', '2024-11-26', 'UPS'),
(7, '2024-11-20', '2024-11-24', 'QuickShip');     -- 1 day early
SELECT * FROM shipments;

USE supply_chain_db;

SELECT
    p.product_id,
    p.product_name,
    p.category,
    i.warehouse,
    i.quantity         AS current_stock,
    p.reorder_level,
    (p.reorder_level - i.quantity) AS units_short
FROM inventory i
JOIN products p ON i.product_id = p.product_id
WHERE i.quantity < p.reorder_level
ORDER BY units_short DESC;

SELECT
    s.supplier_id,
    s.supplier_name,
    s.country,
    s.reliability_score,
    COUNT(o.order_id)                        AS total_orders,
    SUM(CASE WHEN o.status = 'Delivered' 
             THEN 1 ELSE 0 END)              AS delivered_orders,
    AVG(DATEDIFF(sh.delivered_date, 
                 sh.shipped_date))           AS avg_transit_days,
    AVG(DATEDIFF(sh.delivered_date, 
                 o.expected_date))           AS avg_delay_days
FROM suppliers s
LEFT JOIN orders o    ON s.supplier_id = o.supplier_id
LEFT JOIN shipments sh ON o.order_id   = sh.order_id
GROUP BY s.supplier_id, s.supplier_name, s.country, s.reliability_score
ORDER BY avg_delay_days ASC;

SELECT
    i.warehouse,
    COUNT(DISTINCT i.product_id)            AS unique_products,
    SUM(i.quantity)                          AS total_units,
    SUM(i.quantity * p.unit_cost)            AS total_cost_value,
    SUM(i.quantity * p.unit_price)           AS total_retail_value,
    SUM(i.quantity * (p.unit_price - p.unit_cost)) AS potential_gross_profit
FROM inventory i
JOIN products p ON i.product_id = p.product_id
GROUP BY i.warehouse
ORDER BY total_retail_value DESC;

SELECT
    status,
    COUNT(*)            AS order_count,
    SUM(quantity)       AS total_units,
    MIN(order_date)     AS earliest_order,
    MAX(expected_date)  AS latest_expected
FROM orders
GROUP BY status
ORDER BY FIELD(status, 'Pending', 'Shipped', 'Delivered', 'Cancelled');

SELECT
    sh.carrier,
    s.supplier_name,
    COUNT(sh.shipment_id)                         AS shipments,
    AVG(DATEDIFF(sh.delivered_date, 
                 o.expected_date))                AS avg_delay_days,
    MAX(DATEDIFF(sh.delivered_date, 
                 o.expected_date))                AS worst_delay_days,
    SUM(CASE WHEN sh.delivered_date > o.expected_date 
             THEN 1 ELSE 0 END)                   AS late_shipments
FROM shipments sh
JOIN orders    o  ON sh.order_id    = o.order_id
JOIN suppliers s  ON o.supplier_id  = s.supplier_id
GROUP BY sh.carrier, s.supplier_name
ORDER BY avg_delay_days DESC;

CREATE OR REPLACE VIEW vw_supply_chain_summary AS
SELECT
    o.order_id,
    o.order_date,
    o.expected_date,
    o.status                                        AS order_status,
    p.product_name,
    p.category,
    p.unit_cost,
    p.unit_price,
    o.quantity                                      AS ordered_qty,
    (o.quantity * p.unit_cost)                      AS order_cost,
    s.supplier_name,
    s.country                                       AS supplier_country,
    s.reliability_score,
    sh.carrier,
    sh.shipped_date,
    sh.delivered_date,
    DATEDIFF(sh.delivered_date, o.expected_date)    AS delay_days,
    i.warehouse,
    i.quantity                                      AS stock_on_hand,
    p.reorder_level,
    CASE WHEN i.quantity < p.reorder_level 
         THEN 'REORDER NOW' ELSE 'OK' END           AS stock_status
FROM orders o
JOIN products  p  ON o.product_id  = p.product_id
JOIN suppliers s  ON o.supplier_id = s.supplier_id
LEFT JOIN shipments sh ON o.order_id = sh.order_id
LEFT JOIN inventory  i  ON p.product_id = i.product_id;