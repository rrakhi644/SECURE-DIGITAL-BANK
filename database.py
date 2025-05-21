# database.py
import mysql.connector

class DbTask:
    def creating_connection(self):
        connection = None
        try:
            connection = mysql.connector.connect(
                host='sql12.freesqldatabase.com',   # ✅ Cloud host
                user='sql12779970',                 # ✅ Your DB username
                password='pCUjHudNpc',              # 🔒 Replace with actual password
                database='sql12779970',             # ✅ Your assigned DB name
                port=3306                           # ✅ Optional, default MySQL port
            )
            print("✅ Connected to online database.")
        except mysql.connector.Error as err:
            print(f"❌ Error: {err}")
        return connection

# Testing connection
if __name__ == '__main__':
    obj2 = DbTask()
    obj2.creating_connection()
