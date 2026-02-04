-- Create own enum for the 'orders' table:
CREATE TYPE order_status AS ENUM (
    'pending',
    'shipped',
    'arrived',
    'cancelled'
);


-- Create tables:
CREATE TABLE customers (
    id          SERIAL PRIMARY KEY,
    first_name  VARCHAR(50)   NOT NULL,
    middle_name VARCHAR(50),
    last_name   VARCHAR(50)   NOT NULL,
    city        VARCHAR(50),
    created_at  TIMESTAMP     NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE orders (
    id          SERIAL PRIMARY KEY,
    customer_id INT           NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
    amount      NUMERIC(10,2) NOT NULL CHECK (amount >= 0),
    status      order_status  NOT NULL DEFAULT 'pending',
    order_date  DATE          NOT NULL DEFAULT CURRENT_DATE
);


-- Create index on 'order_date' for the 'orders' table:
CREATE INDEX idx_orders_order_date ON orders (order_date);


-- Create view that summarizes each customer order count and total revenue
-- while handling missing names and cities:
CREATE VIEW customer_revenue_view AS
SELECT 
    c.id,
    c.first_name || ' ' || COALESCE(c.middle_name || ' ', '') || c.last_name AS name,
    COALESCE(c.city, 'Unbekannt') AS city,
    COUNT(o.id) AS orders,
    COALESCE(SUM(o.amount), 0) AS revenue
FROM customers c LEFT JOIN orders o ON c.id = o.customer_id
GROUP BY c.id, c.last_name, c.first_name, c.middle_name, COALESCE(c.city, 'Unbekannt');