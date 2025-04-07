from datetime import datetime
import logging
import math
from random import uniform
from models.account import Account
from models.bond import Bond
from data_fetchers.getFREDData import fetch_bond_rates
from data_fetchers.getYFinanceData import fetch_data
from services.company_service import get_company_name
from utils.date_utils import pad_historical_prices
from dateutil.relativedelta import relativedelta

logging.basicConfig(
    level=logging.ERROR,
    format="%(asctime)s - %(levelname)s - %(message)s [%(filename)s:%(lineno)d]"
)

def run_hybrid_simulation(params):
    """
    Simulates a hybrid strategy combining bonds and options based on real stock and bond data.

    :param params: A dictionary containing simulation parameters:
                   - start_date: Start date of the simulation.
                   - end_date: End date of the simulation.
                   - initial_investment: Initial investment amount.
                   - tickers: List of stock tickers for options.
    :return: A list of Account objects, one for each ticker, representing the hybrid simulation results.
    """
    try:
        start_date = datetime.strptime(params["start_date"], "%Y-%m-%d")
        end_date = datetime.strptime(params["end_date"], "%Y-%m-%d")
        initial_investment = int(params["initial_investment"].replace(",", ""))
        tickers = params["tickers"].split(",") if isinstance(params["tickers"], str) else params["tickers"]

        # Fetch bond rates for the simulation period
        from dotenv import load_dotenv
        import os
        load_dotenv(dotenv_path="./secrets.env")
        fred_api_key = os.getenv("FRED_API_KEY")
        bond_rates = fetch_bond_rates(fred_api_key, start_date=start_date.date(), end_date=end_date.date())
        bond_rate_dict = {rate["date"]: rate["rate"] for rate in bond_rates}

        # Pad bond rates to ensure no missing dates
        padded_bond_rates = pad_historical_prices(
            [{"Date": date, "Close": rate} for date, rate in bond_rate_dict.items()],
            start_date.strftime("%Y-%m-%d"),
            end_date.strftime("%Y-%m-%d")
        )
        bond_rate_dict = {entry["Date"]: entry["Close"] for entry in padded_bond_rates}

        # Fetch historical stock data for all tickers
        historical_datas = fetch_data(tickers=tickers, period="max")
        if not historical_datas:
            raise ValueError("Failed to fetch historical data for the provided tickers.")

        accounts = []  # List to store accounts for each ticker

        for ticker in tickers:
            historical_data = historical_datas.get(ticker)
            historical_data_dict = {data['Date']: data['Close'] for data in historical_data}
            company_name = historical_datas.get("company_name")
            if not company_name:
                try:
                    company_name = get_company_name(ticker)
                except Exception as e:
                    logging.error(f"Failed to fetch company name for ticker {ticker}: {e}")
                    company_name = "Unknown Company"


            # Initialize accounts for the current ticker
            cash_account = Account(start_date, initial_balance=initial_investment, name=f"Cash Account - {ticker}")
            bond_account = Account(start_date, initial_balance=0, name=f"Bond Account - {ticker}")
            option_account = Account(start_date, initial_balance=0, name=f"Option Account - {ticker}")
            hybrid_account = Account(start_date, initial_balance=initial_investment, name=f"(Hybrid) {ticker} - {company_name}")

            current_date = start_date
            bonds = []

            balance_history = [{
                "date": current_date.strftime("%Y-%m-%d"),
                "cash": cash_account.balance,
                "bonds": 0.0,
                "options": 0.0,
                "account_balance": cash_account.balance,  # Add total balance
                "bond_count": len(bonds)
            }]

            while current_date <= end_date:
                # Format the current date to match the bond rate data format
                current_date_str = current_date.strftime("%Y-%m-%d")

                # Get the annual yield for the current date
                annual_yield = bond_rate_dict.get(current_date_str, 0.0)

                # Maturing bonds
                interest_accrued = 0.0
                for bond in bonds[:]:
                    if bond.is_matured(current_date):
                        # Cash in the bond on its maturity date
                        interest_accrued += bond.get_value() - bond.get_matured_value()
                        cash_account.record_balance(current_date, cash_account.balance + bond.get_value())
                        bonds.remove(bond)

                # Purchase bonds in $100 increments
                bond_purchase_amount = (cash_account.balance // 100) * 100
                if bond_purchase_amount >= 100 and annual_yield > 0.0:  # Ensure valid rate and sufficient funds
                    maturity_date = current_date + relativedelta(months=3)  # Set maturity date 3 months from now
                    bond = Bond(investment=bond_purchase_amount, purchase_date=current_date, maturity_date=maturity_date, annual_yield=annual_yield)
                    bonds.append(bond)
                    cash_account.record_balance(current_date, cash_account.balance - bond_purchase_amount)

                # Purchase options on the first day of each month
                if current_date.day == 1 and cash_account.balance > 0:
                    option_budget = interest_accrued

                    # Get the stock price for the current date
                    ticker_data = historical_data_dict.get(ticker, {})
                    current_price = ticker_data.get(current_date.strftime("%Y-%m-%d"))

                    if current_price is not None:
                        # Determine strike price and cost of options
                        strike_price = current_price * uniform(1.05, 1.15)  # 5-15% above current price
                        option_cost = option_budget

                        # Simulate option outcome (e.g., profit or loss)
                        option_profit = max(0, (current_price - strike_price) * (option_cost / current_price))
                        option_account.record_balance(current_date, option_account.balance + option_profit)

                # Record balances only on the 1st of the month
                if current_date.day == 1:
                    total_bond_value = sum(bond.get_value() for bond in bonds)
                    total_balance = cash_account.balance + total_bond_value + option_account.balance
                    balance_history.append({
                        "date": current_date.strftime("%Y-%m-%d"),
                        "cash": cash_account.balance,
                        "bonds": total_bond_value,
                        "options": option_account.balance,
                        "account_balance": total_balance,
                        "bond_count": len(bonds)
                    })

                current_date += relativedelta(days=1)

            hybrid_account.balance_history = balance_history
            accounts.append(hybrid_account)

        return accounts

    except Exception as e:
        logging.error(f"Error in run_hybrid_simulation: {e}", exc_info=True)
        raise