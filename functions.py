from imports import *

def get_sp500_symbols():
    """
    Fetches the current list of S&P 500 companies from Wikipedia.

    Returns:
        pd.DataFrame: DataFrame with columns ['Symbol', 'Security', 'GICS Sector']
                      containing all S&P 500 companies
    """
    url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    table = pd.read_html(url)[0]
    return table[['Symbol', 'Security', 'GICS Sector']]

def fetch_one_ticker(symbol, period="10y"):
    """
    Fetches comprehensive financial data for a single ticker and generates visualizations.

    Downloads historical price data, calculates key financial metrics (Market Cap, P/E Ratio,
    Dividend Yield), and generates plots for each metric over time.

    Args:
        symbol (str): Stock ticker symbol (e.g., 'AAPL', 'MSFT')
        period (str): Time period for historical data (default: '10y')
                     Valid periods: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max

    Returns:
        pd.DataFrame: DataFrame with columns ['Adj_Close', 'Market_Cap', 'P/E_Ratio', 'Dividend_Yield']
                      or None if data cannot be retrieved

    Displays:
        - Static financial metrics (P/B, PEG, Debt/Equity, EBITDA)
        - Time series plots for price, market cap, P/E ratio, and dividend yield
    """
    try:
        stock = yf.Ticker(symbol)
        hist = stock.history(period=period)

        if hist.empty:
            print("No historical price data available.")
            return None

        # Use Adjusted Close when available, else fallback to Close
        if 'Adj Close' in hist.columns and not hist['Adj Close'].isna().all():
            hist['Adj_Close'] = hist['Adj Close']
            print(f"✅ Using Adjusted Close for {symbol}")
        else:
            hist['Adj_Close'] = hist['Close']
            print(f"⚠️ Adjusted Close not available, using Close for {symbol}")

        # --- Static Info ---
        info = stock.info
        shares_outstanding = info.get("sharesOutstanding", None)
        pb_ratio = info.get("priceToBook", None)
        peg_ratio = info.get("pegRatio", None)
        debt_to_equity = info.get("debtToEquity", None)
        ebitda = info.get("ebitda", None)
        eps = info.get("trailingEps", None)
        pe = info.get('trailingPE', None)

        if shares_outstanding is None:
            print("Shares outstanding data not available.")
            shares_outstanding = 1  # Avoid NaN in market cap calc

        # --- Market Cap using price * shares ---
        hist['Market_Cap'] = hist['Adj_Close'] * shares_outstanding

        # --- Approximate P/E Ratio using static EPS ---
        if eps and eps != 0:
            hist['P/E_Ratio'] = hist['Adj_Close'] / eps
        else:
            hist['P/E_Ratio'] = None

        # --- Dividend Yield from monthly dividend and price ---
        dividends = stock.dividends
        if not dividends.empty:
            dividends = dividends.resample('M').sum()
            price_monthly = hist['Adj_Close'].resample('M').last()
            dividend_yield = (dividends / price_monthly).fillna(0)
            hist['Dividend_Yield'] = dividend_yield.reindex(hist.index, method='ffill').fillna(0)
        else:
            hist['Dividend_Yield'] = 0

        # --- Print Static Info ---
        print(f"\nStatic Financial Metrics for {symbol}:\n")

        print(f"P/B Ratio: {pb_ratio}")
        print(" - Price-to-Book: Market value vs book value.\n")

        print(f"PEG Ratio: {peg_ratio}")
        print(" - PE / Earnings Growth: Value vs growth.\n")

        print(f"Debt to Equity: {debt_to_equity}")
        print(" - Leverage: Total liabilities vs shareholder equity.\n")

        print(f"EBITDA: {ebitda}")
        print(" - Core operating profit before financing & taxes.\n")

        # --- Plotting Metrics ---
        metrics_to_plot = {
            'Adj_Close': 'Adjusted Stock Price',
            'Market_Cap': 'Market Capitalization',
            'P/E_Ratio': 'P/E Ratio (approx)',
            'Dividend_Yield': 'Dividend Yield'
        }

        plt.style.use('ggplot')
        for column, title in metrics_to_plot.items():
            plt.figure(figsize=(10, 5))
            plt.plot(hist.index, hist[column], label=title, color='tab:blue')
            plt.title(f"{symbol} - {title}")
            plt.xlabel('Date')
            plt.ylabel(title)
            plt.legend()
            plt.tight_layout()
            plt.show()

        # --- Standalone P/E Plot with EPS Note ---
        if eps:
            plt.figure(figsize=(10, 5))
            plt.plot(hist.index, hist['P/E_Ratio'], color='tab:orange')
            plt.title(f"{symbol} - Historic P/E Ratio (based on static trailing EPS = {eps:.2f})")
            plt.xlabel("Date")
            plt.ylabel("P/E Ratio (approx)")
            plt.grid(True)
            plt.tight_layout()
            plt.show()

        return hist[['Adj_Close', 'Market_Cap', 'P/E_Ratio', 'Dividend_Yield']]

    except Exception as e:
        print(f"❌ Error occurred: {e}")
        return None

def download_and_plot_stock_data(tickers, period='10y'):
    """
    Downloads and plots normalized stock performance for multiple tickers.

    Automatically includes VOO and RSP (S&P 500 benchmarks) for comparison.
    Normalizes all prices to start at 1.0 for easy performance comparison.

    Args:
        tickers (list): List of ticker symbols to analyze
        period (str): Time period for historical data (default: '10y')

    Returns:
        pd.DataFrame: Normalized prices for all tickers (starting value = 1.0)

    Displays:
        - Line plot showing normalized price performance over time
    """
    tickers = list(set(tickers + ['VOO', 'RSP']))  # Ensure SPY and RSP are included and avoid duplicates

    # Download data using Yahoo Finance
    data = yf.download(tickers, period=period, auto_adjust=False)
    # all_data = []
    # for ticker in tickers:
    #     # print(f"Downloading {ticker}...")
    #     df = yf.download(ticker, period=period, auto_adjust=False)
    #     # add ticker to column names to match multiindex style
    #     df.columns = pd.MultiIndex.from_product([[ticker], df.columns])
    #     all_data.append(df)
    #     time.sleep(0.5)
        
    # Prefer 'Adj Close' over 'Close'
    if 'Adj Close' in data:
        prices = data['Adj Close']
    elif 'Close' in data:
        print("Warning: 'Adj Close' not found. Using 'Close' instead.")
        prices = data['Close']
    else:
        raise ValueError("Neither 'Adj Close' nor 'Close' found in the downloaded data.")

    # Normalize prices
    normalized_prices = (prices / prices.iloc[0]).dropna()

    # Plotting
    plt.figure(figsize=(8, 4))
    for column in normalized_prices.columns:
        plt.plot(normalized_prices.index, normalized_prices[column], label=column)

    plt.xlabel('Date')
    plt.ylabel('Normalized Price')
    plt.title(f'Stock Performance (Normalized) — Period: {period}')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

    return normalized_prices


def download_and_plot_daily_pct_change(tickers, period='10y'):
    """
    Downloads stock data and plots daily percentage changes for given tickers.

    Args:
        tickers (list): List of ticker symbols to download
        period (str): Time period for historical data (default: '10y')

    Returns:
        pd.DataFrame: DataFrame containing daily percentage changes for all tickers
    """
    tickers = list(set(tickers + ['SPY', 'RSP']))  # Ensure SPY and RSP are included and avoid duplicates

    # Download data using Yahoo Finance
    data = yf.download(tickers, period=period, auto_adjust=False)

    # Prefer 'Adj Close' over 'Close'
    if 'Adj Close' in data:
        prices = data['Adj Close']
    elif 'Close' in data:
        print("Warning: 'Adj Close' not found. Using 'Close' instead.")
        prices = data['Close']
    else:
        raise ValueError("Neither 'Adj Close' nor 'Close' found in the downloaded data.")

    # Calculate daily percent change
    pct_change = prices.pct_change().dropna() * 100  # Convert to percentage

    # Plotting
    plt.figure(figsize=(10, 5))
    for column in pct_change.columns:
        plt.plot(pct_change.index, pct_change[column], label=column, alpha=0.7)

    plt.xlabel('Date')
    plt.ylabel('Daily % Change')
    plt.title(f'Daily Percentage Change — Period: {period}')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

    return pct_change



def fetch_historical_stock_data(ticker_list, period='5Y', verbose=False):
    """
    Fetches comprehensive historical data for multiple stocks with advanced analytics.

    Downloads monthly historical data, calculates valuation metrics, and computes
    portfolio-level weighted averages. Generates weighted P/E ratio time series.

    Args:
        ticker_list (list): List of ticker symbols to analyze
        period (str): Time period for historical data (default: '5Y')
        verbose (bool): If True, prints detailed static metrics summary

    Returns:
        dict: Dictionary mapping symbols to DataFrames with monthly metrics
              Each DataFrame contains: Close, Market_Cap, P/E_Ratio, Dividend_Yield
              (ETFs only include Close and Dividend_Yield)

    Displays:
        - Metric explanations
        - Weighted static metrics (P/B, PEG, Debt/Equity, EBITDA)
        - Weighted P/E ratio time series plot
    """
    results = {}
    static_metrics = {}
    earnings_dict = {}
    revenue_dict = {}

    for symbol in tqdm(ticker_list):
        time.sleep(0.5)
        try:
            stock = yf.Ticker(symbol)
            hist = stock.history(period=period)

            if hist.empty:
                print(f"No historical price data available for {symbol}.\n")
                continue

            try:
                info = stock.info
            except Exception as e:
                print(f"Could not fetch info for {symbol}: {e}")
                continue

            quote_type = info.get("quoteType", "").upper()
            is_etf = (quote_type == "ETF")

            shares_outstanding = info.get("sharesOutstanding", None)
            pb_ratio = info.get("priceToBook", None)
            peg_ratio = info.get("pegRatio", None)
            debt_to_equity = info.get("debtToEquity", None)
            ebitda = info.get("ebitda", None)
            eps = info.get("trailingEps", None)
            earnings = info.get("netIncomeToCommon", None)
            revenue = info.get("totalRevenue", None)

            # Dividends
            dividends = stock.dividends
            if not dividends.empty:
                dividends = dividends.resample('ME').sum()
                price_monthly = hist['Close'].resample('ME').last()
                dividend_yield = (dividends / price_monthly).fillna(0)
                hist['Dividend_Yield'] = dividend_yield.reindex(hist.index, method='ffill').fillna(0)
            else:
                hist['Dividend_Yield'] = 0

            # ETF or missing valuation data
            if is_etf or shares_outstanding is None or eps is None:
                if verbose:
                    print(f"Skipping valuation metrics for {symbol} (ETF or missing data).")
                hist_monthly = hist[['Close', 'Dividend_Yield']].resample('ME').last()
                results[symbol] = hist_monthly
                continue

            # Proceed with valuation metrics for stocks
            static_metrics[symbol] = {
                'P/B Ratio': pb_ratio,
                'PEG Ratio': peg_ratio,
                'Debt to Equity': debt_to_equity,
                'EBITDA': ebitda
            }

            earnings_dict[symbol] = earnings if earnings else 0
            revenue_dict[symbol] = revenue if revenue else 0

            hist['Market_Cap'] = hist['Close'] * shares_outstanding
            hist['P/E_Ratio'] = hist['Close'] / eps if eps else None

            hist_monthly = hist[['Close', 'Market_Cap', 'P/E_Ratio', 'Dividend_Yield']].resample('ME').last()
            results[symbol] = hist_monthly

        except Exception as e:
            print(f"Error processing {symbol}: {e}\n")
            continue

    # Verbose Static Summary
    if verbose and static_metrics:
        print("\n=========== Static Financial Metrics Summary ===========\n")
        for metric in ['P/B Ratio', 'PEG Ratio', 'Debt to Equity', 'EBITDA']:
            print(f"{metric}:")
            for symbol in static_metrics:
                print(f"  {symbol}: {static_metrics[symbol][metric]}")
            print()

    # Create static dataframe
    symbols = list(static_metrics.keys())
    static_df = pd.DataFrame.from_dict(static_metrics, orient='index').reindex(symbols)
    static_df['Earnings'] = pd.Series(earnings_dict).reindex(symbols).fillna(0)
    static_df['Revenue'] = pd.Series(revenue_dict).reindex(symbols).fillna(0)

    market_caps = {
        symbol: results[symbol]['Market_Cap'].iloc[-1] if 'Market_Cap' in results[symbol].columns else 0
        for symbol in symbols
    }
    static_df['Market_Cap'] = pd.Series(market_caps)

    # Weighted averages
    def compute_weighted_avg(df, metric, weight):
        valid = df[[metric, weight]].dropna()
        return (valid[metric] * valid[weight]).sum() / valid[weight].sum() if valid[weight].sum() != 0 else None

    weighted_metrics = {
        'P/B Ratio': {},
        'PEG Ratio': {},
        'Debt to Equity': {},
        'EBITDA': {}
    }

    for metric in weighted_metrics.keys():
        weighted_metrics[metric]['Market Cap'] = compute_weighted_avg(static_df, metric, 'Market_Cap')
        weighted_metrics[metric]['Earnings'] = compute_weighted_avg(static_df, metric, 'Earnings')
        weighted_metrics[metric]['Revenue'] = compute_weighted_avg(static_df, metric, 'Revenue')

    # Print metric explanations and results
    print("\n=========== Metric Explanations ===========\n")
    print("• P/B Ratio (Price-to-Book): Compares a company’s market value to its book value. Lower values may indicate undervaluation.")
    print("• PEG Ratio (Price/Earnings to Growth): Adjusts the P/E ratio by expected earnings growth. A PEG ~1 is considered fairly valued.")
    print("• Debt to Equity: Measures leverage — how much debt a company uses to finance its assets relative to equity.")
    print("• EBITDA: Earnings before interest, taxes, depreciation, and amortization — used to analyze operating performance.\n")

    print("\n=========== Weighted Static Metrics ===========\n")
    for metric, weights in weighted_metrics.items():
        print(f"{metric}:")
        for by, value in weights.items():
            print(f"  Weighted by {by}: {value}")
        print()

    # Weighted P/E Ratio Time Series
    all_data = []
    for symbol, df in results.items():
        if 'P/E_Ratio' in df.columns and 'Market_Cap' in df.columns:
            temp = df[['P/E_Ratio', 'Market_Cap']].copy()
            temp['Symbol'] = symbol
            temp['Earnings'] = earnings_dict.get(symbol, 0)
            temp['Revenue'] = revenue_dict.get(symbol, 0)
            all_data.append(temp)

    if all_data:
        combined = pd.concat(all_data)
        pe = combined.pivot_table(index=combined.index, columns='Symbol', values='P/E_Ratio')
        mcap = combined.pivot_table(index=combined.index, columns='Symbol', values='Market_Cap')

        earnings_series = pd.Series(earnings_dict).reindex(pe.columns).fillna(0)
        revenue_series = pd.Series(revenue_dict).reindex(pe.columns).fillna(0)

        earnings_matrix = pd.DataFrame([earnings_series.values] * len(pe), index=pe.index, columns=pe.columns)
        revenue_matrix = pd.DataFrame([revenue_series.values] * len(pe), index=pe.index, columns=pe.columns)

        weighted_pe_mcap = (pe * mcap).sum(axis=1) / mcap.sum(axis=1)
        weighted_pe_earnings = (pe * earnings_matrix).sum(axis=1) / earnings_matrix.sum(axis=1)
        weighted_pe_revenue = (pe * revenue_matrix).sum(axis=1) / revenue_matrix.sum(axis=1)

        plt.figure(figsize=(8, 4))
        plt.plot(weighted_pe_mcap.index, weighted_pe_mcap, label='Market Cap Weighted P/E')
        plt.plot(weighted_pe_earnings.index, weighted_pe_earnings, label='Earnings Weighted P/E')
        plt.plot(weighted_pe_revenue.index, weighted_pe_revenue, label='Revenue Weighted P/E')
        plt.title("Weighted Average P/E Ratios Over Time")
        plt.xlabel("Date")
        plt.ylabel("P/E Ratio")
        plt.legend()
        plt.tight_layout()
        plt.show()

    return results

def generate_performance_summary(tickers, period='1y', benchmark='SPY'):
    """
    Generates a comprehensive performance summary report for multiple stocks.

    Calculates key performance metrics including returns, volatility, Sharpe ratio,
    max drawdown, and relative performance vs. benchmark.

    Args:
        tickers (list): List of ticker symbols to analyze
        period (str): Time period for analysis (default: '1y')
        benchmark (str): Benchmark ticker for comparison (default: 'SPY')

    Returns:
        pd.DataFrame: Summary table with performance metrics for each ticker

    Metrics included:
        - Total Return (%): Total percentage return over the period
        - Annualized Return (%): Annualized return
        - Volatility (%): Annualized volatility (standard deviation of returns)
        - Sharpe Ratio: Risk-adjusted return (assuming 0% risk-free rate)
        - Max Drawdown (%): Maximum peak-to-trough decline
        - Current Price: Latest closing price
        - vs Benchmark (%): Outperformance vs benchmark
    """
    # Include benchmark if not already in list
    all_tickers = list(set(tickers + [benchmark]))

    # Download data
    data = yf.download(all_tickers, period=period, auto_adjust=False, progress=False)

    # Use Adj Close if available
    if 'Adj Close' in data:
        prices = data['Adj Close']
    else:
        prices = data['Close']

    # Handle single ticker case
    if len(all_tickers) == 1:
        prices = pd.DataFrame(prices)
        prices.columns = all_tickers

    # Calculate metrics
    summary = {}

    for ticker in all_tickers:
        ticker_prices = prices[ticker].dropna()

        if len(ticker_prices) < 2:
            continue

        # Returns
        total_return = (ticker_prices.iloc[-1] / ticker_prices.iloc[0] - 1) * 100
        daily_returns = ticker_prices.pct_change().dropna()

        # Annualized metrics
        trading_days = len(ticker_prices)
        years = trading_days / 252  # Approximate trading days per year
        annualized_return = ((1 + total_return/100) ** (1/years) - 1) * 100 if years > 0 else 0
        volatility = daily_returns.std() * (252 ** 0.5) * 100  # Annualized volatility

        # Sharpe Ratio (assuming 0% risk-free rate)
        sharpe = (annualized_return / volatility) if volatility > 0 else 0

        # Max Drawdown
        cumulative = (1 + daily_returns).cumprod()
        running_max = cumulative.cummax()
        drawdown = (cumulative - running_max) / running_max * 100
        max_drawdown = drawdown.min()

        # Current price
        current_price = ticker_prices.iloc[-1]

        summary[ticker] = {
            'Total Return (%)': round(total_return, 2),
            'Annualized Return (%)': round(annualized_return, 2),
            'Volatility (%)': round(volatility, 2),
            'Sharpe Ratio': round(sharpe, 2),
            'Max Drawdown (%)': round(max_drawdown, 2),
            'Current Price': round(current_price, 2)
        }

    # Create DataFrame
    summary_df = pd.DataFrame(summary).T

    # Add vs Benchmark column
    if benchmark in summary_df.index:
        benchmark_return = summary_df.loc[benchmark, 'Total Return (%)']
        summary_df['vs Benchmark (%)'] = summary_df['Total Return (%)'] - benchmark_return
        summary_df['vs Benchmark (%)'] = summary_df['vs Benchmark (%)'].round(2)

    # Sort by total return
    summary_df = summary_df.sort_values('Total Return (%)', ascending=False)

    print(f"\n{'='*80}")
    print(f"PERFORMANCE SUMMARY - {period.upper()}")
    print(f"{'='*80}\n")
    print(summary_df.to_string())
    print(f"\n{'='*80}\n")

    return summary_df


def get_etfdb_pe_ratio(symbol):
    """
    Scrapes P/E ratio data for ETFs from etfdb.com.

    Useful for obtaining P/E ratios for ETFs, which are not always available
    through standard financial APIs.

    Args:
        symbol (str): ETF ticker symbol (e.g., 'VOO', 'SPY')

    Returns:
        float: P/E ratio of the ETF, or None if not found

    Note:
        Requires internet connection and may be affected by website structure changes.
    """
    try:
        url = f"https://etfdb.com/etf/{symbol.upper()}/"
        headers = {"User-Agent": "Mozilla/5.0"}
        resp = requests.get(url, headers=headers)
        resp.raise_for_status()

        soup = BeautifulSoup(resp.text, 'html.parser')
        pe_ratio = None

        # ETFdb displays P/E in a "Valuation" section; it appears in table rows labeled "P/E Ratio"
        for row in soup.find_all('tr'):
            header = row.find('th')
            value = row.find('td')
            if header and value:
                header_text = header.get_text(strip=True)
                if 'P/E Ratio' in header_text:
                    try:
                        pe_ratio = float(value.get_text(strip=True).replace(',', ''))
                        print(f"✅ Fetched P/E for {symbol.upper()} from ETFdb: {pe_ratio}")
                    except ValueError:
                        pass
                    break

        if pe_ratio is None:
            print(f"⚠️ Could not find P/E ratio for {symbol.upper()} on ETFdb.")
        return pe_ratio

    except Exception as e:
        print(f"❌ Error fetching from ETFdb: {e}")
        return None

