# nifty50.py
import time
from kiteconnect import KiteConnect
import config

# Initialize Kite API
kite = KiteConnect(api_key=config.API_KEY)
kite.set_access_token(config.ACCESS_TOKEN)

# Function to find the nearest strike price
def get_nearest_strike_price(price, step=50):
    return round(price / step) * step

# Function to find option symbols for ATM CE/PE
def get_option_symbol(atm_strike, option_type):
    instruments = kite.instruments("NFO")
    for instrument in instruments:
        if f"NIFTY" in instrument["tradingsymbol"] and str(atm_strike) in instrument["tradingsymbol"] and option_type in instrument["tradingsymbol"]:
            return instrument["tradingsymbol"]
    return None

# Function to fetch live NIFTY 50 data
def fetch_nifty50_data():
    print("\nFetching live data for NIFTY 50...\n")

    while True:
        try:
            # Fetch index value
            quote = kite.ltp("NSE:NIFTY 50")
            nifty_price = quote["NSE:NIFTY 50"]["last_price"]

            # Get nearest ATM strike price
            atm_strike = get_nearest_strike_price(nifty_price)

            # Get option symbols for CE and PE
            ce_symbol = get_option_symbol(atm_strike, "CE")
            pe_symbol = get_option_symbol(atm_strike, "PE")

            if not ce_symbol or not pe_symbol:
                print(f"⚠️ No valid option contracts found for ATM {atm_strike}. Retrying...")
                time.sleep(5)
                continue

            # Fetch option prices
            option_data = kite.ltp([f"NFO:{ce_symbol}", f"NFO:{pe_symbol}"])
            ce_price = option_data[f"NFO:{ce_symbol}"]["last_price"]
            pe_price = option_data[f"NFO:{pe_symbol}"]["last_price"]

            # Display values
            print("\n--- Live NIFTY 50 Market Data ---")
            print(f"NIFTY 50 Index Value  : {nifty_price}")
            print(f"ATM Strike Price      : {atm_strike}")
            print(f"ATM CE Value ({ce_symbol}): {ce_price}")
            print(f"ATM PE Value ({pe_symbol}): {pe_price}")

            time.sleep(1)  # Fetch every second

        except KeyboardInterrupt:
            print("\nNIFTY 50 data fetching stopped.")
            break
