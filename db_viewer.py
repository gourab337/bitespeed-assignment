import sqlite3

# Connect to the database
conn = sqlite3.connect('fluxkart.db')

# Create a cursor object to execute SQL queries
cursor = conn.cursor()


# Select all rows from the table
cursor.execute("SELECT * FROM Contact")
rows = cursor.fetchall()

# Print the column names
column_names = [description[0] for description in cursor.description]
print("\t".join(column_names))

# Print the table contents
for row in rows:
    print("\t".join(str(item) for item in row))
print()

# Close the cursor and the connection
cursor.close()
conn.close()
