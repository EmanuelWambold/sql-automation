INSERT INTO customers (name, city) VALUES
('Max Mustermann', 'Karlsruhe'),
('Emanuel Wambold', 'Woerth am Rhein'),
('Fremder Kunde', 'Geheimstadt');

INSERT INTO orders (customer_id, amount, order_date) VALUES
(1, 299.99, '2026-01-26'),
(1, 450.00, '2026-01-25'),
(2, 0.50, '2025-12-31'),
(3, 1250.75, '2028-01-20');
