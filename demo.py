import psycopg2
from psycopg2.extras import RealDictCursor
from random import uniform as randomFloat


# Constants:
DEMO_CUSTOMERS = [
    ('Max Mustermann', 'Karlsruhe'),
    ('Emanuel Wambold', 'Woerth am Rhein'),
    ('Fremder Kunde', 'Geheimstadt')
]

DEMO_ORDERS = [
    (1, 299.99, '2026-01-26'),
    (1, 450.00, '2026-01-25'),
    (2, 0.50, '2025-12-31'),
    (3, 1250.75, '2028-01-20')
]

NEW_ORDER_CUSTOMER_ID = 1



print("""
--------------------------------------------------
ATRUVIA DEMO – PostgreSQL + Python automation
--------------------------------------------------
""")

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
    This method resets the database to its designed structure.
    
    Returns:
        None
    """
    
    with conn.cursor() as cur:
        
        # Delete current data
        cur.execute("TRUNCATE TABLE orders, customers RESTART IDENTITY CASCADE")
        
        # Add customers
        for name, city in DEMO_CUSTOMERS:
            cur.execute("INSERT INTO customers (name, city) VALUES (%s, %s)", (name, city))
        
        # Add orders
        for customer_id, amount, order_date in DEMO_ORDERS:
            cur.execute("INSERT INTO orders (customer_id, amount, order_date) VALUES (%s, %s, %s)",
                        (customer_id, amount, order_date))
        
        conn.commit()
    print(f"Demo data has been reset for ({len(DEMO_CUSTOMERS)} customers, {len(DEMO_ORDERS)} orders)\n")




def add_order(customer_id, amount):
    """
    This method automatically adds new orders.
        
    Args:
        customer_id (int): the new added customer id
        amount (float): the new added amount for the customer id
        
    Returns:
        the order ID (int) for the new added order
    """
    
    with conn.cursor() as cur:
        
        # Add the new order into the 'orders' table
        cur.execute("INSERT INTO orders (customer_id, amount) VALUES (%s, %s) RETURNING id", 
                    (customer_id, amount))
        
        # Get the new order ID
        order_id = cur.fetchone()[0]
        conn.commit()
        return order_id


def revenue_report():
    """
    This method calculates the sales for each individual customer and sorts them in descending order
    
    Returns:
        list[dict]: List of customer reports as Dict objects:
            - name (str): customer name
            - city (str): city of the customer  
            - orders (int): amount of orders by the customer
            - revenue (float): Total sales in euros
    """
    
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("""
            SELECT c.name, c.city, 
                   COUNT(o.id) as orders, 
                   SUM(o.amount) as revenue
            FROM customers c LEFT JOIN orders o ON c.id = o.customer_id 
            GROUP BY c.id, c.name, c.city
            ORDER BY revenue DESC
        """)
        return cur.fetchall()



#  Demo execution:
if __name__ == "__main__":
    try:
    
        reset_demo() 
    
        # 1. Automation: NEW ORDER
        new_id = add_order(customer_id=NEW_ORDER_CUSTOMER_ID, amount=randomFloat(1, 100))
        print(f"NEW ORDER: ID {new_id} for {DEMO_CUSTOMERS[NEW_ORDER_CUSTOMER_ID - 1][0]}")
    
        # 2. Evaluation: SALES REPORT
        print("\nSALES REPORT:")
        report = revenue_report()
        for row in report:
            print(f"   {row['name']} ({row['city']}): {row['orders']} order(s), €{row['revenue']:.2f}")
    
        conn.close()
        print("""\n
--------------------------------------------------
Demo completed
--------------------------------------------------
            """)
        
    except Exception as e:
        print("\n An error has occurred:")
        print(e)