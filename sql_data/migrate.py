import os
import pandas as pd
from datetime import datetime
from db_client import SQLiteClient

STOCK_DATA_DIR = 'stock_data'

def standardize_columns(df):
    """
    Standardizes DataFrame columns to match the Database schema.
    Converts CamelCase/spaces to snake_case.
    """
    # Mapping for standard yfinance output
    mapping = {
        'Date': 'date',
        'Open': 'open',
        'High': 'high',
        'Low': 'low',
        'Close': 'close',
        'Adj Close': 'adj_close',
        'Adj_Close': 'adj_close',
        'Volume': 'volume',
        'Ticker': 'ticker',
        'Symbol': 'ticker',
        'Market Cap': 'market_cap',
        'P/E Ratio': 'pe_ratio',
        'Dividend Yield': 'dividend_yield'
    }

    df = df.rename(columns=mapping)
    df.columns = [c.lower().replace(' ', '_') for c in df.columns]
    return df

def migrate_data():
    """
    Scans the stock_data directory and migrates data to SQLite.
    """
    db = SQLiteClient()
    # Ensure tables exist
    db.create_tables()

    print(f"Scanning {STOCK_DATA_DIR} for CSV files...")

    if not os.path.exists(STOCK_DATA_DIR):
        print(f"Directory {STOCK_DATA_DIR} does not exist.")
        return

    for filename in os.listdir(STOCK_DATA_DIR):
        if not filename.endswith('.csv'):
            continue

        filepath = os.path.join(STOCK_DATA_DIR, filename)
        print(f"Processing {filename}...")

        try:
            df = pd.read_csv(filepath)
            df = standardize_columns(df)

            # Ensure 'date' column is datetime
            if 'date' in df.columns:
                df['date'] = pd.to_datetime(df['date']).dt.date
            else:
                print(f"Skipping {filename}: No 'Date' column found.")
                continue

            # Determine Table and Ticker
            # Case 1: daily_prices.csv (Contains multiple tickers, only Price)
            if filename == 'daily_prices.csv':
                # Map 'Price' to 'close' or 'adj_close'
                # The file has Ticker, Price, Date.
                # We'll map Price to close for now, as it's the most generic.
                if 'price' in df.columns:
                    df = df.rename(columns={'price': 'close'})

                # Iterate by ticker to do incremental updates
                if 'ticker' in df.columns:
                    tickers = df['ticker'].unique()
                    for ticker in tickers:
                        ticker_df = df[df['ticker'] == ticker].copy()
                        _process_and_upload(db, ticker, ticker_df, "finance_price_history")
                else:
                    print(f"Skipping {filename}: No 'Ticker' column found.")

            # Case 2: Standard history file (e.g. history_AAPL.csv)
            # Usually these files are single-ticker. We need to infer ticker from filename if not in columns.
            elif 'history_' in filename:
                # Infer ticker from filename history_AAPL.csv -> AAPL
                # This assumes a naming convention.
                ticker = filename.replace('history_', '').replace('.csv', '')
                df['ticker'] = ticker # Add ticker column

                _process_and_upload(db, ticker, df, "finance_price_history")

            # Case 3: Performance/Fundamentals (Not implemented in this pass, can be added later)
            elif 'performance_' in filename:
                 print(f"Skipping {filename}: Performance summaries are not yet mapped to DB.")

            else:
                print(f"Skipping {filename}: Unknown file format.")

        except Exception as e:
            print(f"Error processing {filename}: {e}")

def _process_and_upload(db, ticker, df, table_name):
    """
    Helper to filter new rows and upload.
    """
    latest_date = db.get_latest_date(ticker, table_name)

    if latest_date:
        print(f"[{ticker}] Latest date in DB: {latest_date}")
        # Filter for data strictly after the latest date
        new_data = df[df['date'] > latest_date]
    else:
        print(f"[{ticker}] No data in DB. Uploading all.")
        new_data = df

    if not new_data.empty:
        print(f"[{ticker}] Uploading {len(new_data)} new rows...")
        # Ensure only columns in schema are uploaded
        # For price history:
        expected_cols = ['date', 'ticker', 'open', 'high', 'low', 'close', 'adj_close', 'volume']

        # Select only expected columns that exist in new_data
        cols_to_upload = [col for col in expected_cols if col in new_data.columns]

        # Add missing columns as None to ensure schema match (though to_sql handles missing cols by inserting NULL)
        # However, to be safe and use .loc to avoid copy warnings:
        upload_df = new_data.copy()

        # Add ticker if missing (should be there)
        if 'ticker' not in upload_df.columns:
             upload_df['ticker'] = ticker

        # Filter columns to only what is allowed
        upload_df = upload_df[[c for c in upload_df.columns if c in expected_cols]]

        db.upload_dataframe(upload_df, table_name)
    else:
        print(f"[{ticker}] No new data to upload.")

if __name__ == '__main__':
    migrate_data()
