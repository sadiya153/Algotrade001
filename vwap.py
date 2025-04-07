from kiteconnect import KiteConnect
import pandas as pd
import config
print("Starting VWAP calculation...")
# Replace with your credentials
kite = KiteConnect(api_key=config.API_KEY)
kite.set_access_token(config.ACCESS_TOKEN)


def fetch_historical_data(instrument_token, interval, from_date, to_date):
    """Fetch historical data for a given instrument."""
    data = kite.historical_data(instrument_token, from_date, to_date, interval)
    return pd.DataFrame(data)

def calculate_vwap(data):
    """Calculate VWAP from historical data."""
    data['vwap'] = (data['volume'] * (data['high'] + data['low'] + data['close']) / 3).cumsum() / data['volume'].replace(0, float('nan')).cumsum()
    return data

# Replace with the instrument tokens for Nifty50 CE and PE
nifty_ce_token = 256265  # Example: Replace with the actual instrument token for Nifty50 CE
nifty_pe_token = 260105  # Example: Replace with the actual instrument token for Nifty50 PE

# Fetch historical data (adjust the date range and interval as needed)
from_date = "2023-01-01"
to_date = "2023-01-31"
interval = "5minute"

# Fetch and calculate VWAP for CE
ce_data = fetch_historical_data(nifty_ce_token, interval, from_date, to_date)
ce_data = calculate_vwap(ce_data)

# Fetch and calculate VWAP for PE
pe_data = fetch_historical_data(nifty_pe_token, interval, from_date, to_date)
pe_data = calculate_vwap(pe_data)

# Print the results
print("VWAP for Nifty50 CE:")
print(ce_data[['date', 'vwap']])

print("\nVWAP for Nifty50 PE:")
print(pe_data[['date', 'vwap']])