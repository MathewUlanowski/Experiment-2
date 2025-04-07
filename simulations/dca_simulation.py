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
        initial_investment = int(str(params["initial_investment"].replace(",", "")))
        monthly_investment = int(str(params["monthly_investment"].replace(",", "")))
        tickers: list[str] = params["tickers"].split(",") if isinstance(params["tickers"], str) else params["tickers"]

        accounts = []  # List to store accounts for each ticker

        for ticker in tickers:
            # hash the ticker and the params to create a unique cache key
            ticker_hash = hashlib.sha256(f"{ticker},{start_date},{end_date},{initial_investment},{monthly_investment}".encode()).hexdigest()

            # look for a cache for the specific ticker
            ticker_cache = get_cached_response(f"dca_sim-{ticker_hash}")
            if ticker_cache:
                logging.info(f"Returning cached response for {ticker}. (dca_sim-{ticker_hash})")
                accounts.append(ticker_cache)
                continue

            # Validate the response from fetch_data
            historical_datas = fetch_data(tickers=[ticker], period="max")
            if not historical_datas or ticker not in historical_datas:
                logging.error(f"Invalid or empty response from fetch_data for ticker: {ticker}")
                continue  # Skip this ticker and move to the next one

            historical_data = historical_datas[ticker]

            # Preprocess historical data into a dictionary for fast lookups
            historical_data_dict = {data['Date']: data['Close'] for data in historical_data}

            # Validate the company name
            company_name = historical_datas.get("company_name")
            if not company_name:
                try:
                    company_name = get_company_name(ticker)
                except Exception as e:
                    logging.error(f"Failed to fetch company name for ticker {ticker}: {e}")
                    company_name = "Unknown Company"

            # Initialize the account with the initial investment and name
            account_name = f"(DCA) {ticker} - {company_name}"
            account = Account(start_date, initial_balance=initial_investment, name=account_name)

            cash_account = Account(start_date, initial_balance=initial_investment, name=f"Cash Account - {ticker}")
            investment_account = Account(start_date, initial_balance=0, name=f"Investment Account - {ticker}")

            current_date = start_date
            shares = 0

            balance_histories = [{
                "date": current_date.strftime("%Y-%m-%d"),
                "account_balance": cash_account.balance,
                "shares": shares,
                "price": 0,
                "cash": cash_account.balance,
                "investment_value": investment_account.balance,
            }]

            while current_date <= end_date:

                if current_date.day == 1:
                    cash_account.record_balance(current_date, cash_account.balance + monthly_investment)

                if cash_account.balance > 0:
                    # Find the close price for the current date in historical data dictionary
                    current_price = historical_data_dict.get(current_date.strftime("%Y-%m-%d"))

                    # If current price is valid, calculate shares to buy
                    if current_price is not None and cash_account.balance // current_price > 0:
                        shares_to_buy = cash_account.balance // current_price
                        shares += shares_to_buy
                        cash_account.deduct_funds(current_date, shares_to_buy * current_price)
                        investment_account.record_balance(current_date, shares * current_price)

                # Record the balance for the investment account
                if current_date.day == 1:
                    # If the current price is 0, find the last price that was not 0
                    if current_price is None or current_price == 0:
                        last_valid_price = None
                        temp_date = current_date
                        while last_valid_price is None and temp_date > start_date:
                            temp_date -= relativedelta(days=1)
                            last_valid_price = historical_data_dict.get(temp_date.strftime("%Y-%m-%d"))
                            if last_valid_price == 0:
                                last_valid_price = None
                        current_price = last_valid_price if last_valid_price is not None else 0

                    balance_histories.append({
                        "date": current_date.strftime("%Y-%m-%d"),
                        "account_balance": investment_account.balance + cash_account.balance,
                        "shares": shares,
                        "price": current_price,
                        "cash": cash_account.balance,
                        "investment_value": investment_account.balance
                    })

                current_date += relativedelta(days=1)
            account.balance_history = balance_histories
            accounts.append(account)

            # Cache the account for the specific ticker
            try:
                cache_response(f"dca_sim-{ticker_hash}", account)
            except Exception as e:
                logging.error(f"Failed to cache response for ticker {ticker}: {e}")

        return accounts  # Return a list of accounts, one for each ticker
    except Exception as e:
        logging.error(f"Error in run_dca_simulation: {e}", exc_info=True)  # Log the exception with stack trace
        raise
