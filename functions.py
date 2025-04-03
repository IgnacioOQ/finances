from imports import *


def fetch_one_ticker(symbol,period="10y"):
    try:
        stock = yf.Ticker(symbol)
        hist = stock.history(period=period)

        if hist.empty:
            print("No historical price data available.")
            return None

        # Fetch static financial info
        info = stock.info
        shares_outstanding = info.get("sharesOutstanding", None)
        pb_ratio = info.get("priceToBook", None)
        peg_ratio = info.get("pegRatio", None)
        debt_to_equity = info.get("debtToEquity", None)
        ebitda = info.get("ebitda", None)
        eps = info.get("trailingEps", None)

        if shares_outstanding is None:
            print("Shares outstanding data not available.")
            return None

        # --- Calculate Market Cap History ---
        hist['Market_Cap'] = hist['Close'] * shares_outstanding

        # --- Approximate PE Ratio History ---
        if eps:
            hist['P/E_Ratio'] = hist['Close'] / eps
        else:
            hist['P/E_Ratio'] = None

        # --- Dividend Yield History ---
        dividends = stock.dividends
        if not dividends.empty:
            # Resample dividends to monthly sums
            dividends = dividends.resample('M').sum()
            # Resample prices to monthly close
            price_monthly = hist['Close'].resample('M').last()
            # Compute dividend yield per month
            dividend_yield = (dividends / price_monthly).fillna(0)
            # Forward-fill to align with daily index
            hist['Dividend_Yield'] = dividend_yield.reindex(hist.index, method='ffill').fillna(0)
        else:
            hist['Dividend_Yield'] = 0

        # --- Print Static Metrics with Explanations ---
        print(f"\nStatic Financial Metrics for {symbol}:\n")

        print(f"P/B Ratio: {pb_ratio}")
        print(" - Price-to-Book Ratio: Compares a company's market value to its book value. "
              "A lower P/B may indicate undervaluation relative to assets.\n")

        print(f"PEG Ratio: {peg_ratio}")
        print(" - Price/Earnings-to-Growth Ratio: Adjusts the P/E ratio by the company's earnings growth rate. "
              "Helps evaluate valuation relative to growth potential. A PEG < 1 may indicate undervaluation.\n")

        print(f"Debt to Equity: {debt_to_equity}")
        print(" - Debt to Equity Ratio: Measures the company’s financial leverage by comparing total liabilities to shareholders' equity. "
              "Higher values mean higher debt levels relative to equity.\n")

        print(f"EBITDA: {ebitda}")
        print(" - EBITDA (Earnings Before Interest, Taxes, Depreciation, and Amortization): "
              "A measure of core profitability, often used to compare profitability between companies.\n")

        # --- Plot Dynamic Metrics ---
        metrics_to_plot = {
            'Close': 'Stock Price',
            'Market_Cap': 'Market Capitalization',
            'P/E_Ratio': 'P/E Ratio (approx)',
            'Dividend_Yield': 'Dividend Yield'
        }

        plt.style.use('ggplot')
        for column, title in metrics_to_plot.items():
            plt.figure(figsize=(10, 5))
            plt.plot(hist.index, hist[column], label=title)
            plt.title(f"{symbol} - {title}")
            plt.xlabel('Date')
            plt.ylabel(title)
            plt.legend()
            plt.tight_layout()
            plt.show()

        # --- Return DataFrame with dynamic metrics ---
        return hist[['Close', 'Market_Cap', 'P/E_Ratio', 'Dividend_Yield']]

    except Exception as e:
        print(f"Error occurred: {e}")
        return None


def download_and_plot_stock_data(tickers, period='10y'):
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

def fetch_historical_stock_data(ticker_list, verbose=False):
    results = {}
    static_metrics = {}
    earnings_dict = {}
    revenue_dict = {}

    for symbol in tqdm(ticker_list):
        try:
            stock = yf.Ticker(symbol)
            hist = stock.history(period="15y")

            if hist.empty:
                print(f"No historical price data available for {symbol}.\n")
                continue

            info = stock.info
            shares_outstanding = info.get("sharesOutstanding", None)
            pb_ratio = info.get("priceToBook", None)
            peg_ratio = info.get("pegRatio", None)
            debt_to_equity = info.get("debtToEquity", None)
            ebitda = info.get("ebitda", None)
            eps = info.get("trailingEps", None)
            earnings = info.get("netIncomeToCommon", None)
            revenue = info.get("totalRevenue", None)

            if shares_outstanding is None or eps is None:
                print(f"Missing required data for {symbol}.\n")
                continue

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

            dividends = stock.dividends
            if not dividends.empty:
                dividends = dividends.resample('ME').sum()
                price_monthly = hist['Close'].resample('ME').last()
                dividend_yield = (dividends / price_monthly).fillna(0)
                hist['Dividend_Yield'] = dividend_yield.reindex(hist.index, method='ffill').fillna(0)
            else:
                hist['Dividend_Yield'] = 0

            hist_monthly = hist[['Close', 'Market_Cap', 'P/E_Ratio', 'Dividend_Yield']].resample('ME').last()
            results[symbol] = hist_monthly

        except Exception as e:
            print(f"Error processing {symbol}: {e}\n")
            continue

    if verbose:
        print("\n=========== Static Financial Metrics Summary ===========\n")
        for metric in ['P/B Ratio', 'PEG Ratio', 'Debt to Equity', 'EBITDA']:
            print(f"{metric}:")
            for symbol in static_metrics:
                print(f"  {symbol}: {static_metrics[symbol][metric]}")
            print()

        metrics_to_plot = {
            'Close': 'Stock Price',
            'Market_Cap': 'Market Capitalization',
            'P/E_Ratio': 'P/E Ratio (approx)',
            'Dividend_Yield': 'Dividend Yield'
        }

        plt.style.use('ggplot')
        for column, title in metrics_to_plot.items():
            plt.figure(figsize=(8, 4))
            for symbol in results.keys():
                df = results[symbol]
                plt.plot(df.index, df[column], label=symbol)
            plt.title(f"Comparison: {title}")
            plt.xlabel('Date')
            plt.ylabel(title)
            plt.legend()
            plt.tight_layout()
            plt.show()

    # --- Aggregate Weighted P/E Ratios ---
    all_data = []
    for symbol, df in results.items():
        temp = df[['P/E_Ratio', 'Market_Cap']].copy()
        temp['Symbol'] = symbol
        temp['Earnings'] = earnings_dict.get(symbol, 0)
        temp['Revenue'] = revenue_dict.get(symbol, 0)
        all_data.append(temp)
    combined = pd.concat(all_data)

    # Pivot for multi-column weighting
    pe = combined.pivot_table(index=combined.index, columns='Symbol', values='P/E_Ratio')
    mcap = combined.pivot_table(index=combined.index, columns='Symbol', values='Market_Cap')

    # Correctly shape static earnings and revenue into broadcastable DataFrames
    earnings_series = pd.Series(earnings_dict).reindex(pe.columns).fillna(0)
    revenue_series = pd.Series(revenue_dict).reindex(pe.columns).fillna(0)

    earnings_matrix = pd.DataFrame(
        [earnings_series.values] * len(pe.index),
        index=pe.index,
        columns=pe.columns
    )

    revenue_matrix = pd.DataFrame(
        [revenue_series.values] * len(pe.index),
        index=pe.index,
        columns=pe.columns
    )

    # Compute weighted P/E ratios
    weighted_pe_mcap = (pe * mcap).sum(axis=1) / mcap.sum(axis=1)
    weighted_pe_earnings = (pe * earnings_matrix).sum(axis=1) / earnings_matrix.sum(axis=1)
    weighted_pe_revenue = (pe * revenue_matrix).sum(axis=1) / revenue_matrix.sum(axis=1)

    # --- Plot all three weighted P/Es ---
    plt.figure(figsize=(8, 4))
    plt.plot(weighted_pe_mcap.index, weighted_pe_mcap, label='Market Cap Weighted P/E')
    plt.plot(weighted_pe_earnings.index, weighted_pe_earnings, label='Earnings Weighted P/E')
    plt.plot(weighted_pe_revenue.index, weighted_pe_revenue, label='Revenue Weighted P/E')
    plt.title("Weighted Average P/E Ratios")
    plt.xlabel("Date")
    plt.ylabel("Weighted P/E")
    plt.legend()
    plt.tight_layout()
    plt.show()

    return results
