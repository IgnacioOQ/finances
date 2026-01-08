import sqlite3
import pandas as pd
import os
from datetime import datetime

class SQLiteClient:
    def __init__(self, db_path='sql_data/finance.db'):
        """
        Initialize the SQLite client.

        Args:
            db_path (str): Path to the SQLite database file.
        """
        # Ensure the directory exists
        db_dir = os.path.dirname(db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir)

        self.db_path = db_path

    def get_connection(self):
        """Returns a connection to the SQLite database."""
        return sqlite3.connect(self.db_path)

    def create_tables(self):
        """Creates the necessary tables if they do not exist."""
        conn = self.get_connection()
        cursor = conn.cursor()

        # Schema for Finance Price History
        # SQLite types: NULL, INTEGER, REAL, TEXT, BLOB
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS finance_price_history (
                date TEXT NOT NULL,
                ticker TEXT NOT NULL,
                open REAL,
                high REAL,
                low REAL,
                close REAL,
                adj_close REAL,
                volume INTEGER,
                PRIMARY KEY (date, ticker)
            )
        """)

        # Schema for Finance Fundamentals
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS finance_fundamentals (
                date TEXT NOT NULL,
                ticker TEXT NOT NULL,
                market_cap REAL,
                pe_ratio REAL,
                dividend_yield REAL,
                PRIMARY KEY (date, ticker)
            )
        """)

        conn.commit()
        conn.close()
        print(f"Tables ensured in {self.db_path}")

    def get_latest_date(self, ticker, table_name="finance_price_history"):
        """
        Retrieves the latest date for a given ticker in the specified table.
        Returns a datetime.date object or None if no data exists.
        """
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            query = f"SELECT MAX(date) FROM {table_name} WHERE ticker = ?"
            cursor.execute(query, (ticker,))
            result = cursor.fetchone()

            if result and result[0]:
                # SQLite stores dates as strings, convert back to date object
                return datetime.strptime(result[0], '%Y-%m-%d').date()
            return None
        except sqlite3.Error as e:
            print(f"Error querying max date for {ticker}: {e}")
            return None
        finally:
            conn.close()

    def upload_dataframe(self, df, table_name):
        """
        Uploads a pandas DataFrame to the specified SQLite table.
        """
        if df.empty:
            print("Empty dataframe, skipping upload.")
            return

        conn = self.get_connection()
        try:
            # Ensure date column is string format YYYY-MM-DD for consistency
            if 'date' in df.columns:
                # Check if it's already string or datetime
                if not pd.api.types.is_string_dtype(df['date']):
                    df = df.copy()
                    df['date'] = df['date'].apply(lambda x: x.strftime('%Y-%m-%d') if isinstance(x, (datetime, pd.Timestamp)) else str(x))

            # Append data. 'if_exists="append"' adds new rows.
            # Note: This does not handle Primary Key duplicates automatically (it will raise IntegrityError).
            # For this simple implementation, we rely on the upstream logic to filter duplicates.
            df.to_sql(table_name, conn, if_exists='append', index=False)
            print(f"Loaded {len(df)} rows into {table_name}")
        except sqlite3.IntegrityError as e:
            print(f"Integrity Error (likely duplicate data): {e}")
        except Exception as e:
            print(f"Failed to upload data to {table_name}: {e}")
            raise e
        finally:
            conn.close()
