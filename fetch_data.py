import time
from kiteconnect import KiteConnect
import config
 
kite = KiteConnect(api_key=config.API_KEY)
kite.set_access_token(config.ACCESS_TOKEN)
 
def get_instrument_token(symbol, exchange="NSE"):
    """Fetch the instrument token dynamically."""
    instruments = kite.instruments(exchange)
    for instrument in instruments:
        if instrument["tradingsymbol"] == symbol:
            return instrument["instrument_token"]
    raise ValueError(f"Instrument token not found for {symbol}")
 
symbol = "NIFTY 50"  
exchange = "NSE"
 
try:
    instrument_token = get_instrument_token(symbol, exchange)
    print(f"Fetching live data for {symbol} (Instrument Token: {instrument_token})")
except Exception as e:
    print(f"Error fetching instrument token: {e}")
    exit()
 
while True:
    try:
        quote = kite.ltp(f"{exchange}:{symbol}")
        print(f"Live Price of {symbol}: {quote[f'{exchange}:{symbol}']['last_price']}")
        time.sleep(1)
    except Exception as e:
        print(f"Error fetching data: {e}")
        if "TokenException" in str(e):
            print("Access token might be expired. Run get_access_token.py again.")
        time.sleep(5)