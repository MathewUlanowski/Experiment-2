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

    # Create the account with the name "Saving"
    account = Account(start_date,initial_balance=initial_investment, name="Saving")
    current_date: datetime = start_date

    while current_date <= end_date:
        if current_date.day == 1:
            account.record_balance(current_date, account.balance + monthly_investment)  # Record balance before adding funds
        current_date += relativedelta(days=1)

    return [account]
