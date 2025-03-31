from datetime import date, datetime

class Account:
    """
    Represents a generic investment account that tracks balance, investments, and assets (e.g., shares, bonds).
    """
    def __init__(self, date: date, initial_balance=0, name="Unnamed Account"):
        """
        Initializes the account with an initial balance and an optional name.

        :param initial_balance: The starting balance of the account.
        :param name: The name of the account (e.g., ticker or identifier).
        """
        self.name = name
        self.balance = initial_balance
        self.total_invested = initial_balance
        self.assets = 0  # Represents the quantity of assets (e.g., shares, bonds)
        self.history = [{"timestamp": date, "balance": initial_balance}]  # Track balance changes with timestamps
        self.balance_history = [{"date": date.strftime("%Y-%m-%d"), "account_balance": initial_balance}]  # Use current date

    def add_funds(self, amount, date):
        """
        Adds funds to the account and updates the total invested amount.

        :param amount: The amount to add to the account.
        """
        self.balance += amount
        self.total_invested += amount
        self._record_history(date)

    def buy_assets(self, price):
        """
        Buys assets (e.g., shares, bonds) using the available balance.

        :param price: The price of a single asset.
        :return: The number of assets bought.
        """
        if price > 0 and self.balance >= price:
            assets_bought = self.balance // price
            self.assets += assets_bought
            self.balance -= assets_bought * price
            self._record_history()
            return assets_bought
        return 0

    def get_portfolio_value(self, asset_price):
        """
        Calculates the total portfolio value, including the value of assets and the remaining balance.

        :param asset_price: The current price of a single asset.
        :return: The total portfolio value.
        """
        return self.assets * asset_price + self.balance

    def deduct_funds(self, amount):
        """
        Deducts funds from the account balance.

        :param amount: The amount to deduct.
        """
        if self.balance >= amount:
            self.balance -= amount
            self._record_history()

    def _record_history(self, date):
        """
        Records the current balance and timestamp in the history.
        """
        self.history.append({"date": date, "balance": self.balance})

    def record_balance(self, date, balance):
        """
        Records the balance for a specific date.

        :param date: The date for which the balance is being recorded.
        :param balance: The balance to record.
        """
        balance = round(balance, 2)
        self.balance = balance
        self.balance_history.append({"date": date.strftime("%Y-%m-%d"), "account_balance": balance})

    def get_balance_history(self):
        """
        Returns the balance history.

        :return: A list of dictionaries containing 'date' and 'account_balance'.
        """
        return self.balance_history

    def __str__(self):
        """
        Returns a string representation of the account.
        """
        return f"Account(Name: {self.name}, Balance: {self.balance}, Total Invested: {self.total_invested}, Assets: {self.assets})"
