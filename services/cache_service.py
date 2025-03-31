import time
import os
import shutil

# In-memory caches
cache = {}
CACHE_EXPIRATION = 300  # Cache expiration time in seconds
search_tickers_cache = {}
SEARCH_CACHE_EXPIRATION = 600  # Cache expiration time in seconds

def get_cached_response(cache_key):
    """
    Retrieves a cached response if it exists and is not expired.

    :param cache_key: The cache key.
    :return: Cached response or None if not found or expired.
    """
    if cache_key in cache:
        response, timestamp = cache[cache_key]
        if time.time() - timestamp < CACHE_EXPIRATION:
            return response
    return None

def cache_response(cache_key, response):
    """
    Caches a response with the given cache key.

    :param cache_key: The cache key.
    :param response: The response to cache.
    """
    cache[cache_key] = (response, time.time())

def search_tickers_with_cache(query):
    """
    Searches for stock tickers and caches the results.

    :param query: The search query.
    :return: List of search results.
    """
    if query in search_tickers_cache:
        results, timestamp = search_tickers_cache[query]
        if time.time() - timestamp < SEARCH_CACHE_EXPIRATION:
            return results

    from data_fetchers.getStockSearchData import search_stock_tickers
    results = search_stock_tickers(query)
    search_tickers_cache[query] = (results, time.time())
    return results

def clear_all_caches():
    """
    Clears all in-memory caches.
    """
    global cache, search_tickers_cache
    cache.clear()
    search_tickers_cache.clear()

def delete_data_cache_folder():
    """
    Deletes the data_cache folder and all its contents.
    """
    data_cache_path = os.path.join(os.getcwd(), "data_cache")
    if os.path.exists(data_cache_path):
        shutil.rmtree(data_cache_path)
        print("data_cache folder deleted successfully.")
    else:
        print("data_cache folder does not exist.")
