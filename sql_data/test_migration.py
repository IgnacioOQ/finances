import unittest
import pandas as pd
from datetime import date
import sqlite3
import os
from db_client import SQLiteClient
from migrate import standardize_columns, _process_and_upload

class TestSQLiteClient(unittest.TestCase):
    def setUp(self):
        # Use a temporary file for testing to ensure persistence across connections
        self.db_path = 'test_finance.db'
        # Clean up if it exists from a failed previous run
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

        self.client = SQLiteClient(db_path=self.db_path)
        self.client.create_tables()

    def tearDown(self):
        # Clean up the database file
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def test_create_tables(self):
        """Test that tables are created correctly."""
        conn = self.client.get_connection()
        cursor = conn.cursor()

        # Check if tables exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall()]

        self.assertIn("finance_price_history", tables)
        self.assertIn("finance_fundamentals", tables)
        conn.close()

    def test_upload_and_get_latest_date(self):
        """Test uploading data and retrieving the latest date."""
        df = pd.DataFrame({
            'date': ['2023-01-01', '2023-01-02'],
            'ticker': ['AAPL', 'AAPL'],
            'close': [150.0, 152.0]
        })

        self.client.upload_dataframe(df, "finance_price_history")

        latest = self.client.get_latest_date("AAPL", "finance_price_history")
        self.assertEqual(latest, date(2023, 1, 2))

    def test_upload_fundamentals(self):
        """Test uploading fundamental data."""
        df = pd.DataFrame({
            'date': ['2023-01-01'],
            'ticker': ['AAPL'],
            'market_cap': [2000000000.0],
            'pe_ratio': [25.5]
        })

        self.client.upload_dataframe(df, "finance_fundamentals")

        conn = self.client.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT market_cap FROM finance_fundamentals WHERE ticker='AAPL'")
        result = cursor.fetchone()
        self.assertEqual(result[0], 2000000000.0)
        conn.close()

class TestMigrationLogic(unittest.TestCase):
    def setUp(self):
        self.db_path = 'test_migration.db'
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

        self.client = SQLiteClient(db_path=self.db_path)
        self.client.create_tables()

    def tearDown(self):
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def test_standardize_columns(self):
        df = pd.DataFrame({
            'Date': ['2023-01-01'],
            'Adj Close': [150],
            'P/E Ratio': [20]
        })
        standardized = standardize_columns(df)
        expected_cols = ['date', 'adj_close', 'pe_ratio']
        self.assertEqual(list(standardized.columns), expected_cols)

    def test_incremental_upload(self):
        """Test that only new data is uploaded."""
        # 1. Upload initial data
        initial_df = pd.DataFrame({
            'date': [date(2023, 1, 1)],
            'ticker': ['AAPL'],
            'close': [100]
        })
        _process_and_upload(self.client, "AAPL", initial_df, "finance_price_history")

        # Verify count
        conn = self.client.get_connection()
        count = conn.execute("SELECT COUNT(*) FROM finance_price_history").fetchone()[0]
        self.assertEqual(count, 1)

        # 2. Try to upload mixed data (old + new)
        mixed_df = pd.DataFrame({
            'date': [date(2023, 1, 1), date(2023, 1, 2)],
            'ticker': ['AAPL', 'AAPL'],
            'close': [100, 101]
        })
        _process_and_upload(self.client, "AAPL", mixed_df, "finance_price_history")

        # Verify count (should be 2 now)
        count = conn.execute("SELECT COUNT(*) FROM finance_price_history").fetchone()[0]
        self.assertEqual(count, 2)

        # Verify latest date
        latest = self.client.get_latest_date("AAPL", "finance_price_history")
        self.assertEqual(latest, date(2023, 1, 2))
        conn.close()

if __name__ == '__main__':
    unittest.main()
