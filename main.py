import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def load_data_from_json(filepath):
    """Load historical price data (daily) from a JSON file with columns
       at least ['Date', 'Adj Close']."""
    with open(filepath, 'r') as f:
        data = json.load(f)
    df = pd.DataFrame(data)
    df['Date'] = pd.to_datetime(df['Date'])
    df.set_index('Date', inplace=True)
    df.sort_index(inplace=True)
    return df

def resample_to_monthly(df):
    """
    Given a daily DataFrame with an 'Adj Close' price,
    return a monthly DataFrame with end-of-month 'Adj Close' prices.
    """
    monthly_df = df['Adj Close'].resample('M').last().to_frame('Adj Close')
    monthly_df.dropna(inplace=True)
    return monthly_df

def dca_simulation(df, monthly_invest=1000.0):
    """
    Simulate a traditional Dollar-Cost Averaging approach:
      - monthly_invest is the amount invested each month
      - buy shares of the 'index' at the monthly price
    Returns a DataFrame with columns:
      - 'Price': monthly price
      - 'Shares Purchased': how many shares were bought that month
      - 'Total Shares': total shares accumulated
      - 'Portfolio Value': total shares * current price
    """
    prices = df['Adj Close']
    # We will iterate month by month
    total_shares = 0.0

    records = []
    for date, price in prices.iteritems():
        # buy shares with the monthly_invest
        shares_bought = monthly_invest / price
        total_shares += shares_bought
        portfolio_value = total_shares * price

        records.append({
            'Price': price,
            'Shares Purchased': shares_bought,
            'Total Shares': total_shares,
            'Portfolio Value': portfolio_value
        })

    result = pd.DataFrame(records, index=prices.index)
    return result

def indexed_account_simulation(df, monthly_premium=1000.0,
                              monthly_cap=None,
                              floor_rate=0.0):
    """
    A SIMPLIFIED simulation of an 'indexed' strategy:
      - Start with an account value of 0
      - Each month:
          1) Earn monthly_return = price[t]/price[t-1] - 1
             subject to (floor_rate <= monthly_return <= monthly_cap)
          2) The account grows by (1 + credited_return).
          3) Then deposit the next premium.
      - monthly_cap: if not None, is the maximum monthly credited rate
      - floor_rate: typically 0.0 (no negative returns)

    Returns a DataFrame with columns:
      - 'Index Price'
      - 'Index Monthly Return' (actual from historical data)
      - 'Credited Rate' (after floor and cap)
      - 'Account Value'
      - 'Monthly Premium'
    """
    # monthly prices
    prices = df['Adj Close']
    # We need monthly percentage change
    pct_change = prices.pct_change()

    account_value = 0.0
    records = []

    for i, (date, price) in enumerate(prices.iteritems()):
        if i == 0:
            # On the very first month, there's no prior price for return
            monthly_return = 0.0
            credited_rate = max(floor_rate, monthly_return)
        else:
            monthly_return = pct_change.iloc[i]  # e.g. 0.03 => 3%
            # Apply floor and cap
            credited_rate = max(floor_rate, monthly_return)
            if monthly_cap is not None:
                credited_rate = min(credited_rate, monthly_cap)

        # Growth by credited rate
        account_value = account_value * (1 + credited_rate)

        # Add this month's premium (e.g. deposit at the end of month)
        account_value += monthly_premium

        records.append({
            'Index Price': price,
            'Index Monthly Return': monthly_return,
            'Credited Rate': credited_rate,
            'Account Value': account_value,
            'Monthly Premium': monthly_premium
        })

    result = pd.DataFrame(records, index=prices.index)
    return result

def main():
    # 1) Load the data
    df = load_data_from_json('data/your_symbol.json')  # Adjust the file path

    # 2) Convert daily to monthly
    monthly_df = resample_to_monthly(df)

    # 3) Simulate DCA
    dca_results = dca_simulation(monthly_df, monthly_invest=1000.0)

    # 4) Simulate simplified "Insurer-Style" Indexed Account
    #    Suppose we set a monthly cap of 2% (0.02).
    #    Floor rate = 0% => no negative crediting.
    indexed_results = indexed_account_simulation(
        monthly_df,
        monthly_premium=1000.0,
        monthly_cap=0.02,   # 2% monthly cap
        floor_rate=0.0      # 0% floor
    )

    # 5) Compare final values
    final_dca_value = dca_results['Portfolio Value'].iloc[-1]
    final_indexed_value = indexed_results['Account Value'].iloc[-1]

    print("=== DCA Results ===")
    print(dca_results.tail())
    print(f"Final DCA Portfolio Value: ${final_dca_value:,.2f}\n")

    print("=== Indexed Account Results ===")
    print(indexed_results.tail())
    print(f"Final Indexed Account Value: ${final_indexed_value:,.2f}")

    # 6) Plot each strategy's growth over time
    # (A) DCA portfolio value
    plt.figure()
    plt.plot(dca_results.index, dca_results['Portfolio Value'], label='DCA Portfolio Value')
    plt.title('Dollar-Cost Averaging Portfolio Value')
    plt.xlabel('Date')
    plt.ylabel('Value (USD)')
    plt.legend()
    plt.show()

    # (B) Indexed account value
    plt.figure()
    plt.plot(indexed_results.index, indexed_results['Account Value'], label='Indexed Account Value')
    plt.title('Indexed Account Value')
    plt.xlabel('Date')
    plt.ylabel('Value (USD)')
    plt.legend()
    plt.show()

    # (C) Comparison in one chart
    #     We need to align the two DataFrames on the same index
    compare_df = pd.DataFrame({
        'DCA': dca_results['Portfolio Value'],
        'Indexed': indexed_results['Account Value']
    }).dropna()  # in case starting indices differ

    plt.figure()
    plt.plot(compare_df.index, compare_df['DCA'], label='DCA')
    plt.plot(compare_df.index, compare_df['Indexed'], label='Indexed')
    plt.title('DCA vs. Simplified Indexed Strategy')
    plt.xlabel('Date')
    plt.ylabel('Value (USD)')
    plt.legend()
    plt.show()

if __name__ == "__main__":
    main()
