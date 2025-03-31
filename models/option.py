class Option:
    """
    Represents an American-style call option.

    :param strike_price: The strike price of the option.
    :param execution_date: The date the option needs to be executed.
    :param ticker: The stock ticker associated with the option.
    """
    def __init__(self, strike_price, execution_date, ticker):
        self.strike_price = strike_price
        self.execution_date = execution_date
        self.ticker = ticker
        self.executed = False

    def execute(self, current_date, stock_price):
        """
        Executes the option if the current date matches the execution date and the stock price exceeds the strike price.

        :param current_date: The current date in the simulation.
        :param stock_price: The current stock price.
        :return: Profit from the executed option, or 0 if not executed.
        """
        if not self.executed and self.execution_date == current_date:
            self.executed = True
            if stock_price > self.strike_price:
                return stock_price - self.strike_price
        return 0

    def __str__(self):
        """
        Returns a string representation of the option.
        """
        return f"Option(Ticker: {self.ticker}, Strike Price: {self.strike_price}, Execution Date: {self.execution_date}, Executed: {self.executed})"
