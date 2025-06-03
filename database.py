import psycopg2

class DbTask:
    def creating_connection(self):
        conn = None
        try:
            conn = psycopg2.connect(
                host="ep-jolly-block-a81z4ltb-pooler.eastus2.azure.neon.tech",
                database="neondb",
                user="neondb_owner",
                password="npg_SELOWl0j1XxA",
                sslmode="require"
            )
            cursor = conn.cursor()
            print("✅ Connected to NeonDB")

            # Create ACCOUNTS table if not exists
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ACCOUNTS (
                    ACCOUNT_ID BIGINT PRIMARY KEY,
                    NAME VARCHAR(100) NOT NULL,
                    PHONE VARCHAR(15) NOT NULL,
                    CITY VARCHAR(50) NOT NULL,
                    PIN INTEGER NOT NULL,
                    BALANCE NUMERIC(12, 2) DEFAULT 0.00,
                    CREATED_AT TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)

            # Create TRANSACTIONS table if not exists
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS TRANSACTIONS (
                    TRANSACTION_ID SERIAL PRIMARY KEY,
                    AC_ID BIGINT REFERENCES ACCOUNTS(ACCOUNT_ID) ON DELETE CASCADE,
                    AMOUNT NUMERIC(12, 2) NOT NULL,
                    TRANS_DATE TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)

            conn.commit()
            print("✅ Tables checked/created successfully.")

        except Exception as error:
            print("❌ Error while connecting to PostgreSQL:", error)
        return conn

# Testing connection
if __name__ == '__main__':
    obj2 = DbTask()
    obj2.creating_connection()
