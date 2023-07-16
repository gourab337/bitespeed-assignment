import sqlite3


def message_gen():
    conn = sqlite3.connect('fluxkart.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Contact")
    rows = cursor.fetchall()

    if rows[len(rows) - 1][4] == "secondary":
        # Primary contact Id is linkPrecedence
        primary_contact_id = rows[len(rows) - 1][3]
    else:
        # Primary contact Id is order Id
        primary_contact_id = rows[len(rows) - 1][0]

    cursor.execute("SELECT email FROM Contact WHERE linkedId = (?) OR id = (?)", (primary_contact_id, primary_contact_id))
    response = cursor.fetchall()
    response = [*set(response)]
    email_list = []
    for email in response:
        email_list.append(email[0])

    cursor.execute("SELECT phoneNumber FROM Contact WHERE linkedId = (?) OR id = (?)",
                   (primary_contact_id, primary_contact_id))
    response = cursor.fetchall()
    response = [*set(response)]
    phone_list = []
    for phone in response:
        phone_list.append(phone[0])

    cursor.execute(
        "SELECT id FROM Contact WHERE linkedId = (?) AND id != (?)", (primary_contact_id, rows[len(rows) - 1][0]))
    response = cursor.fetchall()
    response = [*set(response)]
    secondary_list = []
    for secondary in response:
        secondary_list.append(secondary[0])

    cursor.close()
    conn.close()

    response = {
        "contact": {
            "primaryContatctId": primary_contact_id,
            "emails": email_list,
            "phoneNumbers": phone_list,
            "secondaryContactIds": secondary_list,
        }
    }
    return response
