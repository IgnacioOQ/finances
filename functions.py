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
