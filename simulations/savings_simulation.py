import logging
from models.account import Account
from dateutil.relativedelta import relativedelta
from datetime import date, datetime


def run_savings_simulation(params):
    """
    Simulates a savings account where money is periodically added.

    :param params: A dictionary containing simulation parameters:
                   - start_date: Start date of the simulation.
                   - end_date: End date of the simulation.
                   - initial_investment: Initial investment amount.
                   - monthly_investment: Monthly investment amount.
    :return: A list containing a single Account object representing the savings simulation results.
    """
    # Derive start_date and end_date as datetime objects
    start_date: datetime = datetime.strptime(params["start_date"], "%Y-%m-%d")
    end_date: datetime = datetime.strptime(params["end_date"], "%Y-%m-%d")
    initial_investment = int(params["initial_investment"])
    monthly_investment = int(params["monthly_investment"])

    # Log as date objects for consistency
    logging.info(f"Running savings simulation from {start_date.date()} to {end_date.date()}")
    logging.info(f"Initial investment: {initial_investment}, Monthly investment: {monthly_investment}")

    # Create the account with the name "Saving"
    account = Account(initial_balance=initial_investment, name="Saving")
    current_date: datetime = start_date

    while current_date <= end_date:
        if current_date.day == 1:
            logging.info(f"Adding monthly investment of {monthly_investment} on {current_date.strftime('%Y-%m-%d')}")
            account.balance_history.append({
                "date": current_date.strftime("%Y-%m-%d"),
                "cash": account.balance,
                "account_balance": account.balance + monthly_investment
            })
        current_date += relativedelta(days=1)

    return [account]
