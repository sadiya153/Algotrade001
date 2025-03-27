import time
from kiteconnect import KiteConnect
import config
 
kite = KiteConnect(api_key=config.API_KEY)
kite.set_access_token(config.ACCESS_TOKEN)
 
def get_instrument_token(symbol, exchange="NFO"):
    
    instruments = kite.instruments(exchange)
    for instrument in instruments:
        if instrument["tradingsymbol"] == symbol:
            return instrument["instrument_token"]
    print(f"⚠️ Instrument token not found for {symbol}")
    return None
 
def get_nearest_strike_price(price, step=50):
    
    return round(price / step) * step
 
def get_option_symbol(atm_strike, option_type):

    instruments = kite.instruments("NFO")
    for instrument in instruments:
        if f"NIFTY" in instrument["tradingsymbol"] and str(atm_strike) in instrument["tradingsymbol"] and option_type in instrument["tradingsymbol"]:
            return instrument["tradingsymbol"]
    return None

def fetch_live_nifty_data():
    symbol = "NIFTY 50"
    exchange = "NSE"
 
    print(f"\nFetching live data for {symbol}...\n")
 
    while True:
        try:
            quote = kite.ltp(f"{exchange}:{symbol}")
            nifty_price = quote[f"{exchange}:{symbol}"]["last_price"]
            atm_strike = get_nearest_strike_price(nifty_price)
 
            ce_symbol = get_option_symbol(atm_strike, "CE")
            pe_symbol = get_option_symbol(atm_strike, "PE")
 
            if not ce_symbol or not pe_symbol:
                print(f"⚠️ No valid option contracts found for ATM {atm_strike}. Retrying...")
                time.sleep(5)
                continue
 
            option_data = kite.ltp([f"NFO:{ce_symbol}", f"NFO:{pe_symbol}"])
 
            ce_price = option_data[f"NFO:{ce_symbol}"]["last_price"]
            pe_price = option_data[f"NFO:{pe_symbol}"]["last_price"]
 
    
            print("\n--- Live Market Data ---")
            print(f"NIFTY 50 Index Value  : {nifty_price}")
            print(f"ATM Strike Price      : {atm_strike}")
            print(f"ATM CE Value ({ce_symbol}): {ce_price}")
            print(f"ATM PE Value ({pe_symbol}): {pe_price}")
 
            time.sleep(1) 
 
        except Exception as e:
            print(f"Error fetching data: {e}")
            time.sleep(5)  
 
fetch_live_nifty_data()