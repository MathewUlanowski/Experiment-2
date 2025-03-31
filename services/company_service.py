import yfinance as yf

def get_company_name(ticker):
    """
    Fetches the full company name for a given stock ticker using the yfinance library.

    :param ticker: The stock ticker symbol.
    :return: The full company name as a string.
    """
    try:
        stock = yf.Ticker(ticker)
        company_name = stock.info.get("longName", "Unknown Company")
        return company_name
    except Exception as e:
        # Log the error and return a default value
        print(f"Error fetching company name for ticker '{ticker}': {e}")
        return "Unknown Company"
