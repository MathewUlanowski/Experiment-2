import os
import json
from datetime import date, timedelta
from fredapi import Fred
from beautify import beautify_json_in_directory
from dateutil.relativedelta import relativedelta  # Import relativedelta for precise date calculations
from beautify import beautify_json_async
import logging

def calculate_date_range(period):
    """
    Calculates the start and end dates based on the given period.

    :param period: Period string (e.g., "10y", "6m").
    :return: Tuple containing start_date and end_date as strings (YYYY-MM-DD).
    """
    end_date = date.today()
    if period.endswith("y"):  # Years
        years = int(period[:-1])
        start_date = end_date - relativedelta(years=years)
    elif period.endswith("m"):  # Months
        months = int(period[:-1])
        start_date = end_date - relativedelta(months=months)
    else:
        raise ValueError("Invalid period format. Use '10y' for 10 years or '6m' for 6 months.")
    return start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")

# In-memory cache for bond rates
bond_rates_cache = {}

def fetch_bond_rates(api_key, period="10y", series_id="DGS10", start_date=None, end_date=None, skip_beautify=False):
    """
    Fetches historical bond rates from FRED using an in-memory cache, folder cache, or API call.

    :param api_key: FRED API key.
    :param period: Period for fetching bond rates (e.g., "10y", "6m"). Ignored if start_date and end_date are provided.
    :param series_id: FRED series ID for bond rates (default: 10-year Treasury rate, "DGS10").
    :param start_date: Start date for fetching bond rates (YYYY-MM-DD). Optional.
    :param end_date: End date for fetching bond rates (YYYY-MM-DD). Optional.
    :param skip_beautify: If True, skips JSON beautification.
    :return: List of bond rates as dictionaries with "date" and "rate" keys.
    """
    # Calculate start_date and end_date if not provided
    if not start_date or not end_date:
        start_date, end_date = calculate_date_range(period)

    cache_key = f"{series_id}_{start_date}_{end_date}"

    # Check in-memory cache
    if cache_key in bond_rates_cache:
        logging.info(f"Cache hit (memory) for bond rates: {cache_key}")
        return bond_rates_cache[cache_key]

    bond_data_folder = "data_cache/bond_data"
    os.makedirs(bond_data_folder, exist_ok=True)
    file_path = f"{bond_data_folder}/{cache_key}.json"

    # Check folder cache
    if os.path.exists(file_path):
        try:
            with open(file_path, "r") as f:
                cached_data = json.load(f)
                bond_rates_cache[cache_key] = cached_data  # Update in-memory cache
                logging.info(f"Cache hit (folder) for bond rates: {cache_key}")
                return cached_data
        except json.JSONDecodeError:
            logging.warning(f"Invalid JSON format in cache file: {file_path}. Deleting the file and refetching data.")
            os.remove(file_path)

    # Fetch data from FRED API
    logging.info(f"Fetching bond rates from API for: {cache_key}")
    fred = Fred(api_key=api_key)
    rates = fred.get_series(series_id, observation_start=start_date, observation_end=end_date)
    rates = rates.ffill()  # Forward-fill missing values
    rates_list = [{"date": str(date), "rate": rate} for date, rate in rates.to_dict().items()]

    # Save to folder cache
    with open(file_path, "w") as f:
        json.dump(rates_list, f)
        logging.info(f"Bond data saved to cache for {start_date} to {end_date}.")

    # Update in-memory cache
    bond_rates_cache[cache_key] = rates_list

    # Beautify the JSON file
    try:
        beautify_json_in_directory(bond_data_folder, skip_beautify=skip_beautify)
    except Exception as e:
        logging.error(f"Error beautifying bond JSON files: {e}")

    return rates_list

# Main function to test the FRED data fetching
if __name__ == "__main__":
    from dotenv import load_dotenv
    import os

    # Load environment variables
    load_dotenv(dotenv_path="./secrets.env")
    fred_api_key = os.getenv("FRED_API_KEY")

    # Test fetching bond rates
    period = "10y"  # Example period
    bond_rates = fetch_bond_rates(fred_api_key, period)

    logging.info("Fetched bond rates: %s", bond_rates)
