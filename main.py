import psycopg2
from psycopg2.extras import RealDictCursor
from typing import Any
from random import uniform as randomFloat
from datetime import datetime



# Constants:
DEMO_CUSTOMERS = [
    ('Max', None, 'Mustermann', 'Karlsruhe'),
    ('Emanuel', None, 'Wambold', 'Woerth am Rhein'),
    ('Fremder', 'Unbekannter', 'Kunde', 'Geheimstadt'),
    ('Keine', None, 'Stadt', None)
]

DEMO_ORDERS = [
    (1, 299.99, 'cancelled', '2026-01-26'),
    (1, 450.00, 'arrived', '2026-01-25'),
    (2, 0.50, 'shipped', '2025-12-31'),
    (3, 1250.75, 'pending', '2028-01-20'),
    (4, 75.75, 'arrived', '2026-01-30')
]

NEW_ORDER_CUSTOMER_ID = 1
START_DATE_REVENUE = "2025-12-01"
END_DATE_REVENUE = "2026-01-25"



print("""
--------------------------------------------------
ATRUVIA DEMO - PostgreSQL + Python automation
--------------------------------------------------
\n""")

# Connection to database as 'atruvia_user' (superuser)
conn = psycopg2.connect(
    dbname="atruvia_demo",
    user="atruvia_user",
    password="atruvia2026",
    host="localhost",
    port=5432
)

def reset_demo() -> None:
    """
    This method resets the database to its designed structure and inserts the demo data.
    
    Returns:
        None
    
    Raises:
        psycopg2.Error: if database operation fails
    """
    
    try:
        with conn: # Auto commit/rollback ensures transaction safety
            with conn.cursor() as cur:
                
                # Delete current data and reset IDs
                cur.execute("TRUNCATE TABLE orders, customers RESTART IDENTITY CASCADE;")
                
                # Add demo customers
                for first_name, middle_name, last_name, city in DEMO_CUSTOMERS:
                    cur.execute(
                        """
                        INSERT INTO customers (first_name, middle_name, last_name, city)
                        VALUES (%s, %s, %s, %s);
                        """,
                        (first_name, middle_name, last_name, city)
                    )
                
                # Add demo orders
                for customer_id, amount, status, order_date in DEMO_ORDERS:
                    cur.execute(
                        """
                        INSERT INTO orders (customer_id, amount, status, order_date)
                        VALUES (%s, %s, %s, %s);
                        """,
                        (customer_id, amount, status, order_date)
                    )
                
        print(f"Demo data has been reset for ({len(DEMO_CUSTOMERS)} customers, {len(DEMO_ORDERS)} orders)\n")
        
    except Exception as e:
        print(f"Failed to reset the demo database to its designed structure: {e}")
        raise



def add_order(customer_id: int, amount: float) -> int:
    """
    This method automatically adds new orders.
        
    Args:
        - customer_id (int): customer ID for the new added order
        - amount (float): amount for the new added order
        
    Returns:
        the order ID (int) for the new added order
    
    Raises:
        - TypeError: if a parameter does not match the expected type
        - ValueError: if the amount is not positive
        - psycopg2.Error: if database operation fails
    """
    
    # Validate parameters
    validate_param_type("customer_id", customer_id, int)
    validate_param_type("amount", amount, (float, int))
    if amount < 0:
        raise ValueError(f"Amount of order must be positive, got {amount} instead")
    
    try:
        with conn: # Auto commit/rollback ensures transaction safety
            with conn.cursor() as cur:
                
                # Add the new order into the 'orders' table
                cur.execute(
                    """
                    INSERT INTO orders (customer_id, amount, status)
                    VALUES (%s, %s, DEFAULT) RETURNING id;
                    """, 
                    (customer_id, amount) # status defaults to 'pending'
                )
                
                return cur.fetchone()[0] # returns the new order ID
    
    except Exception as e:
        print(f"Failed to add new order for customer {customer_id} with amount {amount}: {e}")
        raise



def insert_new_customer_with_first_order(
    first_name: str,
    last_name: str,
    amount: float,
    *,
    middle_name: str | None = None,
    city: str | None = None,
) -> tuple[int, int]:
    
    """
    This method creates a new customer and a first order in single transaction.
    
    Args:
        - first_name: Customer first name
        - last_name: Customer last name
        - amount: First order amount
        - middle_name: Optional middle name
        - city: Optional city
  
    Returns:
        tuple[int, int]: (customer_id, order_id) of newly created entities
  
    Raises:
        - ValueError: if the amount is not positive
        - psycopg2.Error: if database operation fails
    """

    # Validate parameters
    validate_param_type("first_name", first_name, str)
    validate_param_type("last_name", last_name, str)
    validate_param_type("amount", amount, (int, float))
    if amount < 0:
        raise ValueError(f"Amount of order must be positive, got {amount} instead")
    validate_param_type("middle_name", middle_name, str, can_be_null=True)
    validate_param_type("city", city, str, can_be_null=True)
    
    try:
        with conn: # Auto commit/rollback ensures transaction safety
            with conn.cursor() as cur:
                
                # 1. Insert new customer and get its ID
                cur.execute(
                    """
                    INSERT INTO customers (first_name, middle_name, last_name, city)
                    VALUES (%s, %s, %s, %s)
                    RETURNING id
                    """, 
                    (first_name, middle_name, last_name, city)
                )
                customer_id = cur.fetchone()[0]
                
        # 2. Insert first order with SAME customer_id
        order_id = add_order(customer_id, amount)
                
        return customer_id, order_id
        
    except Exception as e:
        print(f"Failed to create customer and order transaction: {e}")
        raise



def customer_revenue_report() -> list[dict]:
    """
    This method calculates the sales for each individual customer and sorts them in descending order,
    using the SQL-view 'customer_revenue_view'.
    
    Returns:
        list[dict]: List of customer reports as Dict objects:
            - name (str): Customer name
            - city (str): City of the customer  
            - orders (int): Amount of orders by the customer
            - revenue (float): Total sales in euros
    
    Raises:
        psycopg2.Error: if database operation fails
    """
    
    try:
        with conn: # Auto commit/rollback ensures transaction safety
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    """
                    SELECT name, city, orders, revenue
                    FROM customer_revenue_view
                    ORDER BY revenue DESC;
                    """
                )
                return cur.fetchall()

    except Exception as e:
        print(f"Failed to create the report revenue: {e}")
        raise



def city_revenue_report_filtered() -> list[dict]:
    """
    This method calculates total orders and revenue per city, including all cities, counting only 
    orders not marked as 'pending' or 'cancelled'. Results are sorted by revenue descending.

    Returns:
        list[dict]: List of city reports as Dict objects:
            - city (str): Name of the city ('Unbekannt' if city is NULL)
            - city_orders (int): Number of completed orders in the city
            - city_revenue (float): Total revenue from completed orders in euros
    
    Raises:
        psycopg2.Error: if database operation fails
    """

    try:
        with conn: # Auto commit/rollback ensures transaction safety
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    """
                    SELECT
                        COALESCE(c.city, 'Unbekannt') AS city,
                        COUNT(
                            CASE 
                                WHEN o.status NOT IN ('pending', 'cancelled') 
                                THEN o.id
                                -- if CASE doesn't match -> returns NULL -> COUNT ignores
                            END
                        ) AS city_orders,
                        COALESCE(
                            SUM(
                                CASE 
                                    WHEN o.status NOT IN ('pending', 'cancelled') 
                                    THEN o.amount
                                    -- if CASE doesn't match -> returns NULL -> SUM ignores 
                                END
                            ), 0) 
                        AS city_revenue
                    FROM customers c LEFT JOIN orders o ON c.id = o.customer_id
                    GROUP BY COALESCE(c.city, 'Unbekannt')
                    ORDER BY city_revenue DESC;
                    """
                )
                return cur.fetchall()

    except Exception as e:
        print(f"Failed to create the city revenue: {e}")
        raise



def status_report() -> list[dict]:
    """
    This method calculates orders and revenue per order status.
    
    Returns:
        list[dict]: List of status reports as Dict objects:
            - status (str): Order name for each status
            - status_revenue (float): Total revenue for each status
            - status_orders (int): Number of orders for each status
        
    Raises:
        psycopg2.Error: if database operation fails
    """
    
    try:
        with conn: # Auto commit/rollback ensures transaction safety
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    """
                    SELECT
                        o.status,
                        COALESCE(SUM(o.amount), 0) AS status_revenue,
                        COUNT(o.id) AS status_orders   
                    FROM orders o
                    GROUP BY o.status
                    ORDER BY status_revenue DESC;
                    """
                )
                return cur.fetchall()
            
    except Exception as e:
        print(f"Failed to create the status report: {e}")
        raise



def revenue_between_report(start_date: str, end_date: str) -> float:
    """
    This method calculates the total revenue for orders between two dates (inclusively).
    Expects dates in 'YYYY-MM-DD' format!
    
    Args:
        start_date (str): Start date in 'YYYY-MM-DD' format  
        end_date (str): End date in 'YYYY-MM-DD' format
        
    Returns:
        float: Total revenue within the date range
        
    Raises:
        ValueError: If date format is invalid or start_date > end_date
        psycopg2.Error: if database operation fails
    """
    
    # Validate parameters
    validate_param_type("start_date", start_date, str)
    validate_param_type("end_date", end_date, str)
    
    # Validate date format 'YYYY-MM-DD'
    try:
        start_dt = datetime.strptime(start_date, '%Y-%m-%d')
        end_dt = datetime.strptime(end_date, '%Y-%m-%d')
    except ValueError:
        raise ValueError(f"Date format must be 'YYYY-MM-DD', got '{start_date}' or '{end_date}'")
    
    # Validate start_date <= end_date
    if start_dt > end_dt:
        raise ValueError(f"start_date ({start_date}) can't be after end_date ({end_date})")
    
    try:
        with conn: # Auto commit/rollback ensures transaction safety
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT COALESCE(SUM(amount), 0) AS dates_revenue
                    FROM orders 
                    WHERE order_date BETWEEN %s AND %s;
                    """,
                    (start_date, end_date)
                )

                return cur.fetchone()[0]
                
    except Exception as e:
        print(f"Failed to calculate revenue between {start_date} and {end_date}: {e}")
        raise



def validate_param_type(name: str, value: Any, expected_type: type, can_be_null: bool = False) -> None:
    """
    This method is used to validate a single parameter type and optional nullability.
    
    Args:
        - name (str): Parameter name for error reporting
        - value (Any): Value to validate
        - expected_type (type): Expected type (int, float, str, tuple of types)
        - can_be_null (bool): Allow None values (default: False)
        
    Raises:
        TypeError: If type doesn't match expected_type or nullability rules
    """
    
    if can_be_null and value is None:
        return  # None is explicitly allowed
    
    if not isinstance(value, expected_type):
        type_name = expected_type.__name__ if not isinstance(expected_type, tuple) else ', '.join(types.__name__ for types in expected_type)
        actual_type = type(value).__name__
        raise TypeError(f"{name} must be {type_name}{' or None' if can_be_null else ''}, got {actual_type} instead")




#  Demo execution:
if __name__ == "__main__":
    
    # 0. Reset the demo
    reset_demo() 

    # 1. Automation: NEW ORDER
    new_id = add_order(customer_id=NEW_ORDER_CUSTOMER_ID, amount=round(randomFloat(1, 100), 2))
    first_name, middle_name, last_name, city = DEMO_CUSTOMERS[NEW_ORDER_CUSTOMER_ID - 1]
    full_name = " ".join([x for x in (first_name, middle_name, last_name) if x]) # remove possible "None" for "middle_name"
    print(f"NEW ORDER: ID {new_id} for {full_name}")

    # 2. Automation: NEW CUSTOMER WITH ORDER
    new_customer_id, new_order_id = insert_new_customer_with_first_order("Neuer", "Kunde", 99.99)
    print(f"NEW ORDER: ID {new_order_id} for the newly created customer with ID {new_customer_id}")

    # 3. Evaluation: CUSTOMER SALES REPORT
    print("\nCUSTOMER SALES REPORT:")
    customer_report = customer_revenue_report()
    for row in customer_report:
        print(f"   {row['name']} ({row['city']}): {row['orders']} order(s), {row['revenue']}€")

    # 4. Evaluation: CITY SALES REPORT
    print("\nCITY SALES REPORT - only 'shipped' and 'arrived' orders included:")
    city_revenue = city_revenue_report_filtered()
    for row in city_revenue:
        print(f"   {row['city']}: {row['city_orders']} order(s), {row['city_revenue']}€")

    # 5. Evaluation: STATUS SALES REPORT
    print("\nSTATUS SALES REPORT:")
    status_data = status_report()
    for row in status_data:
        print(f"   {row['status']}: {row['status_orders']} order(s), {row['status_revenue']}€")
    
    # 6. Evaluation: REVENUE BETWEEN DATES
    print(f"\nREVENUE BETWEEN {START_DATE_REVENUE} AND {END_DATE_REVENUE}:")
    dates_revenue = revenue_between_report(START_DATE_REVENUE, END_DATE_REVENUE)
    print(f"   Total revenue: {dates_revenue}€")

    conn.close()
    
    print("""\n
--------------------------------------------------
Demo completed
--------------------------------------------------
        """)