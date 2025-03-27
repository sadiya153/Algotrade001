import time
from kiteconnect import KiteConnect
import config

kite = KiteConnect(api_key=config.API_KEY)
kite.set_access_token(config.ACCESS_TOKEN)

def get_nearest_strike_price(price, step=100):
    return round(price / step) * step

def get_option_symbol(atm_strike, option_type):
    instruments = kite.instruments("NFO")
    for instrument in instruments:
        if "BANKNIFTY" in instrument["tradingsymbol"] and str(atm_strike) in instrument["tradingsymbol"] and option_type in instrument["tradingsymbol"]:
            return instrument["tradingsymbol"]
    return None

def fetch_banknifty_data():
    print("\nFetching live data for BANK NIFTY...\n")

    while True:
        try:
           
            quote = kite.ltp("NSE:NIFTY BANK")

            banknifty_price = quote["NSE:NIFTY BANK"]["last_price"]

            atm_strike = get_nearest_strike_price(banknifty_price)
            ce_symbol = get_option_symbol(atm_strike, "CE")
            pe_symbol = get_option_symbol(atm_strike, "PE")

            if not ce_symbol or not pe_symbol:
                print(f"No valid option contracts found for ATM {atm_strike}. Retrying...")
                time.sleep(5)
                continue

            option_data = kite.ltp([f"NFO:{ce_symbol}", f"NFO:{pe_symbol}"])
            ce_price = option_data[f"NFO:{ce_symbol}"]["last_price"]
            pe_price = option_data[f"NFO:{pe_symbol}"]["last_price"]

            print("\n--- Live BANK NIFTY Market Data ---")
            print(f"BANK NIFTY Index Value : {banknifty_price}")
            print(f"ATM Strike Price      : {atm_strike}")
            print(f"ATM CE Value ({ce_symbol}): {ce_price}")
            print(f"ATM PE Value ({pe_symbol}): {pe_price}")

            time.sleep(1)

        except KeyboardInterrupt:
            print("\nBANK NIFTY data fetching stopped.")
            break
        
       

        # except KeyboardInterrupt:
        #     print("\nBANK NIFTY data fetching stopped.")
        #     break
        # except Exception as e:
        #     print(f"Error: {e}")
        #     time.sleep(5)

