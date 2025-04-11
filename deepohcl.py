from kiteconnect import KiteConnect
from datetime import datetime, timedelta
import pytz
 
# Initialize Kite Connec
api_key = "tvvurc35y2qhc26f"
access_token = "6TLvTLmzkudwkh7m5P6zZrv88RhaFGox"
kite = KiteConnect(api_key=api_key)
kite.set_access_token(access_token)
 
# NIFTY 50 instrument token (256265)
instrument_token = 256265
 
# IST timezone setup
ist = pytz.timezone("Asia/Kolkata")
 
# Get current time in IST and truncate seconds/microseconds
current_time = datetime.now(ist)
end_time = current_time.replace(second=0, microsecond=0)  # Zero seconds
start_time = end_time - timedelta(minutes=1)  # Previous minute
 
try:
    historical_data = kite.historical_data(
        instrument_token=instrument_token,
        from_date=start_time,
        to_date=end_time,
        interval="minute",
        continuous=False
    )
    if historical_data:
        latest_candle = historical_data[-1]
        candle_time = latest_candle['date'].astimezone(ist).strftime("%Y-%m-%d %H:%M:%S")
        print(f"1-Minute OHLC for NIFTY 50 ({candle_time} IST):")
        print(f"Open: {latest_candle['open']}")
        print(f"High: {latest_candle['high']}")
        print(f"Low: {latest_candle['low']}")
        print(f"Close: {latest_candle['close']}")
        print(f"start_time: {start_time}")
        print(f"end_time: {end_time}")
        print(f"current_time: {current_time}")
    else:
        print("No data found for the specified 1-minute window.")
 
except Exception as e:
    print(f"Error: {e}")