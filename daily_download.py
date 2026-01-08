# Import required libraries
import sys
import traceback

try:
    from functions import *
    from datetime import datetime
    import os
    import pandas as pd
    import yfinance as yf

    # Create data directory if it doesn't exist
    data_dir = 'stock_data'
    os.makedirs(data_dir, exist_ok=True)

    # Get today's date for file naming
    today = datetime.now().strftime('%Y-%m-%d')
    print(f"📅 Running daily download for: {today}")

    # --- 1. Define Watchlist (S&P 500 + Benchmarks) ---
    print("📊 Fetching S&P 500 tickers...")
    try:
        sp500_df = get_sp500_symbols()
        # Replace dots with hyphens for Yahoo Finance (e.g., BRK.B -> BRK-B)
        sp500_df['Symbol'] = sp500_df['Symbol'].str.replace('.', '-', regex=False)
        sp500_tickers = sp500_df['Symbol'].tolist()
        # Create a mapping for sectors for later use
        sector_map = sp500_df.set_index('Symbol')['GICS Sector'].to_dict()
        print(f"✅ Loaded {len(sp500_tickers)} S&P 500 tickers.")
    except Exception as e:
        print(f"❌ Error fetching S&P 500 list: {e}")
        # Fallback list if Wikipedia scrape fails
        # Note: BRK-B instead of BRK.B for Yahoo Finance
        sp500_tickers = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'TSLA', 'META', 'BRK-B', 'LLY', 'V']
        sector_map = {
            'AAPL': 'Information Technology',
            'MSFT': 'Information Technology',
            'GOOGL': 'Communication Services',
            'AMZN': 'Consumer Discretionary',
            'NVDA': 'Information Technology',
            'TSLA': 'Consumer Discretionary',
            'META': 'Communication Services',
            'BRK-B': 'Financials',
            'LLY': 'Health Care',
            'V': 'Financials'
        }
        print(f"⚠️ Using fallback list of {len(sp500_tickers)} top stocks.")

    # Benchmark ETFs
    benchmarks = ['SPY', 'VOO', 'QQQ']

    # Combine lists (remove duplicates)
    all_tickers = list(set(sp500_tickers + benchmarks))
    print(f"📊 Total tickers to track: {len(all_tickers)}")


    # --- 2. Download Latest Price Data ---
    print("\n⬇️ Downloading latest price data...")

    # Get 5 days of data to calculate recent moves and ensure we have the latest close
    # (Some APIs might return empty for 'today' if market is open/just opened, so 5d is safer)
    # Explicitly disable threads for safety
    latest_data = yf.download(all_tickers, period='5d', progress=False, threads=False)

    # Extract latest prices (last row)
    if 'Adj Close' in latest_data:
        latest_prices = latest_data['Adj Close'].iloc[-1]
    else:
        latest_prices = latest_data['Close'].iloc[-1]

    # Create Daily Price DataFrame
    latest_df = pd.DataFrame({
        'Ticker': latest_prices.index,
        'Price': latest_prices.values,
        'Date': today
    })

    # Add Sector info
    latest_df['Sector'] = latest_df['Ticker'].map(sector_map).fillna('Unknown')

    print(f"\n✅ Latest Prices (Top 5):")
    print(latest_df.head().to_string(index=False))

    # Save to CSV (append mode)
    csv_file = f"{data_dir}/daily_prices.csv"
    if os.path.exists(csv_file):
        latest_df.to_csv(csv_file, mode='a', header=False, index=False)
        print(f"📝 Appended to {csv_file}")
    else:
        latest_df.to_csv(csv_file, index=False)
        print(f"📝 Created new file: {csv_file}")


    # --- 3. Performance Summary & Metrics ---
    # We will generate summaries for key timeframes.
    # Note: generate_performance_summary downloads its own data.
    # Optimization: In a production DB environment, we would download once and calculate everything.
    # For now, we reuse the existing function for simplicity and reliability.

    timeframes = {
        '1week': '5d',
        '1month': '1mo',
        '3month': '3mo',
        'ytd': 'ytd',
        '1year': '1y'
    }

    print("\n📈 Generating Performance Summaries...")

    for tf_name, period in timeframes.items():
        print(f"   Processing {tf_name} ({period})...")
        try:
            summary_df = generate_performance_summary(all_tickers, period=period, benchmark='SPY')

            # Enrich with Sector data
            summary_df['Sector'] = summary_df.index.map(sector_map).fillna('Unknown')

            # Save to CSV
            filename = f"{data_dir}/performance_{tf_name}_{today}.csv"
            summary_df.to_csv(filename)
            print(f"   💾 Saved {filename}")

        except Exception as e:
            print(f"   ❌ Error generating {tf_name} summary: {e}")

    # --- 4. Daily Summary Report (Console Output) ---
    print("\n" + "="*80)
    print(f"📋 DAILY SUMMARY REPORT - {today}")
    print("="*80)

    # Load 1-week summary for breadth analysis
    try:
        summary_1w = pd.read_csv(f"{data_dir}/performance_1week_{today}.csv", index_col=0)

        # Market Breadth
        winners = (summary_1w['Total Return (%)'] > 0).sum()
        losers = (summary_1w['Total Return (%)'] < 0).sum()

        print(f"\n📊 Market Breadth (5 days):")
        print(f"   Winners: {winners} | Losers: {losers}")

        # Sector Performance (Average return by sector)
        if 'Sector' in summary_1w.columns:
            print("\n🏭 Sector Performance (5 days):")
            sector_perf = summary_1w.groupby('Sector')['Total Return (%)'].mean().sort_values(ascending=False)
            print(sector_perf.to_string())

        # Top/Bottom Performers (S&P 500)
        print(f"\n🌟 Top 5 Performers (5d):")
        print(summary_1w['Total Return (%)'].nlargest(5).to_string())

        print(f"\n⚠️ Bottom 5 Performers (5d):")
        print(summary_1w['Total Return (%)'].nsmallest(5).to_string())

    except Exception as e:
        print(f"Could not generate text report: {e}")

    print(f"\n{'='*80}\n")
    print("✅ Daily download complete.")

    # Explicitly exit with success code
    sys.exit(0)

except Exception as e:
    print(f"\n❌ FATAL ERROR in daily download script:")
    traceback.print_exc()
    # In CI, we usually want to know if it failed, so exit with 1.
    # However, if you want it to 'pass' even on error to keep the workflow green, use sys.exit(0)
    sys.exit(1)
