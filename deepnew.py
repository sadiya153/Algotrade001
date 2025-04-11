from kiteconnect import KiteConnect
from datetime import datetime, timedelta
import pytz
import time

# Initialize Kite Connect
api_key = "tvvurc35y2qhc26f"
access_token = "6TLvTLmzkudwkh7m5P6zZrv88RhaFGox"
kite = KiteConnect(api_key=api_key)
kite.set_access_token(access_token)

# NIFTY 50 instrument token (256265)
instrument_token = 256265

# IST timezone setup
ist = pytz.timezone("Asia/Kolkata")

# Define CE and PE instrument tokens (replace with actual tokens)
ce_instrument_token = None  # Replace with actual CE instrument token
pe_instrument_token = None  # Replace with actual PE instrument token

while True:
    # Get current time in IST and truncate seconds/microseconds
    current_time = datetime.now(ist)
    end_time = current_time.replace(second=0, microsecond=0)  # Zero seconds
    start_time = end_time - timedelta(minutes=1)  # Previous minute

    try:
        # Fetch historical data for NIFTY 50
        historical_data = kite.historical_data(
            instrument_token=instrument_token,
            from_date=start_time,
            to_date=end_time,
            interval="minute",
            continuous=False
        )
        
        if historical_data:
            latest_candle = historical_data[-1]
            
            # Calculate ATM Strike Price
            nifty_close = latest_candle['close']
            atm_strike_price = round(nifty_close / 100) * 100  # Round to nearest 100
            
            # Fetch CE and PE data
            ce_data = kite.ltp("NSE:" + str(ce_instrument_token)) if ce_instrument_token else None
            pe_data = kite.ltp("NSE:" + str(pe_instrument_token)) if pe_instrument_token else None
            
            # Print Time, O, H, L, C values and ATM Strike Price
            candle_time = latest_candle['date'].astimezone(ist).strftime("%Y-%m-%d %H:%M:%S")
            print(f"Time: {candle_time} | O: {latest_candle['open']} | H: {latest_candle['high']} | L: {latest_candle['low']} | C: {latest_candle['close']}")
            print(f"ATM Strike Price: {atm_strike_price}")
            if ce_data:
                print(f"CE Price: {ce_data['NSE:' + str(ce_instrument_token)]['last_price']}")
            if pe_data:
                print(f"PE Price: {pe_data['NSE:' + str(pe_instrument_token)]['last_price']}")
        else:
            print("No data found for the specified 1-minute window.")

    except Exception as e:
        print(f"Error: {e}")

    # Wait for 60 seconds before the next iteration
    time.sleep(60)