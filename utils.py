from datetime import datetime
import sqlite3
from update_db import update_records
from message_generator import message_gen


def validations(json_body):
    # Length of Json body has to be 2 since there are only 2 fields.
    if len(json_body) != 2:
        return 0
    # Type validations
    for index, field in enumerate(json_body):
        # Use field.decode() in case it breaks
        if index == 0 and field != 'email':
            return 0
        if index == 1 and field != 'phoneNumber':
            return 0
        # Use json_body[b'email'] in case the code breaks
        if field == 'email' and type(json_body['email']) != str:
            return 0
        if field == 'phoneNumber' and type(json_body['phoneNumber']) != str:
            return 0
    return 1


def store_in_db(json_body):
    # Fetch relevant fields from json body
    # Ideally order_id should have been uuid
    order_id, err = fetch_id_from_db()
    order_id += 1  # incrementing prev order id by 1 for new order
    if err is not None:
        return err
    # Use json_body[b'phoneNumber'] in case code breaks
    phone_number = json_body['phoneNumber']
    email = json_body['email']
    linked_id, err = linked_id_finder(phone_number, email)
    if err is not None:
        return err

    if linked_id is None:
        link_precedence = "primary"
    else:
        link_precedence = "secondary"
    # For new orders:
    email_list, err = fetch_email_from_db()
    phone_number_list, err = fetch_phone_number_from_db()
    if err is not None:
        print(err)
        # Right now avoiding the error case by storing the order as a new order. We can store these cases in Redis /
        # SQS and process later for system improvement
    # print(email_list, phone_number_list)
    # if (email not in email_list) and (phone_number not in phone_number_list):
    #     created_at = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
    #     updated_at = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
    # # For existing order (key - email or phone_number)
    # else:
    #     updated_at = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
    created_at = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
    updated_at = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
    # For now no delete feature is there since it's not described in the problem statement.
    deleted_at = None

    # Storing these values in database
    resp, err = db_entry_query_executor(order_id, phone_number, email, linked_id, link_precedence, created_at,
                                        updated_at,
                                        deleted_at)
    if err is not None:
        print(err)
        return err
    else:
        print(resp)
        return resp


def db_entry_query_executor(order_id, phone_number, email, linked_id, link_precedence, created_at, updated_at,
                            deleted_at):
    try:
        conn_obj = sqlite3.connect('fluxkart.db')
        cursor_obj = conn_obj.cursor()
        query = '''INSERT INTO Contact VALUES  (?, ?, ?, ?, ?, ?, 
        ?, ?)'''
        cursor_obj.execute(query, (order_id, phone_number, email, linked_id, link_precedence, created_at,
                                   updated_at, deleted_at))
        conn_obj.commit()
        cursor_obj.close()
        return "ok", None
    except sqlite3.Error as err:
        return None, err
    finally:
        if conn_obj:
            conn_obj.close()


def fetch_id_from_db():
    try:
        conn = sqlite3.connect('fluxkart.db')
        cursor = conn.cursor()
        # Select all rows from the table
        cursor.execute("SELECT * FROM Contact")
        rows = cursor.fetchall()

        # Fetch last order_id
        order_id = 0  # Default value
        for row in rows:
            order_id = row[0]
        # Close the cursor and the connection
        cursor.close()
        return order_id, None
    except sqlite3.Error as err:
        return None, err
    finally:
        if conn:
            conn.close()


def fetch_email_from_db():
    try:
        conn_obj = sqlite3.connect('fluxkart.db')
        cursor_obj = conn_obj.cursor()
        query = '''SELECT email FROM Contact'''
        cursor_obj.execute(query)
        email_list_resp = cursor_obj.fetchall()
        conn_obj.commit()
        cursor_obj.close()
        email_list = []
        for email in email_list_resp:
            email_list.append(email[0])
        return email_list, None
    except sqlite3.Error as err:
        return [], err
    finally:
        if conn_obj:
            conn_obj.close()


def fetch_phone_number_from_db():
    try:
        conn_obj = sqlite3.connect('fluxkart.db')
        cursor_obj = conn_obj.cursor()
        query = '''SELECT phoneNumber FROM Contact'''
        cursor_obj.execute(query)
        phone_number_list_resp = cursor_obj.fetchall()
        conn_obj.commit()
        cursor_obj.close()
        phone_number_list = []
        for phone in phone_number_list_resp:
            phone_number_list.append(phone[0])
        return phone_number_list, None
    except sqlite3.Error as err:
        return [], err
    finally:
        if conn_obj:
            conn_obj.close()


def linked_id_finder(phone_no, email):
    email_list, err = fetch_email_from_db()
    if err is not None:
        return None, err
    phone_list, err = fetch_phone_number_from_db()
    if err is not None:
        return None, err
    print("Email list: ", email_list)
    print("Phone list: ", phone_list)

    if phone_no in phone_list:
        print(phone_no, type(phone_no))
        try:
            conn_obj = sqlite3.connect('fluxkart.db')
            cursor_obj = conn_obj.cursor()

            query = '''SELECT linkPrecedence FROM Contact WHERE phoneNumber = "''' + phone_no + '''" LIMIT 1;'''
            print(query)
            cursor_obj.execute(query)
            link_precedence = cursor_obj.fetchall()
            print(link_precedence[0][0])
            if link_precedence[0][0] == "primary":
                query = '''SELECT id, createdAt FROM Contact WHERE phoneNumber = "''' + phone_no + '''" ORDER BY 
                createdAt ASC LIMIT 1; '''
                print(query)
            else:
                query = '''SELECT linkedId, createdAt FROM Contact WHERE phoneNumber = "''' + phone_no + '''" ORDER BY 
                createdAt ASC LIMIT 1; '''
                print(query)
            cursor_obj.execute(query)
            linked_id_phone = cursor_obj.fetchall()
            conn_obj.commit()
            cursor_obj.close()
            print(linked_id_phone)
        except sqlite3.Error as err:
            return None, err
        finally:
            if conn_obj:
                conn_obj.close()
    if email in email_list:
        print(email, type(email))
        try:
            conn_obj = sqlite3.connect('fluxkart.db')
            cursor_obj = conn_obj.cursor()

            query = '''SELECT linkPrecedence FROM Contact WHERE email = "''' + email + '''" LIMIT 1;'''
            print(query)
            cursor_obj.execute(query)
            link_precedence = cursor_obj.fetchall()
            print(link_precedence[0][0])
            if link_precedence[0][0] == "primary":
                query = '''SELECT id, createdAt FROM Contact WHERE email = "''' + email + '''" ORDER BY createdAt ASC 
                            LIMIT 1; '''
                print(query)
            else:
                query = '''SELECT linkedId, createdAt FROM Contact WHERE email = "''' + email + '''" ORDER BY 
                            createdAt ASC LIMIT 1; '''
                print(query)
            cursor_obj.execute(query)
            linked_id_email = cursor_obj.fetchall()
            conn_obj.commit()
            cursor_obj.close()
            print(linked_id_email)
        except sqlite3.Error as err:
            print(err)
            return None, err
        finally:
            if conn_obj:
                conn_obj.close()

    if (phone_no in phone_list) and (email in email_list):
        # Oldest contact remained as “primary”
        if linked_id_phone[0][1] > linked_id_email[0][1]:
            linked_id = linked_id_email[0][0]
        else:
            linked_id = linked_id_phone[0][0]
        print(linked_id)
        return linked_id, None
    elif phone_no in phone_list:
        linked_id = linked_id_phone[0][0]
        print(linked_id)
        return linked_id, None
    elif email in email_list:
        print(linked_id_email)
        linked_id = linked_id_email[0][0]
        print(linked_id)
        return linked_id, None

    return None, None


def generate_response(json_body):
    print(json_body)
    # Update records to merge duplicate contacts after adding new record
    resp, err = update_records()
    if err is not None:
        print(err)
    print(resp)
    # Prepare response message
    response = message_gen()
    return response
