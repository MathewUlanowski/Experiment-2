from datetime import date, datetime
import logging
import math

from models.account import Account
from models.bond import Bond
from data_fetchers.getFREDData import fetch_bond_rates
from dateutil.relativedelta import relativedelta

logging.basicConfig(
    level=logging.ERROR,
    format="%(asctime)s - %(levelname)s - %(message)s [%(filename)s:%(lineno)d]"
)

def run_bond_simulation(params):
    """
    Simulates investing in bonds with monthly investments and reinvestment upon maturity.

    :param params: A dictionary containing simulation parameters:
                   - start_date: Start date of the simulation.
                   - end_date: End date of the simulation.
                   - initial_investment: Initial investment amount.
                   - monthly_investment: Monthly investment amount.
    :return: A list containing a single Account object representing the bond simulation results.
    """
    try:
        # Derive start_date and end_date as datetime objects
        start_date: datetime = datetime.strptime(params["start_date"], "%Y-%m-%d")
        end_date: datetime = datetime.strptime(params["end_date"], "%Y-%m-%d")
        # Convert to date objects for fetch_bond_rates
        start_date_for_fetch = start_date.date()
        end_date_for_fetch = end_date.date()
        initial_investment = int(params["initial_investment"].replace("$", "").replace(",", ""))
        monthly_investment = int(params["monthly_investment"].replace("$", "").replace(",", ""))

        # Initialize accounts and variables
        bond_account = Account(start_date,name="Bond Account")
        current_date = start_date
        pending_cash = initial_investment + monthly_investment  # Include initial investment in pending cash
        bonds = []

        # Fetch bond rates for the simulation period
        from dotenv import load_dotenv
        import os
        load_dotenv(dotenv_path="./secrets.env")
        fred_api_key = os.getenv("FRED_API_KEY")
        bond_rates = fetch_bond_rates(fred_api_key, start_date=start_date_for_fetch, end_date=end_date_for_fetch)
        bond_rate_dict = {rate["date"]: rate["rate"] for rate in bond_rates}

        # Record initial balance
        balance_history = [{
            "date": current_date.strftime("%Y-%m-%d"),
            "cash": pending_cash,
            "bonds": 0.0,
            "account_balance": pending_cash,  # Add total balance
            "interest_rate": 0.0  # Initial interest rate
        }]

        while current_date <= end_date:
            # Format the current date to match the bond rate data format
            current_date_str = current_date.strftime("%Y-%m-%d 00:00:00")

            # Get the annual yield for the current date
            annual_yield = bond_rate_dict.get(current_date_str, 0.0)

            # Maturing bonds
            for bond in bonds[:]:
                if bond.is_matured(current_date):
                    # Cash in the bond on its maturity date
                    matured_value = bond.get_matured_value()
                    pending_cash += matured_value
                    pending_cash = math.floor(pending_cash * 100) / 100  # Floor to the nearest cent
                    bonds.remove(bond)

            # Purchase bonds in $100 increments
            bond_purchase_amount = (pending_cash // 100) * 100
            if bond_purchase_amount >= 100 and annual_yield > 0.0:  # Ensure valid rate and sufficient funds
                maturity_date = current_date + relativedelta(months=3)  # Set maturity date 3 months from now
                bond = Bond(investment=bond_purchase_amount, purchase_date=current_date, maturity_date=maturity_date, annual_yield=annual_yield)
                bonds.append(bond)
                pending_cash -= bond_purchase_amount
                pending_cash = math.floor(pending_cash * 100) / 100  # Floor to the nearest cent

            # Record balances only on the 1st of the month
            if current_date.day == 1:
                total_bond_value = sum(bond.get_value() for bond in bonds)
                balance_history.append({
                    "date": current_date.strftime("%Y-%m-%d"),
                    "cash": pending_cash,
                    "bonds": total_bond_value,
                    "account_balance": pending_cash + total_bond_value,  # Add total balance
                    "interest_rate": annual_yield  # Include interest rate
                })

                # Add monthly investment only on the 1st of the month
                pending_cash += monthly_investment
                pending_cash = math.floor(pending_cash * 100) / 100  # Floor to the nearest cent

            # Increment the date by one day
            current_date += relativedelta(days=1)

        # Attach balance history to the bond account
        bond_account.balance_history = balance_history

        return [bond_account]
    except Exception as e:
        logging.error(f"Error in run_bond_simulation: {e}", exc_info=True)
        raise
