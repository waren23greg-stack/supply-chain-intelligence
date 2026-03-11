-- ============================================================
--   SUPPLY CHAIN INTELLIGENCE PLATFORM
--   Advanced Analytics Queries
--   Author  : Supply Chain Intelligence Team
--   Database: MySQL 8.0+
--   Tables  : suppliers, products, inventory, orders, shipments
-- ============================================================

USE supply_chain;

-- ============================================================
-- SECTION 1: SUPPLIER PERFORMANCE SCORECARD
-- Ranks every supplier by delivery reliability, order volume,
-- and average delay — the holy trinity of procurement KPIs.
-- ============================================================

-- 1A. Full Supplier Scorecard with Performance Tier
SELECT
    s.supplier_id,
    s.supplier_name,
    s.country,
    s.rating                                                        AS supplier_rating,
    COUNT(o.order_id)                                               AS total_orders,
    SUM(o.quantity_ordered)                                         AS total_units_ordered,
    ROUND(AVG(sh.delay_days), 2)                                    AS avg_delay_days,
    SUM(CASE WHEN sh.shipment_status = 'On Time' THEN 1 ELSE 0 END) AS on_time_deliveries,
    SUM(CASE WHEN sh.shipment_status = 'Delayed'  THEN 1 ELSE 0 END) AS delayed_deliveries,
    ROUND(
        SUM(CASE WHEN sh.shipment_status = 'On Time' THEN 1 ELSE 0 END)
        / NULLIF(COUNT(sh.shipment_id), 0) * 100, 1
    )                                                               AS on_time_rate_pct,
    CASE
        WHEN ROUND(SUM(CASE WHEN sh.shipment_status = 'On Time' THEN 1 ELSE 0 END)
             / NULLIF(COUNT(sh.shipment_id), 0) * 100, 1) >= 85 THEN '🟢 ELITE'
        WHEN ROUND(SUM(CASE WHEN sh.shipment_status = 'On Time' THEN 1 ELSE 0 END)
             / NULLIF(COUNT(sh.shipment_id), 0) * 100, 1) >= 65 THEN '🟡 RELIABLE'
        WHEN ROUND(SUM(CASE WHEN sh.shipment_status = 'On Time' THEN 1 ELSE 0 END)
             / NULLIF(COUNT(sh.shipment_id), 0) * 100, 1) >= 45 THEN '🟠 AVERAGE'
        ELSE '🔴 AT RISK'
    END                                                             AS performance_tier
FROM suppliers s
LEFT JOIN orders o    ON s.supplier_id = o.supplier_id
LEFT JOIN shipments sh ON o.order_id   = sh.order_id
GROUP BY s.supplier_id, s.supplier_name, s.country, s.rating
ORDER BY on_time_rate_pct DESC, avg_delay_days ASC;


-- 1B. Top 10 Best Suppliers
SELECT
    s.supplier_name,
    s.country,
    ROUND(AVG(sh.delay_days), 2)   AS avg_delay_days,
    COUNT(o.order_id)              AS total_orders,
    ROUND(
        SUM(CASE WHEN sh.shipment_status = 'On Time' THEN 1 ELSE 0 END)
        / NULLIF(COUNT(sh.shipment_id), 0) * 100, 1
    )                              AS on_time_rate_pct
FROM suppliers s
JOIN orders o     ON s.supplier_id = o.supplier_id
JOIN shipments sh ON o.order_id    = sh.order_id
GROUP BY s.supplier_id, s.supplier_name, s.country
ORDER BY on_time_rate_pct DESC, avg_delay_days ASC
LIMIT 10;


-- 1C. Bottom 5 Worst Performing Suppliers (At Risk)
SELECT
    s.supplier_name,
    s.country,
    ROUND(AVG(sh.delay_days), 2) AS avg_delay_days,
    COUNT(o.order_id)            AS total_orders,
    ROUND(
        SUM(CASE WHEN sh.shipment_status = 'Delayed' THEN 1 ELSE 0 END)
        / NULLIF(COUNT(sh.shipment_id), 0) * 100, 1
    )                            AS delay_rate_pct
FROM suppliers s
JOIN orders o     ON s.supplier_id = o.supplier_id
JOIN shipments sh ON o.order_id    = sh.order_id
GROUP BY s.supplier_id, s.supplier_name, s.country
HAVING delay_rate_pct > 40
ORDER BY delay_rate_pct DESC, avg_delay_days DESC
LIMIT 5;


-- ============================================================
-- SECTION 2: INVENTORY HEALTH & STOCKOUT ALERTS
-- Identifies products at critical stock levels before they
-- cause supply chain disruptions.
-- ============================================================

-- 2A. Full Inventory Health Dashboard
SELECT
    p.product_id,
    p.product_name,
    p.category,
    p.unit_price,
    p.reorder_level,
    i.warehouse_location,
    i.quantity_in_stock,
    i.last_updated,
    ROUND(i.quantity_in_stock * p.unit_price, 2)   AS stock_value_usd,
    CASE
        WHEN i.quantity_in_stock = 0                        THEN '🔴 OUT OF STOCK'
        WHEN i.quantity_in_stock <= p.reorder_level * 0.5  THEN '🟠 CRITICAL'
        WHEN i.quantity_in_stock <= p.reorder_level        THEN '🟡 REORDER NOW'
        WHEN i.quantity_in_stock <= p.reorder_level * 1.5  THEN '🔵 ADEQUATE'
        ELSE                                                     '🟢 HEALTHY'
    END                                             AS stock_status,
    i.quantity_in_stock - p.reorder_level           AS buffer_units
FROM products p
JOIN inventory i ON p.product_id = i.product_id
ORDER BY quantity_in_stock ASC;


-- 2B. Critical Stockout Alert — Immediate Action Required
SELECT
    p.product_name,
    p.category,
    s.supplier_name,
    s.lead_time_days                               AS supplier_lead_days,
    i.warehouse_location,
    i.quantity_in_stock,
    p.reorder_level,
    p.reorder_level - i.quantity_in_stock          AS units_short,
    DATE_ADD(CURDATE(), INTERVAL s.lead_time_days DAY) AS earliest_restock_date
FROM products p
JOIN inventory i  ON p.product_id  = i.product_id
JOIN suppliers s  ON p.supplier_id = s.supplier_id
WHERE i.quantity_in_stock <= p.reorder_level
ORDER BY units_short DESC;


-- 2C. Total Inventory Value by Warehouse
SELECT
    i.warehouse_location,
    COUNT(DISTINCT p.product_id)            AS unique_products,
    SUM(i.quantity_in_stock)                AS total_units,
    ROUND(SUM(i.quantity_in_stock * p.unit_price), 2) AS total_value_usd,
    ROUND(AVG(i.quantity_in_stock), 1)      AS avg_stock_per_product
FROM inventory i
JOIN products p ON i.product_id = p.product_id
GROUP BY i.warehouse_location
ORDER BY total_value_usd DESC;


-- 2D. Inventory Turnover by Category
-- High turnover = fast moving goods = potential stockout risk
SELECT
    p.category,
    SUM(i.quantity_in_stock)                        AS current_stock,
    SUM(o.quantity_ordered)                         AS total_ordered_last_2yr,
    ROUND(SUM(o.quantity_ordered)
          / NULLIF(SUM(i.quantity_in_stock), 0), 2) AS turnover_ratio,
    CASE
        WHEN ROUND(SUM(o.quantity_ordered)
             / NULLIF(SUM(i.quantity_in_stock), 0), 2) > 20 THEN '⚡ HIGH VELOCITY'
        WHEN ROUND(SUM(o.quantity_ordered)
             / NULLIF(SUM(i.quantity_in_stock), 0), 2) > 10 THEN '➡️  MODERATE'
        ELSE '🐢 SLOW MOVING'
    END                                             AS velocity_tag
FROM products p
JOIN inventory i ON p.product_id = i.product_id
JOIN orders o    ON p.product_id = o.product_id
GROUP BY p.category
ORDER BY turnover_ratio DESC;


-- ============================================================
-- SECTION 3: SHIPMENT DELAY ANALYSIS
-- Breaks down delays by carrier, supplier, and time period
-- to identify patterns and root causes.
-- ============================================================

-- 3A. Carrier Performance Leaderboard
SELECT
    sh.carrier,
    COUNT(sh.shipment_id)                                           AS total_shipments,
    SUM(CASE WHEN sh.shipment_status = 'On Time' THEN 1 ELSE 0 END) AS on_time,
    SUM(CASE WHEN sh.shipment_status = 'Delayed'  THEN 1 ELSE 0 END) AS delayed_count,
    SUM(CASE WHEN sh.shipment_status = 'Early'    THEN 1 ELSE 0 END) AS early,
    ROUND(AVG(sh.delay_days), 2)                                    AS avg_delay_days,
    MAX(sh.delay_days)                                              AS worst_delay_days,
    ROUND(
        SUM(CASE WHEN sh.shipment_status = 'On Time' THEN 1 ELSE 0 END)
        / COUNT(sh.shipment_id) * 100, 1
    )                                                               AS reliability_pct,
    RANK() OVER (ORDER BY
        SUM(CASE WHEN sh.shipment_status = 'On Time' THEN 1 ELSE 0 END)
        / COUNT(sh.shipment_id) DESC
    )                                                               AS reliability_rank
FROM shipments sh
GROUP BY sh.carrier
ORDER BY reliability_rank;


-- 3B. Monthly Delay Trend (Last 24 Months)
-- Spot seasonal patterns in shipping delays
SELECT
    DATE_FORMAT(sh.actual_delivery, '%Y-%m')        AS month,
    COUNT(sh.shipment_id)                           AS total_shipments,
    ROUND(AVG(sh.delay_days), 2)                    AS avg_delay_days,
    SUM(CASE WHEN sh.shipment_status = 'Delayed' THEN 1 ELSE 0 END) AS delayed_count,
    ROUND(
        SUM(CASE WHEN sh.shipment_status = 'Delayed' THEN 1 ELSE 0 END)
        / COUNT(sh.shipment_id) * 100, 1
    )                                               AS delay_rate_pct
FROM shipments sh
WHERE sh.actual_delivery >= DATE_SUB(CURDATE(), INTERVAL 24 MONTH)
GROUP BY DATE_FORMAT(sh.actual_delivery, '%Y-%m')
ORDER BY month ASC;


-- 3C. Delay Cost Impact Estimate
-- Estimates financial impact of delays based on order value
SELECT
    sh.carrier,
    COUNT(CASE WHEN sh.shipment_status = 'Delayed' THEN 1 END)     AS delayed_shipments,
    ROUND(AVG(sh.delay_days), 1)                                    AS avg_delay_days,
    ROUND(SUM(o.quantity_ordered * p.unit_price), 2)                AS total_order_value_usd,
    ROUND(
        SUM(CASE WHEN sh.shipment_status = 'Delayed'
            THEN o.quantity_ordered * p.unit_price ELSE 0 END), 2
    )                                                               AS delayed_order_value_usd,
    ROUND(
        SUM(CASE WHEN sh.shipment_status = 'Delayed'
            THEN o.quantity_ordered * p.unit_price ELSE 0 END)
        / NULLIF(SUM(o.quantity_ordered * p.unit_price), 0) * 100, 1
    )                                                               AS pct_value_at_risk
FROM shipments sh
JOIN orders o  ON sh.order_id   = o.order_id
JOIN products p ON o.product_id = p.product_id
GROUP BY sh.carrier
ORDER BY delayed_order_value_usd DESC;


-- ============================================================
-- SECTION 4: ORDER TRENDS & REVENUE ANALYSIS
-- Monthly and category-level revenue trends to support
-- demand planning and business strategy decisions.
-- ============================================================

-- 4A. Monthly Order Volume & Revenue Trend
SELECT
    DATE_FORMAT(o.order_date, '%Y-%m')              AS month,
    COUNT(o.order_id)                               AS total_orders,
    SUM(o.quantity_ordered)                         AS total_units,
    ROUND(SUM(o.quantity_ordered * p.unit_price), 2) AS gross_revenue_usd,
    ROUND(AVG(o.quantity_ordered * p.unit_price), 2) AS avg_order_value_usd,
    SUM(CASE WHEN o.status = 'Delivered'  THEN 1 ELSE 0 END) AS delivered,
    SUM(CASE WHEN o.status = 'Cancelled'  THEN 1 ELSE 0 END) AS cancelled,
    SUM(CASE WHEN o.status = 'In Transit' THEN 1 ELSE 0 END) AS in_transit,
    SUM(CASE WHEN o.status = 'Pending'    THEN 1 ELSE 0 END) AS pending
FROM orders o
JOIN products p ON o.product_id = p.product_id
GROUP BY DATE_FORMAT(o.order_date, '%Y-%m')
ORDER BY month ASC;


-- 4B. Revenue by Product Category
SELECT
    p.category,
    COUNT(o.order_id)                                AS total_orders,
    SUM(o.quantity_ordered)                          AS total_units_sold,
    ROUND(SUM(o.quantity_ordered * p.unit_price), 2) AS total_revenue_usd,
    ROUND(AVG(o.quantity_ordered * p.unit_price), 2) AS avg_order_value_usd,
    ROUND(
        SUM(o.quantity_ordered * p.unit_price)
        / SUM(SUM(o.quantity_ordered * p.unit_price)) OVER () * 100, 1
    )                                                AS revenue_share_pct,
    RANK() OVER (ORDER BY SUM(o.quantity_ordered * p.unit_price) DESC) AS revenue_rank
FROM orders o
JOIN products p ON o.product_id = p.product_id
WHERE o.status != 'Cancelled'
GROUP BY p.category
ORDER BY revenue_rank;


-- 4C. Month-over-Month Revenue Growth
WITH monthly_revenue AS (
    SELECT
        DATE_FORMAT(o.order_date, '%Y-%m')               AS month,
        ROUND(SUM(o.quantity_ordered * p.unit_price), 2) AS revenue
    FROM orders o
    JOIN products p ON o.product_id = p.product_id
    WHERE o.status != 'Cancelled'
    GROUP BY DATE_FORMAT(o.order_date, '%Y-%m')
)
SELECT
    month,
    revenue,
    LAG(revenue) OVER (ORDER BY month)                   AS prev_month_revenue,
    ROUND(
        (revenue - LAG(revenue) OVER (ORDER BY month))
        / NULLIF(LAG(revenue) OVER (ORDER BY month), 0) * 100, 1
    )                                                    AS mom_growth_pct,
    CASE
        WHEN (revenue - LAG(revenue) OVER (ORDER BY month))
             / NULLIF(LAG(revenue) OVER (ORDER BY month), 0) * 100 > 5  THEN '📈 GROWING'
        WHEN (revenue - LAG(revenue) OVER (ORDER BY month))
             / NULLIF(LAG(revenue) OVER (ORDER BY month), 0) * 100 < -5 THEN '📉 DECLINING'
        ELSE '➡️  STABLE'
    END                                                  AS trend
FROM monthly_revenue
ORDER BY month ASC;


-- 4D. Top 10 Highest Value Products
SELECT
    p.product_name,
    p.category,
    p.unit_price,
    COUNT(o.order_id)                                AS times_ordered,
    SUM(o.quantity_ordered)                          AS total_units_sold,
    ROUND(SUM(o.quantity_ordered * p.unit_price), 2) AS total_revenue_usd
FROM products p
JOIN orders o ON p.product_id = o.product_id
WHERE o.status != 'Cancelled'
GROUP BY p.product_id, p.product_name, p.category, p.unit_price
ORDER BY total_revenue_usd DESC
LIMIT 10;


-- ============================================================
-- SECTION 5: EXECUTIVE SUMMARY KPIs
-- Single-query snapshot of the entire supply chain health.
-- Perfect for a Power BI card visual or C-suite report.
-- ============================================================

SELECT
    -- Order KPIs
    COUNT(DISTINCT o.order_id)                                      AS total_orders,
    ROUND(SUM(o.quantity_ordered * p.unit_price), 2)                AS total_gross_revenue_usd,
    ROUND(AVG(o.quantity_ordered * p.unit_price), 2)                AS avg_order_value_usd,
    SUM(CASE WHEN o.status = 'Cancelled' THEN 1 ELSE 0 END)         AS cancelled_orders,
    ROUND(SUM(CASE WHEN o.status = 'Cancelled' THEN 1 ELSE 0 END)
          / COUNT(o.order_id) * 100, 1)                             AS cancellation_rate_pct,

    -- Supplier KPIs
    COUNT(DISTINCT s.supplier_id)                                   AS active_suppliers,
    ROUND(AVG(s.rating), 2)                                         AS avg_supplier_rating,

    -- Shipment KPIs
    COUNT(DISTINCT sh.shipment_id)                                  AS total_shipments,
    ROUND(AVG(sh.delay_days), 2)                                    AS avg_delay_days,
    ROUND(
        SUM(CASE WHEN sh.shipment_status = 'On Time' THEN 1 ELSE 0 END)
        / NULLIF(COUNT(sh.shipment_id), 0) * 100, 1
    )                                                               AS overall_on_time_pct,

    -- Inventory KPIs
    COUNT(DISTINCT CASE WHEN i.quantity_in_stock = 0
          THEN i.inventory_id END)                                  AS out_of_stock_items,
    COUNT(DISTINCT CASE WHEN i.quantity_in_stock <= p.reorder_level
          THEN i.inventory_id END)                                  AS items_needing_reorder,
    ROUND(SUM(i.quantity_in_stock * p.unit_price), 2)               AS total_inventory_value_usd

FROM orders o
JOIN products p   ON o.product_id  = p.product_id
JOIN suppliers s  ON o.supplier_id = s.supplier_id
JOIN shipments sh ON o.order_id    = sh.order_id
JOIN inventory i  ON p.product_id  = i.product_id;


-- ============================================================
-- SECTION 6: ADVANCED WINDOW FUNCTION ANALYTICS
-- These queries demonstrate senior-level SQL skills using
-- CTEs, window functions, and complex aggregations.
-- ============================================================

-- 6A. Running Total Revenue (Cumulative Growth)
SELECT
    DATE_FORMAT(o.order_date, '%Y-%m')               AS month,
    ROUND(SUM(o.quantity_ordered * p.unit_price), 2) AS monthly_revenue,
    ROUND(SUM(SUM(o.quantity_ordered * p.unit_price))
          OVER (ORDER BY DATE_FORMAT(o.order_date, '%Y-%m')), 2) AS cumulative_revenue
FROM orders o
JOIN products p ON o.product_id = p.product_id
WHERE o.status != 'Cancelled'
GROUP BY DATE_FORMAT(o.order_date, '%Y-%m')
ORDER BY month;


-- 6B. Supplier Country Performance Comparison
SELECT
    s.country,
    COUNT(DISTINCT s.supplier_id)                    AS supplier_count,
    COUNT(o.order_id)                                AS total_orders,
    ROUND(AVG(sh.delay_days), 2)                     AS avg_delay_days,
    ROUND(AVG(s.rating), 2)                          AS avg_supplier_rating,
    ROUND(
        SUM(CASE WHEN sh.shipment_status = 'On Time' THEN 1 ELSE 0 END)
        / NULLIF(COUNT(sh.shipment_id), 0) * 100, 1
    )                                                AS on_time_rate_pct,
    RANK() OVER (ORDER BY
        SUM(CASE WHEN sh.shipment_status = 'On Time' THEN 1 ELSE 0 END)
        / NULLIF(COUNT(sh.shipment_id), 0) DESC
    )                                                AS country_rank
FROM suppliers s
JOIN orders o     ON s.supplier_id = o.supplier_id
JOIN shipments sh ON o.order_id    = sh.order_id
GROUP BY s.country
ORDER BY country_rank;


-- 6C. Product Reorder Priority Queue
-- Ranks which products to reorder first based on
-- stock level, turnover rate, and unit value
WITH product_metrics AS (
    SELECT
        p.product_id,
        p.product_name,
        p.category,
        p.unit_price,
        p.reorder_level,
        i.quantity_in_stock,
        i.warehouse_location,
        s.supplier_name,
        s.lead_time_days,
        COUNT(o.order_id)       AS order_frequency,
        SUM(o.quantity_ordered) AS total_demanded
    FROM products p
    JOIN inventory i ON p.product_id  = i.product_id
    JOIN suppliers s ON p.supplier_id = s.supplier_id
    LEFT JOIN orders o ON p.product_id = o.product_id
    GROUP BY p.product_id, p.product_name, p.category, p.unit_price,
             p.reorder_level, i.quantity_in_stock, i.warehouse_location,
             s.supplier_name, s.lead_time_days
)
SELECT
    product_name,
    category,
    warehouse_location,
    supplier_name,
    lead_time_days,
    quantity_in_stock,
    reorder_level,
    reorder_level - quantity_in_stock                AS units_short,
    unit_price,
    ROUND((reorder_level - quantity_in_stock) * unit_price, 2) AS reorder_cost_usd,
    order_frequency,
    RANK() OVER (ORDER BY
        (reorder_level - quantity_in_stock) * unit_price DESC
    )                                                AS reorder_priority_rank
FROM product_metrics
WHERE quantity_in_stock < reorder_level
ORDER BY reorder_priority_rank
LIMIT 20;


-- ============================================================
-- END OF ANALYTICS QUERIES
-- Total Queries  : 18
-- Techniques Used: JOINs, CTEs, Window Functions (RANK, LAG,
--                  SUM OVER), CASE WHEN, Subqueries,
--                  Date Functions, Aggregations
-- ============================================================