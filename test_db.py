import mysql.connector
from config import DB_CONFIG

try:
    db = mysql.connector.connect(**DB_CONFIG)

    if db.is_connected():
        print("SUCCESS: Connected to DueMate database!")

        cursor = db.cursor()
        cursor.execute("SHOW TABLES")

        print("\nTables in DueMate:")

        for table in cursor.fetchall():
            print(table[0])

        cursor.close()
        db.close()

except mysql.connector.Error as e:
    print("Database connection failed:", e)