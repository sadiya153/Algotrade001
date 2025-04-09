import time
from datetime import datetime
from kiteconnect import KiteConnect
from kiteconnect import KiteConnect
import config
from datetime import datetime, timedelta
import signal
import sys
 
 
kite = KiteConnect(api_key=config.API_KEY)
kite.set_access_token(config.ACCESS_TOKEN)
 
log_file = "buy.txt"
def log_message(message):
    with open(log_file, "a") as file:
        file.write(f"{datetime.now()}: {message}\n")
 
def detect_trend(data):
    if len(data) < 3:
        return "sideways"
    if data[-1] > data[-2] > data[-3]:
        return "uptrend"
    elif data[-1] < data[-2] < data[-3]:
        return "downtrend"
    else:
        return "sideways"
 
def fetch_market_data():
    try:
        instrument = "RELIANCE"
        instruments = kite.instruments("NSE")
        instrument_token = next((item['instrument_token'] for item in instruments if item['tradingsymbol'] == instrument), None)
        if not instrument_token:
            raise ValueError(f"Instrument token for {instrument} not found")
       
        server_time = datetime.now()
        zerodha_time = server_time.replace(second=0, microsecond=0)
        if zerodha_time.second != 0 or zerodha_time.microsecond != 0:
            zerodha_time += timedelta(minutes=1)
       
        from_date = zerodha_time - timedelta(minutes=1)
        to_date = zerodha_time
       
        historical_data = kite.historical_data(
            instrument_token=instrument_token,
            from_date=from_date.strftime('%Y-%m-%d %H:%M:%S'),
            to_date=to_date.strftime('%Y-%m-%d %H:%M:%S'),
            interval="minute"
        )
       
        return [candle['close'] for candle in historical_data]
    except Exception as e:
        log_message(f"Error fetching market data: {e}")
        return []
 
previous_trend = None
 
def execute_trade():
    try:
        order = kite.place_order(
            tradingsymbol="RELIANCE",
            exchange="NSE",
            transaction_type="BUY",
            quantity=1,
            order_type="MARKET",
            product="MIS"
        )
        log_message(f"Trade executed: {order}")
    except Exception as e:
        log_message(f"Error executing trade: {e}")
 
while True:
    current_time = datetime.now()
    next_minute = (current_time + timedelta(minutes=1)).replace(second=0, microsecond=0)
    sleep_duration = (next_minute - current_time).total_seconds()
    time.sleep(sleep_duration)
 
    market_data = fetch_market_data()
    if not market_data:
        continue
 
    current_trend = detect_trend(market_data)
    log_message(f"Current trend detected: {current_trend}")
 
    if current_trend == "uptrend" and not entered_market:
        log_message("Entering the market for the first time.")
        execute_trade()
        entered_market = True
 
    if current_trend != previous_trend:
        log_message(f"Trend changed from {previous_trend} to {current_trend}")
        previous_trend = current_trend
 
def fetch_market_data():
    try:
        instrument = "RELIANCE"
        instruments = kite.instruments("NSE")
        instrument_token = next((item['instrument_token'] for item in instruments if item['tradingsymbol'] == instrument), None)
        if not instrument_token:
            raise ValueError(f"Instrument token for {instrument} not found")
       
        server_time = datetime.now()
        zerodha_time = server_time.replace(second=0, microsecond=0)
        if zerodha_time.second != 0 or zerodha_time.microsecond != 0:
            zerodha_time += timedelta(minutes=1)
       
        from_date = zerodha_time - timedelta(minutes=1)
        to_date = zerodha_time
       
        historical_data = kite.historical_data(
            instrument_token=instrument_token,
            from_date=from_date.strftime('%Y-%m-%d %H:%M:%S'),
            to_date=to_date.strftime('%Y-%m-%d %H:%M:%S'),
            interval="minute"
        )
       
        return [candle['close'] for candle in historical_data]
    except Exception as e:
        log_message(f"Error fetching market data: {e}")
        return []
 
def execute_trade():
    try:
        order = kite.place_order(
            tradingsymbol="RELIANCE",
            exchange="NSE",
            transaction_type="BUY",
            quantity=1,
            order_type="MARKET",
            product="MIS"
        )
        log_message(f"Trade executed: {order}")
    except Exception as e:
        log_message(f"Error executing trade: {e}")
 
def signal_handler(sig, frame):
    log_message("Exiting the code.")
    sys.exit(0)
 
signal.signal(signal.SIGINT, signal_handler)
 
previous_trend = None
entered_market = False
 
while True:
    market_data = fetch_market_data()
    if not market_data:
        time.sleep(60)
        continue
 
    current_trend = detect_trend(market_data)
    log_message(f"Current trend detected: {current_trend}")
 
    if current_trend == "uptrend" and not entered_market:
        log_message("Entering the market for the first time.")
        execute_trade()
        entered_market = True
 
    if current_trend != previous_trend:
        log_message(f"Trend changed from {previous_trend} to {current_trend}")
        previous_trend = current_trend
 
    time.sleep(60)