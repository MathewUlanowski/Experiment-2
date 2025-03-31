from datetime import datetime, timedelta

def pad_historical_prices(historical_prices, start_date, end_date):
    """
    Pads the historical prices by carrying forward the previous price for non-trading days.

    :param historical_prices: List of dictionaries with 'Date' and 'Close' keys.
    :param start_date: Start date of the simulation (YYYY-MM-DD).
    :param end_date: End date of the simulation (YYYY-MM-DD).
    :return: Padded list of historical prices with no missing dates.
    """
    padded_prices = []
    current_date = datetime.strptime(start_date, "%Y-%m-%d")
    end_date = datetime.strptime(end_date, "%Y-%m-%d")
    price_index = 0

    while current_date <= end_date:
        if price_index < len(historical_prices) and historical_prices[price_index]['Date'] == current_date.strftime("%Y-%m-%d"):
            padded_prices.append(historical_prices[price_index])
            price_index += 1
        else:
            # Carry forward the previous price if it's not a trading day
            previous_price = padded_prices[-1]['Close'] if padded_prices else 0
            padded_prices.append({'Date': current_date.strftime("%Y-%m-%d"), 'Close': previous_price})
        current_date += timedelta(days=1)

    return padded_prices
