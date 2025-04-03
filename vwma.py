from kiteconnect import KiteConnect
import pandas as pd

# ---------------------- 1. Initialize Kite API ----------------------
api_key = "tvvurc35y2qhc26f"
access_token = "MYFjt9Z2douVU3cR6zwlGoB7vsuwue7z"

kite = KiteConnect(api_key=api_key)
kite.set_access_token(access_token)

# ---------------------- 2. Fetch Historical Data ----------------------
instrument_token = 738561  # Example: Nifty 50
from_date = "2024-02-01"  # Get at least 1+ month of data
to_date = "2024-03-31"
interval = "day"

historical_data = kite.historical_data(instrument_token, from_date, to_date, interval)
df = pd.DataFrame(historical_data)

# ---------------------- 3. Calculate VWMA ----------------------
def calculate_vwma(df, period=20):
    df["typical_price"] = (df["high"] + df["low"] + df["close"]) / 3
    df["tpv"] = df["typical_price"] * df["volume"]
    
    df["VWMA"] = df["tpv"].rolling(window=period).sum() / df["volume"].rolling(window=period).sum()
    
    return df

df = calculate_vwma(df, period=20)

# Drop NaN values (Optional)
df.dropna(subset=["VWMA"], inplace=True)

# ---------------------- 4. Display Results ----------------------
print(df[["date", "close", "VWMA"]].tail(10))  # Show last 10 rows
