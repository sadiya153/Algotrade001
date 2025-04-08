import time
from datetime import datetime
from kiteconnect import KiteConnect
import config
 
kite = KiteConnect(api_key=config.API_KEY)
try:
    kite.set_access_token(config.ACCESS_TOKEN)
except Exception as e:
    print(f"Error setting access token: {e}")
    exit(1)
 
# Function to fetch historical data
def fetch_historical_data(instrument_token, interval, from_date, to_date):
    return kite.historical_data(instrument_token, from_date, to_date, interval)
 
# Function to calculate VWAP
def calculate_vwap(data):
    cumulative_price_volume = 0
    cumulative_volume = 0
    for candle in data:
        high = candle['high']
        low = candle['low']
        close = candle['close']
        volume = candle['volume']
        typical_price = (high + low + close) / 3
        cumulative_price_volume += typical_price * volume
        cumulative_volume += volume
    return cumulative_price_volume / cumulative_volume if cumulative_volume != 0 else 0
 
# Main function to fetch data and calculate VWAP every minute
def main():
    instrument_token_ce = 123456  # Replace with the instrument token for NIFTY50 CE
    instrument_token_pe = 654321  # Replace with the instrument token for NIFTY50 PE
    interval = "minute"
    
    from_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    to_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    while True:
        now = datetime.now()
        try:
            data_ce = fetch_historical_data(instrument_token_ce, interval, from_date, to_date)
        except Exception as e:
            print(f"Error fetching data for CE: {e}")
            try:
                data_pe = fetch_historical_data(instrument_token_pe, interval, from_date, to_date)
            except Exception as e:
                print(f"Error fetching data for PE: {e}")
                continue
            from_date = to_date = now.strftime("%Y-%m-%d %H:%M:%S")
            
            # Fetch data for CE
            data_ce = fetch_historical_data(instrument_token_ce, interval, from_date, to_date)
            vwap_ce = calculate_vwap(data_ce)
            
            # Fetch data for PE
            data_pe = fetch_historical_data(instrument_token_pe, interval, from_date, to_date)
            vwap_pe = calculate_vwap(data_pe)
            
            # Print VWAP values
            print(f"VWAP CE at {now.strftime('%Y-%m-%d %H:%M:%S')}: {vwap_ce}")
            print(f"VWAP PE at {now.strftime('%Y-%m-%d %H:%M:%S')}: {vwap_pe}")
            
            time.sleep(60)  # Wait for the next minute
        time.sleep(1)  # Check every second
 
if __name__ == "__main__":
    main()