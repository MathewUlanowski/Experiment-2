import os
import json
from beautify import beautify_json_async, beautify_json_in_directory
import yfinance as yf
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# In-memory cache for stock data
stock_data_cache = {}

def fetch_data(tickers=["AAPL", "TSLA", "MSFT"], period="max", skip_beautify=False):
    """
    Fetches stock data for the given tickers using an in-memory cache, folder cache, or API call.

    :param tickers: List of stock tickers to fetch data for.
    :param period: Period for which to fetch the data (e.g., "1y", "5y").
    :param skip_beautify: If True, skips JSON beautification.
    :return: Dictionary of fetched stock data.
    """
    stock_data_folder = f"data_cache/stock_data/{period}"
    os.makedirs(stock_data_folder, exist_ok=True)

    fetched_data = {}
    fetched_from_api = False  # Track if any data is fetched from the API

    for ticker in tickers:
        cache_key = f"{ticker}_{period}"

        # Check in-memory cache
        if cache_key in stock_data_cache:
            logging.info(f"Cache hit (memory) for stock data: {cache_key}")
            fetched_data[ticker] = stock_data_cache[cache_key]
            continue

        file_path = f"{stock_data_folder}/{ticker}.json"

        # Check folder cache
        if os.path.exists(file_path):
            try:
                with open(file_path, "r") as f:
                    cached_data = json.load(f)
                    stock_data_cache[cache_key] = cached_data  # Update in-memory cache
                    fetched_data[ticker] = cached_data
                    logging.info(f"Cache hit (folder) for stock data: {cache_key}")
                    continue
            except json.JSONDecodeError:
                logging.warning(f"Invalid JSON format in cache file: {file_path}. Deleting the file and refetching data.")
                os.remove(file_path)

        # Fetch data from Yahoo Finance API
        logging.info(f"Fetching stock data from API for: {ticker}")
        try:
            ticker_data = yf.Ticker(ticker)
            df = ticker_data.history(period=period)
            df = df.reset_index()                          # Turn the date index into a column
            df['Date'] = df['Date'].dt.strftime('%Y-%m-%d')# Format date as "YYYY-MM-DD"

            records = df.to_dict(orient='records')

            # Save to folder cache
            with open(file_path, "w") as f:
                json.dump(records, f)
                logging.info(f"New data saved to cache for {ticker} under period {period}.")

            # Update in-memory cache
            stock_data_cache[cache_key] = records
            fetched_data[ticker] = records

            fetched_from_api = True  # Mark that data was fetched from the API
        except Exception as e:
            logging.error(f"Error fetching data for {ticker}: {e}")

    # Beautify the JSON files only if data was fetched from the API
    if fetched_from_api:
        try:
            beautify_json_in_directory(stock_data_folder, skip_beautify=skip_beautify)
            logging.info("Stock JSON files beautified successfully.")
        except Exception as e:
            logging.error(f"Error beautifying stock JSON files: {e}")

    return fetched_data

# main function to run the test
if __name__ == "__main__":
    results = fetch_data()  # Call the test function directly # Beautify the JSON files in the data_cache directory

    logging.info("Fetched data: %s", results)  # Print the fetched data for verification