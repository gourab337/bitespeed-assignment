import sqlite3

try:
    # Connecting to DB, creating a cursor
    sqliteConnection = sqlite3.connect('fluxkart.db')
    cursor = sqliteConnection.cursor()
    print('DB Init')

    with open('./sql_query.sql', 'r') as f:
        sql_script = f.read()
    # Remember to delete the print statement in prod.
    print("Query: \n" + sql_script)
    # Executing the query.
    cursor.executescript(sql_script)

    cursor.close()

except sqlite3.Error as error:
    print('Error occurred - ', error)

# Close DB Connection irrespective of success or failure
finally:

    if sqliteConnection:
        sqliteConnection.close()
        print('SQLite Connection closed')