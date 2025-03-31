import logging

from matplotlib.dates import relativedelta  # Import logging for exception handling
from models.account import Account
from data_fetchers.getYFinanceData import fetch_data
from utils.date_utils import pad_historical_prices
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

        for ticker in tickers:
            historical_data = fetch_data(tickers=[ticker], period="max")

            # Extract company name from the historical data or query for it
            company_name = historical_data.get("company_name")
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
                        if data['Date'] == current_date.strftime("%Y-%m-%d"):
                            current_price = data.get('Close')
                            break
                    logging.info(f"Current price for {ticker} on {current_date}: {current_price}")

                current_date += relativedelta(days=1)


            # # Iterate through the padded prices to simulate DCA
            # for i in range(len(padded_prices)):
            #     # Extract the current date and check if it's a trade day
            #     current_date = padded_prices[i]['Date']
            #     current_price = padded_prices[i].get('Close')

            #     if current_price is None:  # Skip non-trade days
            #         continue

            #     # Calculate the current month
            #     current_month = datetime.strptime(current_date, "%Y-%m-%d").month

            #     # Add the monthly investment only if the month has changed
            #     if current_month != last_month:
            #         cash_balance += monthly_investment
            #         last_month = current_month

            #     # Calculate the number of shares to buy with the cash balance
            #     shares_to_buy = cash_balance // current_price
            #     invested_balance += shares_to_buy * current_price
            #     cash_balance -= shares_to_buy * current_price

            #     # Credit the total balance (cash + invested) to the account for the current day
            #     total_balance = cash_balance + invested_balance
            #     account.record_balance(current_date, total_balance)

            # # Add the account for this ticker to the list
            # accounts.append(account)

        return accounts  # Return a list of accounts, one for each ticker
    except Exception as e:
        logging.error(f"Error in run_dca_simulation: {e}", exc_info=True)  # Log the exception with stack trace
        raise
