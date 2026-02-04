import psycopg2
from psycopg2.extras import RealDictCursor
from typing import List, Tuple
from datetime import datetime

from src.validation import validate_param_type


# --- Main Funtions ---
def reset_demo(conn: "psycopg2.connection", demo_customers: List[Tuple], demo_orders: List[Tuple]) -> None:
    """
    This method resets the database to its designed structure and inserts the demo data.
    
    Args:
        conn (psycopg2.connection): active database connection

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
                cur.executemany(
                    """
                    INSERT INTO customers (first_name, middle_name, last_name, city)
                    VALUES (%s, %s, %s, %s);
                    """,
                    demo_customers
                )
                
                # Add demo orders
                cur.executemany(
                    """
                    INSERT INTO orders (customer_id, amount, status, order_date)
                    VALUES (%s, %s, %s, %s);
                    """,
                    demo_orders
                )
                
        print(f"Demo data has been reset for ({len(demo_customers)} customers, {len(demo_orders)} orders)\n")
        
    except psycopg2.Error as e:
        print(f"Failed to reset the demo database to its designed structure: {e}")
        raise



def add_order(conn: "psycopg2.connection", customer_id: int, amount: float) -> int:
    """
    This method automatically adds new orders.
        
    Args:
        - conn (psycopg2.connection): active database connection
        - customer_id (int): customer ID for the new added order
        - amount (float): amount for the new added order
        
    Returns:
        the order ID (int) for the new added order
    
    Raises:
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
    
    except psycopg2.Error as e:
        print(f"Failed to add new order for customer {customer_id} with amount {amount}: {e}")
        raise



def insert_new_customer_with_first_order(
    conn: "psycopg2.connection",
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
        - conn (psycopg2.connection): active database connection
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
        order_id = add_order(conn, customer_id, amount)
                
        return customer_id, order_id
        
    except psycopg2.Error as e:
        print(f"Failed to create customer and order transaction: {e}")
        raise



def customer_revenue_report(conn: "psycopg2.connection") -> list[dict]:
    """
    This method calculates the sales for each individual customer and sorts them in descending order,
    using the SQL-view 'customer_revenue_view'.
    
    Args:
        - conn (psycopg2.connection): active database connection

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

    except psycopg2.Error as e:
        print(f"Failed to create the report revenue: {e}")
        raise



def city_revenue_report_filtered(conn: "psycopg2.connection") -> list[dict]:
    """
    This method calculates total orders and revenue per city, including all cities, counting only 
    orders not marked as 'pending' or 'cancelled'. Results are sorted by revenue descending.

    Args:
        - conn (psycopg2.connection): active database connection

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

    except psycopg2.Error as e:
        print(f"Failed to create the city revenue: {e}")
        raise



def status_report(conn: "psycopg2.connection") -> list[dict]:
    """
    This method calculates orders and revenue per order status.
    
    Args:
        - conn (psycopg2.connection): active database connection

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
            
    except psycopg2.Error as e:
        print(f"Failed to create the status report: {e}")
        raise



def revenue_between_report(conn: "psycopg2.connection", start_date: str, end_date: str) -> float:
    """
    This method calculates the total revenue for orders between two dates (inclusively).
    Expects dates in 'YYYY-MM-DD' format!
    
    Args:
        - conn (psycopg2.connection): active database connection
        - start_date (str): Start date in 'YYYY-MM-DD' format  
        - end_date (str): End date in 'YYYY-MM-DD' format
        
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
                
    except psycopg2.Error as e:
        print(f"Failed to calculate revenue between {start_date} and {end_date}: {e}")
        raise