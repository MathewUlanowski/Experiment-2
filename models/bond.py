from datetime import date, timedelta

class Bond:
    """
    Represents an individual bond purchase.

    :param investment: Initial investment amount for the bond.
    :param purchase_date: The date the bond was purchased.
    :param maturity_date: The date when the bond matures and can be cashed in.
    :param annual_yield: Annual yield of the bond (as a decimal, e.g., 0.05 for 5%).
    """
    def __init__(self, investment, purchase_date, maturity_date, annual_yield):
        self.investment = investment
        self.purchase_date = purchase_date  # Store the purchase date
        self.maturity_date = maturity_date
        self.annual_yield = annual_yield  # Store the annual yield at the time of purchase

    def is_matured(self, current_date):
        """
        Checks if the bond has matured (maturity date has been reached).
        """
        return current_date >= self.maturity_date

    def get_value(self):
        """
        Returns the current value of the bond.
        """
        return self.investment

    def get_matured_value(self):
        """
        Returns the total value of the bond upon maturity, including the face amount and interest.
        """
        # Calculate the term of the bond in months
        term_in_months = (self.maturity_date.year - self.purchase_date.year) * 12 + (self.maturity_date.month - self.purchase_date.month)
        # Derive interest based on the term and the bond's stored annual yield
        interest = self.investment * (self.annual_yield / 100) * (term_in_months / 12)
        # Return the face amount (investment) plus the interest
        return round(self.investment + interest, 2)

    def __str__(self):
        """
        Returns a string representation of the bond, including the investment, purchase date, annual yield, and maturity date.
        """
        return f"Bond(Investment: {self.investment}, Purchase Date: {self.purchase_date}, Annual Yield: {self.annual_yield}, Maturity Date: {self.maturity_date})"
