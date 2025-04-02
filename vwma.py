import time
import pandas as pd
from datetime import datetime, timedelta
from kiteconnect import KiteConnect
import config  

kite = KiteConnect(api_key=config.API_KEY)
kite.set_access_token(config.ACCESS_TOKEN)

def fetch_nifty_historical():
    """
    Fetches historical data for NIFTY 50 for the past 30 minutes.
    """
    to_date = datetime.now()
    from_date = to_date - timedelta(minutes=30)  # Fetch last 30 minutes of data
    interval = "minute"

    try:
        historical_data = kite.historical_data(256265, from_date, to_date, interval)  # 256265 = NIFTY 50 token
        df = pd.DataFrame(historical_data)

        if df.empty:
            print("No historical data fetched.")
            return None

        return df

    except Exception as e:
        print(f"Error fetching historical data: {e}")
        return None

def calculate_vwma(df, period=10):
    """
    Calculates the Volume-Weighted Moving Average (VWMA).
    """
    if df is None or df.empty:
        print("No data available for VWMA calculation.")
        return None

    # Ensure necessary columns exist
    if 'volume' not in df.columns or 'close' not in df.columns:
        print("Missing required columns in data")
        return None

    # Handle missing and zero values in volume
    df['volume'] = df['volume'].replace(0, 1).fillna(1)  # Replace zero with 1
    df['close'] = df['close'].ffill()  # Use forward fill for missing close prices

    # Calculate VWMA
    df["Weighted_Price"] = df["close"] * df["volume"]
    df["VWMA"] = df["Weighted_Price"].rolling(window=period).sum() / df["volume"].rolling(window=period).sum()

    return df["VWMA"].iloc[-1]  # Return latest VWMA value

def fetch_live_nifty():
    """
    Fetches live NIFTY 50 price and calculates VWMA.
    """
    print("\nFetching Live Data for NIFTY 50 with VWMA...\n")

    while True:
        try:
            # Fetch Live NIFTY Price
            quote = kite.quote("NSE:NIFTY 50")
            nifty_price = quote["NSE:NIFTY 50"]["last_price"]

            # Fetch Historical Data
            historical_df = fetch_nifty_historical()

            # Calculate VWMA
            vwma = calculate_vwma(historical_df)

            # Get Current Time
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Print Data
            print(f"{current_time} | NIFTY 50: {nifty_price} | VWMA: {vwma}")

            time.sleep(60)  # Wait for 1 minute before fetching again

        except KeyboardInterrupt:
            print("\nStopping data fetch...")
            break
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(60)

if __name__ == "__main__":
    fetch_live_nifty()
