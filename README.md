# Stock Performance Analysis & Reporting

A comprehensive Python toolkit for analyzing stock performance, generating reports, and tracking daily market data.

## Features

- 📊 **Performance Analysis**: Calculate returns, volatility, Sharpe ratios, and max drawdown
- 📈 **Visualization**: Normalized price charts, P/E ratio trends, and daily volatility plots
- 💰 **Valuation Metrics**: P/E, P/B, PEG ratios, debt-to-equity, EBITDA, and dividend yields
- 🔄 **Daily Tracking**: Automated notebook for daily data downloads and reports
- 🎯 **Benchmark Comparison**: Compare stocks against SPY, VOO, or custom benchmarks
- 📋 **S&P 500 Integration**: Fetch current S&P 500 components by sector

## Files

- **`functions.py`**: Core analysis functions (all capabilities)
- **`imports.py`**: Required library imports
- **`daily_download.ipynb`**: Run daily to download data and generate reports
- **`example_analysis.ipynb`**: Usage examples for all features
- **`README.md`**: This file

## Installation

Install required dependencies:

```bash
pip install pandas yfinance matplotlib tqdm requests beautifulsoup4
```

## Quick Start

### Daily Tracking

Open and run `daily_download.ipynb`:

```python
# Edit your watchlist
my_tickers = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA']

# Run all cells to:
# - Download latest prices
# - Generate performance reports (1W, 1M, 3M, YTD, 1Y)
# - Save data to CSV
# - Display top performers and laggards
```

### Analysis Examples

See `example_analysis.ipynb` for comprehensive examples.

## Available Functions

### 1. `get_sp500_symbols()`
Fetch current S&P 500 companies from Wikipedia.

```python
sp500 = get_sp500_symbols()
tech_stocks = sp500[sp500['GICS Sector'] == 'Information Technology']
```

### 2. `fetch_one_ticker(symbol, period='10y')`
Deep analysis of a single stock with visualizations.

```python
data = fetch_one_ticker('AAPL', period='5y')
# Displays: P/B, PEG, Debt/Equity, EBITDA
# Plots: Price, Market Cap, P/E Ratio, Dividend Yield
```

### 3. `download_and_plot_stock_data(tickers, period='10y')`
Compare multiple stocks with normalized performance.

```python
normalized = download_and_plot_stock_data(['AAPL', 'MSFT', 'GOOGL'], period='2y')
# Automatically includes VOO and RSP benchmarks
```

### 4. `download_and_plot_daily_pct_change(tickers, period='10y')`
Visualize daily volatility and movement patterns.

```python
pct_changes = download_and_plot_daily_pct_change(['AAPL', 'TSLA'], period='6mo')
volatility = pct_changes.std()  # Calculate volatility
```

### 5. `generate_performance_summary(tickers, period='1y', benchmark='SPY')`
Comprehensive performance metrics report.

```python
summary = generate_performance_summary(['AAPL', 'MSFT', 'NVDA'], period='1y')
# Returns: Total Return, Annualized Return, Volatility, Sharpe Ratio,
#          Max Drawdown, Current Price, vs Benchmark
```

### 6. `fetch_historical_stock_data(ticker_list, period='5Y', verbose=False)`
Monthly historical data with weighted portfolio metrics.

```python
data = fetch_historical_stock_data(['AAPL', 'MSFT', 'GOOGL'], period='3y', verbose=True)
# Includes: Weighted P/E ratio time series
# Metrics: P/B, PEG, Debt/Equity, EBITDA (weighted by market cap, earnings, revenue)
```

### 7. `get_etfdb_pe_ratio(symbol)`
Scrape P/E ratios for ETFs from etfdb.com.

```python
voo_pe = get_etfdb_pe_ratio('VOO')
```

## Usage Examples

### Example 1: Daily Portfolio Tracking

```python
from functions import *

# Define portfolio
portfolio = ['AAPL', 'MSFT', 'GOOGL', 'NVDA', 'AMZN']

# Get today's performance
perf_today = generate_performance_summary(portfolio, period='5d', benchmark='SPY')

# Save to CSV
perf_today.to_csv('portfolio_performance.csv')
```

### Example 2: Sector Analysis

```python
# Technology stocks
tech = ['AAPL', 'MSFT', 'NVDA', 'GOOGL', 'META']

# Compare 1-year performance
tech_perf = generate_performance_summary(tech, period='1y', benchmark='XLK')

# Visualize normalized performance
normalized = download_and_plot_stock_data(tech, period='1y')
```

### Example 3: Risk Analysis

```python
# Diverse portfolio
stocks = ['AAPL', 'JNJ', 'XOM', 'KO', 'PG']

# Calculate risk-adjusted returns
summary = generate_performance_summary(stocks, period='2y')

# Sort by Sharpe Ratio
best_risk_adjusted = summary.sort_values('Sharpe Ratio', ascending=False)
print(best_risk_adjusted[['Total Return (%)', 'Volatility (%)', 'Sharpe Ratio']])
```

### Example 4: Multi-Timeframe Analysis

```python
ticker = 'NVDA'
periods = ['1mo', '3mo', '6mo', '1y', '2y']

for period in periods:
    perf = generate_performance_summary([ticker], period=period)
    print(f"{period}: {perf.loc[ticker, 'Total Return (%)']}%")
```

## Performance Metrics Explained

- **Total Return (%)**: Total percentage return over the period
- **Annualized Return (%)**: Compound annual growth rate (CAGR)
- **Volatility (%)**: Annualized standard deviation of daily returns
- **Sharpe Ratio**: Risk-adjusted return (higher is better)
- **Max Drawdown (%)**: Largest peak-to-trough decline
- **vs Benchmark (%)**: Outperformance relative to benchmark

## Data Storage

`daily_download.ipynb` saves data to `stock_data/` directory:

- `daily_prices.csv`: Appends daily price data
- `performance_1week_YYYY-MM-DD.csv`: Weekly performance snapshot
- `performance_1month_YYYY-MM-DD.csv`: Monthly performance snapshot
- `performance_3month_YYYY-MM-DD.csv`: Quarterly performance snapshot
- `performance_ytd_YYYY-MM-DD.csv`: Year-to-date performance snapshot
- `performance_1year_YYYY-MM-DD.csv`: Annual performance snapshot

## Tips

1. **Daily Workflow**: Run `daily_download.ipynb` every morning before market open
2. **Historical Analysis**: Use `example_analysis.ipynb` for deep dives
3. **Custom Benchmarks**: Change benchmark parameter to match your strategy (e.g., 'QQQ' for tech-heavy portfolios)
4. **Sector Filtering**: Use `get_sp500_symbols()` to filter by GICS sector
5. **Risk Management**: Monitor Sharpe Ratio and Max Drawdown for risk-adjusted performance

## Notes

- All data sourced from Yahoo Finance via `yfinance`
- S&P 500 list fetched from Wikipedia
- ETF P/E ratios scraped from etfdb.com (may be affected by website changes)
- Assumes 252 trading days per year for annualized calculations
- Risk-free rate assumed to be 0% for Sharpe ratio calculations

## License

Free to use for personal and educational purposes.
