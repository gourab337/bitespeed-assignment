import sqlite3
from datetime import datetime
from datetime import timedelta


def find_oldest_order_id(id_to_update):
    future = datetime.now() + timedelta(days=3000)
    max_order_id = 0
    # Finding oldest order
    for order in id_to_update:
        if datetime.strptime(order[1], "%m/%d/%Y, %H:%M:%S") < future:
            future = datetime.strptime(order[1], "%m/%d/%Y, %H:%M:%S")
            max_order_id = order[0]
    return max_order_id


def update_records():
    try:
        conn = sqlite3.connect('fluxkart.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Contact")
        rows = cursor.fetchall()
        column_names = [description[0] for description in cursor.description]
        cursor.close()

        # If inserted record is secondary then only perform update, else skip
        id_to_update_with_datetime = []
        id_list = []
        if rows[len(rows)-1][4] == "secondary":
            # Fetch list of primary linkPrecedence
            for row in rows:
                if row[4] == "primary":
                    # If email or phoneNumber of new record is equal to an existing primary record
                    if row[1] == rows[len(rows)-1][1] or row[2] == rows[len(rows)-1][2]:
                        # Since order id is the primary key
                        id_to_update_with_datetime.append((row[0], row[5]))
                        id_list.append(row[0])

            # print(id_to_update_with_datetime)

            order_id = find_oldest_order_id(id_to_update_with_datetime)
            print("Oldest order: ", order_id, type(order_id))
            # Update
            print(id_list)
            for row in rows:
                if row[0] in id_list:
                    # updating only the records that are not the oldest record as secondary and setting it's
                    # linkPrecedence as id of the oldest order
                    if row[0] != order_id:
                        resp, err = commit_update_to_db(order_id, "secondary", row[0])
                        print(resp, err)
                        if err is not None:
                            return None, err
                        return resp, None
        return "ok", None
    except sqlite3.Error as err:
        return None, err
    finally:
        if conn:
            conn.close()


def commit_update_to_db(linked_id, link_precedence, order_id):
    try:
        conn = sqlite3.connect('fluxkart.db')
        cursor = conn.cursor()
        # Select all rows from the table
        query = '''UPDATE Contact SET linkedId = (?), linkPrecedence = (?) WHERE id = (?)'''
        print(query)
        cursor.execute(query, (linked_id, link_precedence, order_id))
        # Close the cursor and the connection
        conn.commit()
        cursor.close()
        return "ok", None
    except sqlite3.Error as err:
        return None, err
    finally:
        if conn:
            conn.close()
