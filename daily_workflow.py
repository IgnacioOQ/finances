from functions import *
from datetime import datetime
import os
import sys

# Add sql_data to path to import db modules
sys.path.append(os.path.join(os.getcwd(), 'sql_data'))
from db_client import SQLiteClient
from migrate import standardize_columns, _process_and_upload

# Create data directory if it doesn't exist
data_dir = 'stock_data'
os.makedirs(data_dir, exist_ok=True)

# Get today's date for file naming
today = datetime.now().strftime('%Y-%m-%d')
print(f"📅 Running daily workflow for: {today}")

# --- 1. Define Watchlist ---
my_tickers = [
    'AAPL',   # Apple
    'MSFT',   # Microsoft
    'GOOGL',  # Alphabet
    'AMZN',   # Amazon
    'NVDA',   # NVIDIA
    'TSLA',   # Tesla
    'META',   # Meta
]

benchmarks = ['SPY', 'VOO', 'QQQ']
all_tickers = my_tickers + benchmarks
print(f"📊 Tracking {len(my_tickers)} stocks and {len(benchmarks)} benchmarks")

# --- 2. Download & Persist Data ---
print("⬇️ Downloading latest price data...")
# Download 1 day of data for latest prices
latest_data = yf.download(all_tickers, period='5d', progress=False, auto_adjust=False)

# Convert to a format suitable for DB persistence (Long format)
# yfinance download with multiple tickers returns a MultiIndex columns dataframe.
# We need to flatten it: Date (index) -> Column, Ticker -> Column

# Stack the dataframe to get (Date, Ticker) as index
try:
    # Check if we have multi-level columns (Price, Ticker)
    if isinstance(latest_data.columns, pd.MultiIndex):
        # Stack the Ticker level (level 1) to become part of the index
        stacked = latest_data.stack(level=1, future_stack=True)
        stacked.index.names = ['Date', 'Ticker']
        stacked = stacked.reset_index()
    else:
        # Single ticker or flat structure (unlikely with list of tickers)
        stacked = latest_data.reset_index()
        # If single ticker, 'Ticker' column might be missing
        if 'Ticker' not in stacked.columns and len(all_tickers) == 1:
            stacked['Ticker'] = all_tickers[0]

    # Standardize columns for DB
    db_ready_df = standardize_columns(stacked)

    # Ensure 'date' column is datetime.date objects for comparison logic
    if 'date' in db_ready_df.columns:
        db_ready_df['date'] = pd.to_datetime(db_ready_df['date']).dt.date

    # Initialize DB Client
    db = SQLiteClient(db_path='sql_data/finance.db')
    db.create_tables()

    print(f"💾 Persisting data to SQLite ({len(db_ready_df)} rows)...")

    # Upload data for each ticker (using helper from migrate.py logic)
    # We iterate to use the incremental check logic efficiently
    unique_tickers = db_ready_df['ticker'].unique()
    for ticker in unique_tickers:
        ticker_df = db_ready_df[db_ready_df['ticker'] == ticker].copy()
        _process_and_upload(db, ticker, ticker_df, "finance_price_history")

except Exception as e:
    print(f"❌ Error during database persistence: {e}")
    # Fallback: Save to CSV only if DB fails? Or just log.
    print("⚠️ Saving raw dump to CSV as backup...")
    csv_file = f"{data_dir}/daily_prices_backup_{today}.csv"
    latest_data.to_csv(csv_file)


# --- 3. Generate & Display Performance Summaries (No CSV Dump) ---
print("\n" + "="*80)
print("📈 PERFORMANCE SUMMARIES (Plots Only)")
print("="*80)

# We can reuse the generate_performance_summary function but suppress its CSV saving if it did any
# (The function in functions.py returns a DF and prints it, it doesn't save CSVs itself).
# The original notebook was saving the returns of this function.
# Here we just run them to print the tables to console/logs.

print("\n--- 1 Week Performance ---")
summary_1w = generate_performance_summary(my_tickers, period='5d', benchmark='SPY')

print("\n--- 1 Month Performance ---")
summary_1m = generate_performance_summary(my_tickers, period='1mo', benchmark='SPY')

print("\n--- Year-to-Date Performance ---")
summary_ytd = generate_performance_summary(my_tickers, period='ytd', benchmark='SPY')

print("\n--- 1 Year Performance ---")
summary_1y = generate_performance_summary(my_tickers, period='1y', benchmark='SPY')


# --- 4. Plots ---
print("\n📊 Generating Plots...")
# These functions call plt.show(), which will display if run interactively
# or can be caught by backend if needed.
download_and_plot_stock_data(my_tickers, period='ytd')


# --- 5. Daily Summary Report ---
print("\n" + "="*80)
print(f"📋 DAILY SUMMARY REPORT - {today}")
print("="*80)

# Winners/Losers based on 1 week
winners_1d = (summary_1w['Total Return (%)'] > 0).sum()
losers_1d = (summary_1w['Total Return (%)'] < 0).sum()

print(f"\n📊 Market Breadth (5 days):")
print(f"   Winners: {winners_1d} | Losers: {losers_1d}")

best = summary_1w['Total Return (%)'].idxmax()
worst = summary_1w['Total Return (%)'].idxmin()

print(f"\n🌟 Best Performer (5d): {best} ({summary_1w.loc[best, 'Total Return (%)']}%)\n")
print(f"⚠️  Worst Performer (5d): {worst} ({summary_1w.loc[worst, 'Total Return (%)']}%)\n")

print("Done.")
