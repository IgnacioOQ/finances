# CLAUDE.md - Development Log & Guidelines

**Last Updated:** 2026-01-05
**Current Branch:** `claude/stock-reporting-improvements-q6lux` (merged to main)
**Repository:** finances - Stock Performance Analysis & Reporting

---

## Project Overview

This repository contains a comprehensive Python toolkit for analyzing stock performance, generating reports, and tracking daily market data using Yahoo Finance API.

### Core Components
- **[functions.py](functions.py)**: All analysis functions with comprehensive docstrings
- **[imports.py](imports.py)**: Centralized library imports
- **[daily_download.ipynb](daily_download.ipynb)**: Automated daily data collection notebook
- **[example_analysis.ipynb](example_analysis.ipynb)**: Comprehensive usage examples
- **[README.md](README.md)**: Complete documentation

---

## Recent Updates (Branch: claude/stock-reporting-improvements-q6lux)

### Latest Commit: e11d328 - "Polish stock reporting code and add daily download notebook"

**Date:** 2026-01-04

#### Changes Made:

1. **Bug Fixes**
   - Fixed bug in `download_and_plot_daily_pct_change()` function
   - Ensured proper handling of adjusted close prices vs close prices

2. **Documentation Improvements**
   - Added comprehensive docstrings to all functions in [functions.py](functions.py)
   - Each function now includes:
     - Purpose description
     - Args with types and defaults
     - Returns with types
     - Displays section (what visualizations are shown)
     - Additional notes where relevant

3. **New Functions Added**
   - `generate_performance_summary(tickers, period='1y', benchmark='SPY')` - [functions.py:422](functions.py#L422)
     - Calculates comprehensive performance metrics
     - Returns: Total Return, Annualized Return, Volatility, Sharpe Ratio, Max Drawdown, Current Price, vs Benchmark
     - Includes formatted console output

4. **New Notebooks Created**
   - **[daily_download.ipynb](daily_download.ipynb)**: Automated daily tracking workflow
     - Configurable watchlist
     - Multi-timeframe reports (1W, 1M, 3M, YTD, 1Y)
     - CSV data storage in `stock_data/` directory
     - Top performers and laggards analysis
     - Daily summary report with market breadth

   - **[example_analysis.ipynb](example_analysis.ipynb)**: Complete feature demonstration
     - 10 different analysis examples
     - S&P 500 integration
     - Sector comparison
     - Risk analysis
     - Multi-timeframe analysis

5. **Documentation Created**
   - **[README.md](README.md)**: Complete project documentation
     - Features overview
     - Installation instructions
     - Function reference with examples
     - Performance metrics explanations
     - Usage tips and best practices

6. **Configuration Files**
   - **[.vscode/settings.json](.vscode/settings.json)**: VS Code Python environment settings
     - Configured for conda environment management

---

## Available Functions

### Data Fetching Functions

1. **`get_sp500_symbols()`** - [functions.py:3](functions.py#L3)
   - Fetches S&P 500 companies from Wikipedia
   - Returns: DataFrame with Symbol, Security, GICS Sector

2. **`fetch_one_ticker(symbol, period='10y')`** - [functions.py:15](functions.py#L15)
   - Comprehensive single stock analysis
   - Displays: P/B, PEG, Debt/Equity, EBITDA
   - Plots: Price, Market Cap, P/E Ratio, Dividend Yield

3. **`fetch_historical_stock_data(ticker_list, period='5Y', verbose=False)`** - [functions.py:238](functions.py#L238)
   - Monthly historical data for multiple stocks
   - Calculates weighted portfolio metrics
   - Plots weighted P/E ratio time series

### Comparison & Visualization Functions

4. **`download_and_plot_stock_data(tickers, period='10y')`** - [functions.py:135](functions.py#L135)
   - Normalized price performance comparison
   - Auto-includes VOO and RSP benchmarks
   - Returns normalized prices (starting value = 1.0)

5. **`download_and_plot_daily_pct_change(tickers, period='10y')`** - [functions.py:193](functions.py#L193)
   - Daily percentage change visualization
   - Auto-includes SPY and RSP benchmarks
   - Useful for volatility analysis

### Performance Analysis Functions

6. **`generate_performance_summary(tickers, period='1y', benchmark='SPY')`** - [functions.py:422](functions.py#L422)
   - Comprehensive performance metrics
   - Metrics: Returns, Volatility, Sharpe, Max Drawdown
   - Formatted console output
   - Sorted by total return

### Utility Functions

7. **`get_etfdb_pe_ratio(symbol)`** - [functions.py:524](functions.py#L524)
   - Web scraping for ETF P/E ratios
   - Source: etfdb.com
   - May be affected by website structure changes

---

## Common Issues & Mistakes to Avoid

### 1. **Benchmark Auto-Inclusion Inconsistency**

**Issue:** Different functions auto-include different benchmarks:
- `download_and_plot_stock_data()` adds: `['VOO', 'RSP']`
- `download_and_plot_daily_pct_change()` adds: `['SPY', 'RSP']`

**Fix Needed:** Standardize benchmark inclusion across functions or make it configurable via parameter.

**Workaround:** Users should be aware that different functions use different default benchmarks.

---

### 2. **Adjusted Close vs Close Column Handling**

**Issue:** Inconsistent handling of 'Adj Close' vs 'Close' across functions.

**Current Implementation:**
- Some functions check for 'Adj Close' and fall back to 'Close'
- Others assume 'Adj Close' is always available

**Best Practice:** Always check for both and provide clear feedback to user:
```python
if 'Adj Close' in data:
    prices = data['Adj Close']
elif 'Close' in data:
    print("Warning: 'Adj Close' not found. Using 'Close' instead.")
    prices = data['Close']
else:
    raise ValueError("Neither 'Adj Close' nor 'Close' found")
```

---

### 3. **Static EPS for Historical P/E Calculation**

**Limitation:** Functions use current trailing EPS to calculate historical P/E ratios.

**Location:** [functions.py:69-72](functions.py#L69-L72) in `fetch_one_ticker()`

**Impact:** Historical P/E ratios are approximations only, not actual historical values.

**Note Added:** Function now includes explanatory print statement:
```python
plt.title(f"{symbol} - Historic P/E Ratio (based on static trailing EPS = {eps:.2f})")
```

**Future Improvement:** Consider fetching historical earnings data for accurate P/E calculations.

---

### 4. **Error Handling for Missing Data**

**Good Practice Implemented:**
- Functions check for empty DataFrames
- Handle missing `sharesOutstanding` gracefully
- Provide informative print statements

**Example from code:**
```python
if hist.empty:
    print("No historical price data available.")
    return None

if shares_outstanding is None:
    print("Shares outstanding data not available.")
    shares_outstanding = 1  # Avoid NaN in market cap calc
```

---

### 5. **ETF vs Stock Handling**

**Implementation:** `fetch_historical_stock_data()` detects ETFs and skips valuation metrics.

**Location:** [functions.py:282-309](functions.py#L282-L309)

**Logic:**
```python
quote_type = info.get("quoteType", "").upper()
is_etf = (quote_type == "ETF")

if is_etf or shares_outstanding is None or eps is None:
    # Skip valuation metrics, only include Close and Dividend_Yield
```

**Best Practice:** Maintain this separation between ETF and stock analysis.

---

### 6. **Web Scraping Dependencies**

**Function:** `get_etfdb_pe_ratio(symbol)` - [functions.py:524](functions.py#L524)

**Warning:** This function relies on:
- External website structure (etfdb.com)
- BeautifulSoup HTML parsing
- Specific table structure

**Risk:** May break if website changes structure.

**Recommendation:** Implement try-except blocks and provide clear error messages (already done).

---

### 7. **Rate Limiting for Yahoo Finance API**

**Implementation:** `fetch_historical_stock_data()` includes sleep delays:
```python
time.sleep(0.5)  # Between ticker requests
```

**Location:** [functions.py:266](functions.py#L266)

**Best Practice:** Maintain rate limiting to avoid API throttling.

**Note:** Commented-out code exists for sequential downloads ([functions.py:156-163](functions.py#L156-L163)) - keep as backup if bulk download fails.

---

### 8. **Dividend Yield Calculation**

**Method:** Monthly resampling with forward-fill

**Implementation:**
```python
dividends = dividends.resample('ME').sum()
price_monthly = hist['Adj_Close'].resample('ME').last()
dividend_yield = (dividends / price_monthly).fillna(0)
hist['Dividend_Yield'] = dividend_yield.reindex(hist.index, method='ffill').fillna(0)
```

**Note:** Uses 'ME' for month-end frequency (pandas convention).

---

### 9. **Plotting Style**

**Style Set:** `plt.style.use('ggplot')`

**Location:** [functions.py:107](functions.py#L107)

**Consistency:** Applied in `fetch_one_ticker()` but not in other plot functions.

**Recommendation:** Consider standardizing plot style across all functions.

---

### 10. **DataFrame Column Naming**

**Convention Used:**
- Snake_case for created columns: `Adj_Close`, `Market_Cap`, `P/E_Ratio`, `Dividend_Yield`
- Matches pandas convention for multi-word column names

**Best Practice:** Maintain this convention for consistency.

---

## Development Guidelines

### When Adding New Functions:

1. **Always include comprehensive docstrings:**
   ```python
   def function_name(param1, param2='default'):
       """
       Brief description.

       Detailed explanation of what the function does.

       Args:
           param1 (type): Description
           param2 (type): Description (default: 'default')

       Returns:
           type: Description

       Displays:
           - What visualizations/outputs are shown
       """
   ```

2. **Handle missing data gracefully:**
   - Check for empty DataFrames
   - Provide informative print statements
   - Return None or appropriate default values

3. **Include progress indicators:**
   - Use `tqdm` for loops over multiple tickers
   - Use `progress=False` in `yf.download()` for cleaner output in notebooks

4. **Benchmark inclusion:**
   - Consider making benchmark inclusion configurable
   - Document which benchmarks are auto-included

5. **Error handling:**
   - Wrap API calls in try-except blocks
   - Print specific error messages
   - Continue processing other tickers if one fails

### Code Style:

- Follow PEP 8 conventions
- Use descriptive variable names
- Add comments for complex calculations
- Keep functions focused on single responsibility

---

## Data Storage Structure

### Directory: `stock_data/`

Created by [daily_download.ipynb](daily_download.ipynb):

- `daily_prices.csv` - Appended daily (columns: Ticker, Price, Date)
- `performance_1week_YYYY-MM-DD.csv` - Weekly snapshots
- `performance_1month_YYYY-MM-DD.csv` - Monthly snapshots
- `performance_3month_YYYY-MM-DD.csv` - Quarterly snapshots
- `performance_ytd_YYYY-MM-DD.csv` - YTD snapshots
- `performance_1year_YYYY-MM-DD.csv` - Annual snapshots

---

## Dependencies

```python
pandas
yfinance
matplotlib
tqdm
requests
beautifulsoup4
```

Install with:
```bash
pip install pandas yfinance matplotlib tqdm requests beautifulsoup4
```

---

## Testing & Validation

### Before Committing Changes:

1. Run all cells in [example_analysis.ipynb](example_analysis.ipynb)
2. Run all cells in [daily_download.ipynb](daily_download.ipynb)
3. Verify all plots display correctly
4. Check console output for error messages
5. Validate CSV files are created in `stock_data/`

---

## Future Improvements

### Potential Enhancements:

1. **Historical EPS Data**: Fetch historical earnings for accurate P/E ratios
2. **Standardize Benchmarks**: Make benchmark inclusion configurable across all functions
3. **Database Storage**: Consider SQLite for better historical data management
4. **Additional Metrics**: Add beta, alpha, correlation analysis
5. **Portfolio Optimization**: Add Markowitz portfolio optimization
6. **Sector Rotation**: Add sector momentum analysis
7. **Technical Indicators**: Add RSI, MACD, moving averages
8. **Alert System**: Email/notification for significant price movements
9. **API Rate Limiting**: Implement more sophisticated rate limiting
10. **Caching**: Add caching layer to reduce API calls

---

## Notes for Future Claude Sessions

### Context for AI Assistants:

1. **Project Purpose**: Personal finance tool for stock analysis and portfolio tracking
2. **User Level**: Assumes intermediate Python knowledge
3. **Use Case**: Daily monitoring and historical analysis
4. **Data Source**: Yahoo Finance (free tier, no API key required)
5. **Environment**: Jupyter notebooks preferred for interactive analysis

### Code Modification Principles:

- **Preserve backward compatibility** with existing notebooks
- **Maintain function signatures** unless explicitly requested to change
- **Test with real data** before committing
- **Document all changes** in this CLAUDE.md file
- **Update README.md** if user-facing functionality changes

### Common User Requests:

1. Adding new tickers to watchlist
2. Adjusting time periods for analysis
3. Adding new performance metrics
4. Customizing visualizations
5. Exporting data in different formats

---

## Commit History Summary

Recent commits (oldest to newest):

- Multiple "Update functions.py" commits - Iterative development
- `850d385` - Update imports.py
- `e11d328` - **Polish stock reporting code and add daily download notebook**
  - Added comprehensive docstrings
  - Created daily_download.ipynb
  - Created example_analysis.ipynb
  - Added README.md
  - Fixed bug in download_and_plot_daily_pct_change()
  - Added generate_performance_summary() function

**Status:** Merged to main via PR #1

---

## Questions or Issues?

When encountering problems:

1. Check function docstrings for usage examples
2. Review [README.md](README.md) for comprehensive documentation
3. Check [example_analysis.ipynb](example_analysis.ipynb) for working examples
4. Verify Yahoo Finance API is accessible
5. Check for rate limiting issues (add time.sleep() if needed)

---

**End of CLAUDE.md**
