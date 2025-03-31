import requests
import os
import logging
from dotenv import load_dotenv

# Load environment variables from secrets.env
load_dotenv(dotenv_path="./secrets.env")

# Cache for storing search results
search_cache = {}

def search_stock_tickers(query):
    """
    Searches for stock tickers based on a query string. Caches responses for efficiency.

    :param query: The search query (e.g., company name or ticker symbol).
    :return: A list of matching stock tickers with their names and symbols.
    """
    # Check if the query is already cached
    if query in search_cache:
        logging.info(f"Cache hit for query: {query}")
        return search_cache[query]

    api_key = os.getenv("POLYGON_API_KEY")
    if not api_key:
        raise ValueError("POLYGON_API_KEY is not set in the environment.")

    url = f"https://api.polygon.io/v3/reference/tickers?search={query}&active=true&apiKey={api_key}"
    response = requests.get(url)

    if response.status_code != 200:
        raise Exception(f"Failed to fetch stock tickers: {response.status_code} - {response.text}")

    data = response.json()
    results = data.get("results", [])
    formatted_results = [{"symbol": result["ticker"], "name": result["name"]} for result in results]
    
    # Cache the response
    search_cache[query] = formatted_results

    return formatted_results

# Test the function
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    query = input("Enter a search query for stock tickers: ")
    try:
        results = search_stock_tickers(query)
        logging.info("Search Results:")
        for result in results:
            logging.info(f"{result['symbol']}: {result['name']}")
    except Exception as e:
        logging.error(f"Error: {e}")
