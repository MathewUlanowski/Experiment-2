import logging

from matplotlib.dates import relativedelta  # Import logging for exception handling
from models.account import Account
from data_fetchers.getYFinanceData import fetch_data
from services.cache_service import cache_response, get_cached_response
from utils.date_utils import pad_historical_prices
import hashlib
from datetime import datetime, date # Import the datetime module
from services.company_service import get_company_name  # Import a service to fetch company names

# Update logging configuration to include file and line number
logging.basicConfig(
    level=logging.ERROR,
    format="%(asctime)s - %(levelname)s - %(message)s [%(filename)s:%(lineno)d]"
)

def run_dca_simulation(params):
    """
    Simulates Dollar-Cost Averaging (DCA) using historical stock data.

    :param params: A dictionary containing simulation parameters:
                   - start_date: Start date of the simulation.
                   - end_date: End date of the simulation.
                   - initial_investment: Initial investment amount.
                   - monthly_investment: Monthly investment amount.
                   - tickers: List of stock tickers to simulate.
    :return: A list of Account objects, one for each ticker.
    """
    try:
        start_date: datetime = datetime.strptime(params["start_date"], "%Y-%m-%d")
        end_date: datetime = datetime.strptime(params["end_date"], "%Y-%m-%d")
        initial_investment = int(params["initial_investment"])
        monthly_investment = int(params["monthly_investment"])
        tickers: list[str] = params["tickers"].split(",") if isinstance(params["tickers"], str) else params["tickers"]

        accounts = []  # List to store accounts for each ticker

        shares = 0
        for ticker in tickers:
            # hash the ticker and the params to create a unique cache key
            ticker_hash = hashlib.sha256(f"{ticker},{start_date},{end_date},{initial_investment},{monthly_investment}".encode()).hexdigest()

            # look for a cache for the specific ticker
            ticker_cache = get_cached_response(f"dca_sim-{ticker_hash}")
            if ticker_cache:
                logging.info(f"Returning cached response for {ticker}. (dca_sim-{ticker_hash})")
                accounts.append(ticker_cache)
                continue

            historical_datas = fetch_data(tickers=[ticker], period="max")
            historical_data = historical_datas[ticker]

            # Extract company name from the historical data or query for it
            company_name = historical_datas.get("company_name")
            if not company_name:
                company_name = get_company_name(ticker)  # Query for the company name if not available

            # Initialize the account with the initial investment and name
            account_name = f"(DCA) {ticker} - {company_name}"
            account = Account(start_date, initial_balance=initial_investment, name=account_name)

            cash_account = Account(start_date, initial_balance=initial_investment, name=f"Cash Account - {ticker}")
            investment_account = Account(start_date, initial_balance=0, name=f"Investment Account - {ticker}")


            current_date = start_date
            while current_date <= end_date:

                if current_date.day == 1:
                    cash_account.record_balance(current_date, cash_account.balance + monthly_investment)

                if cash_account.balance > 0:
                    # find the close price for the current date in historical data
                    current_price = None
                    for data in historical_data:
                        # logging.info(f"Checking data for {ticker} on {current_date}: {data["Close"]}")
                        if data['Date'] == current_date.strftime("%Y-%m-%d"):
                            current_price = data.get('Close')
                            break
                    # if current price is not none log how many shares we can buy
                    if current_price is not None and cash_account.balance // current_price > 0:
                        pass
                        # buy shares 
                        shares += cash_account.balance // current_price
                        cash_account.deduct_funds(current_date,cash_account.balance // current_price * current_price)
                        investment_account.record_balance(current_date, shares * current_price)

                if(current_date.day == 1):
                    # Record the balance for the investment account
                    account.balance_history.append({
                        "date": current_date.strftime("%Y-%m-%d"),
                        "account_balance": investment_account.balance + cash_account.balance,
                        "shares": shares,
                        "price": current_price,
                    })
                current_date += relativedelta(days=1)
            accounts.append(account)

            # Cache the account for the specific ticker
            cache_response(f"dca_sim-{ticker_hash}", account)

        return accounts  # Return a list of accounts, one for each ticker
    except Exception as e:
        logging.error(f"Error in run_dca_simulation: {e}", exc_info=True)  # Log the exception with stack trace
        raise
