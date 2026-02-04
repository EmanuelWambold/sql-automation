from src.connection import get_connection
from src.repository import (
    reset_demo,
    add_order,
    insert_new_customer_with_first_order,
    customer_revenue_report,
    city_revenue_report_filtered,
    status_report,
    revenue_between_report
)
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
    (3, 1250.75, 'pending', '2028-01-20'),
    (4, 75.75, 'arrived', '2026-01-30')
]

NEW_ORDER_CUSTOMER_ID = 1
START_DATE_REVENUE = "2025-12-01"
END_DATE_REVENUE = "2026-01-25"



# --- Demo execution: ---
if __name__ == "__main__":

    # Connection to database as 'atruvia_user' (superuser)
    conn = get_connection()

    print("""
--------------------------------------------------
ATRUVIA DEMO - PostgreSQL + Python automation
--------------------------------------------------
    \n""")

    # 0. Reset the demo
    reset_demo(conn, DEMO_CUSTOMERS, DEMO_ORDERS) 

    # 1. Automation: NEW ORDER
    new_id = add_order(conn, customer_id=NEW_ORDER_CUSTOMER_ID, amount=round(randomFloat(1, 100), 2))
    first_name, middle_name, last_name, city = DEMO_CUSTOMERS[NEW_ORDER_CUSTOMER_ID - 1]
    full_name = " ".join([x for x in (first_name, middle_name, last_name) if x]) # remove possible "None" for "middle_name"
    print(f"NEW ORDER: ID {new_id} for {full_name}")

    # 2. Automation: NEW CUSTOMER WITH ORDER
    new_customer_id, new_order_id = insert_new_customer_with_first_order(conn, "Neuer", "Kunde", 99.99)
    print(f"NEW ORDER: ID {new_order_id} for the newly created customer with ID {new_customer_id}")

    # 3. Evaluation: CUSTOMER SALES REPORT
    print("\nCUSTOMER SALES REPORT:")
    customer_report = customer_revenue_report(conn)
    for row in customer_report:
        print(f"   {row['name']} ({row['city']}): {row['orders']} order(s), {row['revenue']}€")

    # 4. Evaluation: CITY SALES REPORT
    print("\nCITY SALES REPORT - only 'shipped' and 'arrived' orders included:")
    city_revenue = city_revenue_report_filtered(conn)
    for row in city_revenue:
        print(f"   {row['city']}: {row['city_orders']} order(s), {row['city_revenue']}€")

    # 5. Evaluation: STATUS SALES REPORT
    print("\nSTATUS SALES REPORT:")
    status_data = status_report(conn)
    for row in status_data:
        print(f"   {row['status']}: {row['status_orders']} order(s), {row['status_revenue']}€")
    
    # 6. Evaluation: REVENUE BETWEEN DATES
    print(f"\nREVENUE BETWEEN {START_DATE_REVENUE} AND {END_DATE_REVENUE}:")
    dates_revenue = revenue_between_report(conn, START_DATE_REVENUE, END_DATE_REVENUE)
    print(f"   Total revenue: {dates_revenue}€")


    conn.close()
    
    print("""\n
--------------------------------------------------
Demo completed
--------------------------------------------------
        """)