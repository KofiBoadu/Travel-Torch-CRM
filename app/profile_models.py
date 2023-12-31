from .models import create_databaseConnection




def profile_details(customer_id):
    query = """
        SELECT
          CONCAT(c.first_name, ' ', c.last_name) AS customer_name,
          c.email_address,
          c.phone_number,
          c.state_address,
          GROUP_CONCAT(CONCAT(t.tour_name, ' ', YEAR(t.start_date)) SEPARATOR ', ') AS tours,
          SUM(t.tour_price) AS total_price
        FROM
          customers c
        JOIN
          tour_bookings tb ON c.customer_id = tb.customer_id
        JOIN
          tours t ON tb.tour_id = t.tour_id
        WHERE
          c.customer_id = %s
        GROUP BY
          c.customer_id;
    """
    database_connection = None
    cursor = None
    try:
        database_connection = create_databaseConnection()
        cursor = database_connection.cursor()
        cursor.execute(query, (customer_id,))
        results = cursor.fetchall()
        return results[0] if results else None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
    finally:
        if cursor is not None:
            cursor.close()
        if database_connection is not None:
            database_connection.close()




