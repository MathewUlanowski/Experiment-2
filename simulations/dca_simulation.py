import logging  # Import logging for exception handling
from models.account import Account
from data_fetchers.getYFinanceData import fetch_data
from utils.date_utils import pad_historical_prices
import datetime  # Import the datetime module
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
        start_date: datetime = params["start_date"].strftime("%Y-%m-%d") if isinstance(params["start_date"], (datetime.date, datetime.datetime)) else params["start_date"]
        end_date: datetime = params["end_date"].strftime("%Y-%m-%d") if isinstance(params["end_date"], (datetime.date, datetime.datetime)) else params["end_date"]
        initial_investment = int(params["initial_investment"])
        monthly_investment = int(params["monthly_investment"])
        tickers: list[str] = params["tickers"].split(",") if isinstance(params["tickers"], str) else params["tickers"]

        accounts = []  # List to store accounts for each ticker

        for ticker in tickers:
            # Fetch historical data and pad it to match the simulation period
            historical_data = fetch_data(tickers=[ticker], period="max")
            padded_prices = pad_historical_prices(historical_data[ticker], start_date, end_date)

            # Extract company name from the historical data or query for it
            company_name = historical_data.get("company_name")
            if not company_name:
                company_name = get_company_name(ticker)  # Query for the company name if not available

            # Initialize the account with the initial investment and name
            account_name = f"(DCA) {ticker} - {company_name}"
            account = Account(initial_balance=initial_investment, name=account_name)

            # Track the last month to ensure monthly investments are added only once per month
            last_month = None

            # Iterate through the padded prices to simulate DCA
            for i in range(1, len(padded_prices)):
                # Extract the current date and month
                current_date = padded_prices[i]['Date']
                current_month = datetime.datetime.strptime(current_date, "%Y-%m-%d").month

                # Calculate the rate change from the last month's price
                previous_price = padded_prices[i - 1]['Close']
                current_price = padded_prices[i]['Close']
                rate_change = (current_price / previous_price - 1) if previous_price > 0 else 0

                # Adjust the current balance by the rate change
                account.balance *= (1 + rate_change)

                # Add the monthly investment only if the month has changed
                if current_month != last_month:
                    account.add_funds(monthly_investment)
                    last_month = current_month

                # Credit the balance to the account for the current day
                account.record_balance(datetime.datetime.strptime(current_date, "%Y-%m-%d"), account.balance)

            # Add the account for this ticker to the list
            accounts.append(account)

        return accounts  # Return a list of accounts, one for each ticker
    except Exception as e:
        logging.error(f"Error in run_dca_simulation: {e}", exc_info=True)  # Log the exception with stack trace
        raise
