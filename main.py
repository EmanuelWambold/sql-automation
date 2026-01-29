import psycopg2
from psycopg2.extras import RealDictCursor
from random import uniform as randomFloat



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
    (3, 1250.75, 'pending', '2028-01-20') 
]

NEW_ORDER_CUSTOMER_ID = 1



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

def reset_demo():
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
        customer_id (int): customer ID for the new added order
        amount (float): amount for the new added order
        
    Returns:
        the order ID (int) for the new added order
    
    Raises:
        ValueError: if the amount is not positive
        psycopg2.Error: if database operation fails
    """
    
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



def customer_revenue_report() -> list[dict]:
    """
    This method calculates the sales for each individual customer and sorts them in descending order.
    
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
                    SELECT 
                        c.first_name || ' ' || COALESCE(c.middle_name || ' ', '') || c.last_name AS name,
                        COALESCE(c.city, 'Unbekannt') AS city,
                        COUNT(o.id) AS orders,
                        COALESCE(SUM(o.amount), 0) AS revenue
                    FROM customers c LEFT JOIN orders o ON c.id = o.customer_id 
                    GROUP BY c.id, c.last_name, c.first_name, c.middle_name, COALESCE(c.city, 'Unbekannt')
                    ORDER BY revenue DESC;
                    """
                )
                return cur.fetchall()

    except Exception as e:
        print(f"Failed to create the report revenue: {e}")
        raise



def city_revenue_report() -> list[dict]:
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



#  Demo execution:
if __name__ == "__main__":
    
    # 0. Reset the demo
    reset_demo() 

    # 1. Automation: NEW ORDER
    new_id = add_order(customer_id=NEW_ORDER_CUSTOMER_ID, amount=round(randomFloat(1, 100), 2))
    first_name, middle_name, last_name, city = DEMO_CUSTOMERS[NEW_ORDER_CUSTOMER_ID - 1]
    full_name = " ".join([x for x in (first_name, middle_name, last_name) if x]) # remove possible "None" for "middle_name"
    print(f"NEW ORDER: ID {new_id} for {full_name}")

    # 2. Evaluation: CUSTOMER SALES REPORT
    print("\nCUSTOMER SALES REPORT:")
    customer_report = customer_revenue_report()
    for row in customer_report:
        print(f"   {row['name']} ({row['city']}): {row['orders']} order(s), {row['revenue']}€")

    # 3. Evaluation: CITY SALES REPORT
    print("\nCITY SALES REPORT:")
    city_revenue = city_revenue_report()
    for row in city_revenue:
        print(f"   {row['city']}: {row['city_orders']} order(s), {row['city_revenue']}€")

    # 4. Evaluation: STATUS SALES REPORT
    print("\nSTATUS SALES REPORT:")
    status_data = status_report()
    for row in status_data:
        print(f"  {row['status']}: {row['status_orders']} order(s), {row['status_revenue']}€")

    conn.close()
    
    print("""\n
--------------------------------------------------
Demo completed
--------------------------------------------------
        """)