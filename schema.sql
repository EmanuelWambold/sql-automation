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