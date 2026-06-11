import numpy as np
import pandas as pd

def simulate_bitcoin_price(days=60, start_price=60000, mu=0.1, sigma=0.4):
    """
    Simulates Bitcoin price using Geometric Brownian Motion (GBM).

    mu: annual drift
    sigma: annual volatility
    """
    dt = 1/365
    np.random.seed(100) # For reproducible results that show trading action

    # Generate daily returns
    daily_returns = np.exp((mu - 0.5 * sigma**2) * dt + sigma * np.sqrt(dt) * np.random.normal(0, 1, days))
    prices = start_price * np.cumprod(daily_returns)

    # Prepend the start price and remove the last one to keep it at 'days' length
    prices = np.insert(prices, 0, start_price)[:-1]

    dates = pd.date_range(start='2023-01-01', periods=days)
    df = pd.DataFrame({'Date': dates, 'Price': prices})

    # Calculate 7-day and 30-day Moving Averages using pandas
    df['MA7'] = df['Price'].rolling(window=7).mean()
    df['MA30'] = df['Price'].rolling(window=30).mean()

    return df

def run_trading_strategy(df, initial_balance=10000):
    """
    Implements the Golden Cross trading strategy:
    - BUY when 7-day MA crosses above 30-day MA.
    - SELL when 7-day MA crosses below 30-day MA.
    """
    balance = initial_balance
    btc_holdings = 0
    position = False  # False means we are in cash, True means we hold BTC

    print(f"{'Date':<12} | {'Price':<10} | {'MA7':<10} | {'MA30':<10} | {'Action':<10} | {'Portfolio Value':<15}")
    print("-" * 85)

    for i in range(len(df)):
        row = df.iloc[i]
        date_str = row['Date'].strftime('%Y-%m-%d')
        price = row['Price']
        ma7 = row['MA7']
        ma30 = row['MA30']
        action = "Wait"

        # Trading Logic: Golden Cross / Death Cross
        if not np.isnan(ma7) and not np.isnan(ma30):
            if ma7 > ma30 and not position:
                # Buy signal
                btc_holdings = balance / price
                balance = 0
                position = True
                action = "BUY"
            elif ma7 < ma30 and position:
                # Sell signal
                balance = btc_holdings * price
                btc_holdings = 0
                position = False
                action = "SELL"

        # Calculate current portfolio value for display
        current_value = balance + (btc_holdings * price)
        print(f"{date_str:<12} | {price:10.2f} | {ma7 if not np.isnan(ma7) else 0:10.2f} | {ma30 if not np.isnan(ma30) else 0:10.2f} | {action:<10} | {current_value:15.2f}")

    final_price = df.iloc[-1]['Price']
    final_value = balance + (btc_holdings * final_price)

    print("-" * 85)
    print(f"Initial Portfolio Value: ${initial_balance:.2f}")
    print(f"Final Portfolio Value:   ${final_value:.2f}")
    print(f"Total Return:            {((final_value - initial_balance) / initial_balance) * 100:.2f}%")

if __name__ == "__main__":
    # Simulate 60 days of Bitcoin data
    bitcoin_data = simulate_bitcoin_price(days=60)

    # Run the Golden Cross strategy
    run_trading_strategy(bitcoin_data)
