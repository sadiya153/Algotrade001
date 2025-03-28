import time
from kiteconnect import KiteConnect
import config  

kite = KiteConnect(api_key=config.API_KEY)
kite.set_access_token(config.ACCESS_TOKEN)

def get_nearest_strike_price(price, step=50):
    return round(price / step) * step

def get_option_symbol(atm_strike, option_type):
    instruments = kite.instruments("NFO")
    for instrument in instruments:
        if "NIFTY" in instrument["tradingsymbol"] and str(atm_strike) in instrument["tradingsymbol"] and option_type in instrument["tradingsymbol"]:
            return instrument["tradingsymbol"]
    return None

def fetch_nifty_data():
    print("\nFetching live data for NIFTY 50...\n")
    
    while True:
        try:
            quote = kite.quote("NSE:NIFTY 50")
            nifty_price = quote["NSE:NIFTY 50"]["last_price"]

            atm_strike = get_nearest_strike_price(nifty_price)

            ce_symbol = get_option_symbol(atm_strike, "CE")
            pe_symbol = get_option_symbol(atm_strike, "PE")

            if not ce_symbol or not pe_symbol:
                print(f"No valid option contracts found for ATM {atm_strike}. Retrying...")
                time.sleep(1)
                continue

            option_data = kite.quote([f"NFO:{ce_symbol}", f"NFO:{pe_symbol}"])

            ce_price = option_data[f"NFO:{ce_symbol}"]["last_price"]
            pe_price = option_data[f"NFO:{pe_symbol}"]["last_price"]

            ce_vwap = option_data[f"NFO:{ce_symbol}"].get("average_price", None)
            pe_vwap = option_data[f"NFO:{pe_symbol}"].get("average_price", None)

            ce_volume = option_data[f"NFO:{ce_symbol}"].get("volume", 0)
            pe_volume = option_data[f"NFO:{pe_symbol}"].get("volume", 0)

            ce_vwma = round(ce_vwap * ce_volume / max(ce_volume, 1), 2) if ce_vwap else "VWMA not available"
            pe_vwma = round(pe_vwap * pe_volume / max(pe_volume, 1), 2) if pe_vwap else "VWMA not available"

            print("\n--- Live NIFTY 50 Market Data ---")
            print(f"NIFTY 50 Index Value  : {nifty_price}")
            print(f"ATM Strike Price      : {atm_strike}")
            print(f"ATM CE Value ({ce_symbol}): {ce_price}")
            print(f"ATM PE Value ({pe_symbol}): {pe_price}")
            print(f"VWAP CE ({ce_symbol})  : {ce_vwap if ce_vwap else 'VWAP not available'}")
            print(f"VWAP PE ({pe_symbol})  : {pe_vwap if pe_vwap else 'VWAP not available'}")
            print(f"VWMA CE ({ce_symbol})  : {ce_vwma}")
            print(f"VWMA PE ({pe_symbol})  : {pe_vwma}")

            time.sleep(1)  

        except KeyboardInterrupt:
            print("\nNIFTY 50 data fetching stopped.")
            break
        except Exception as e:
            print(f"⚠️ Error: {e}")
            time.sleep(1) 

if __name__ == "__main__":
    fetch_nifty_data()
