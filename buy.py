import time
from datetime import datetime
from kiteconnect import KiteConnect
from kiteconnect import KiteConnect
import config
from datetime import datetime, timedelta
 
 
kite = KiteConnect(api_key=config.API_KEY)
kite.set_access_token(config.ACCESS_TOKEN)
 
log_file = "buy.txt"
 
def log_action(message):
    with open(log_file, "a") as file:
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
        file.write(f"[{timestamp}] {message}\n")
    print(message)
 
def get_trend(data):
    if data[-1]['close'] > data[-2]['close']:
        return "uptrend"
    elif data[-1]['close'] < data[-2]['close']:
        return "downtrend"
    else:
        return "sideways"
 
def fetch_candle_data(instrument_token, interval="1minute"):
    to_date = datetime.utcnow()
    from_date = to_date - timedelta(minutes=2)
    data = kite.historical_data(
        instrument_token=instrument_token,
        from_date=from_date,
        to_date=to_date,
        interval=interval
    )
    return data
 
def main():
    instrument_token = 738561
    log_action("Script started. Monitoring trends...")
    waiting_for_entry = True
 
    while 1:
        try:
            data = fetch_candle_data(instrument_token)
            if len(data) < 2:
                log_action("Insufficient data. Waiting for more candles...")
                time.sleep(60)
                continue
 
            trend = get_trend(data)
            if waiting_for_entry:
                log_action("Waiting to take entry in the market...")
                if trend == "uptrend":
                    log_action("Taking entry: Uptrend detected. Buying Call.")
                    waiting_for_entry = False
                elif trend == "downtrend":
                    log_action("Taking entry: Downtrend detected. Buying Put.")
                    waiting_for_entry = False
                else:
                    log_action("Sideways trend detected. Waiting for a clear trend.")
            else:
                log_action("Already in position. Monitoring the market...")
 
        except Exception as e:
            log_action(f"Error: {e}")
 
        time.sleep(60)
 
if __name__ == "__main__":
    main()