# sensex.py
import time
from kiteconnect import KiteConnect
import config

# Initialize Kite API
kite = KiteConnect(api_key=config.API_KEY)
kite.set_access_token(config.ACCESS_TOKEN)

# Function to find the nearest strike price
def get_nearest_strike_price(price, step=100):
    return round(price / step) * step

# Function to find option symbols for ATM CE/PE
def get_option_symbol(atm_strike, option_type):
    instruments = kite.instruments("BFO")
    for instrument in instruments:
        if f"SENSEX" in instrument["tradingsymbol"] and str(atm_strike) in instrument["tradingsymbol"] and option_type in instrument["tradingsymbol"]:
            return instrument["tradingsymbol"]
    return None

# Function to fetch live SENSEX data
def fetch_sensex_data():
    print("\nFetching live data for SENSEX...\n")

    while True:
        try:
            # Fetch index value
            quote = kite.ltp("BSE:SENSEX")
            sensex_price = quote["BSE:SENSEX"]["last_price"]

            # Get nearest ATM strike price
            atm_strike = get_nearest_strike_price(sensex_price)

            # Get option symbols for CE and PE
            ce_symbol = get_option_symbol(atm_strike, "CE")
            pe_symbol = get_option_symbol(atm_strike, "PE")

            if not ce_symbol or not pe_symbol:
                print(f"⚠️ No valid option contracts found for ATM {atm_strike}. Retrying...")
                time.sleep(5)
                continue

            # Fetch option prices
            option_data = kite.ltp([f"BFO:{ce_symbol}", f"BFO:{pe_symbol}"])
            ce_price = option_data[f"BFO:{ce_symbol}"]["last_price"]
            pe_price = option_data[f"BFO:{pe_symbol}"]["last_price"]

            # Display values
            print("\n--- Live SENSEX Market Data ---")
            print(f"SENSEX Index Value    : {sensex_price}")
            print(f"ATM Strike Price      : {atm_strike}")
            print(f"ATM CE Value ({ce_symbol}): {ce_price}")
            print(f"ATM PE Value ({pe_symbol}): {pe_price}")

            time.sleep(1)  # Fetch every second

        except KeyboardInterrupt:
            print("\nSENSEX data fetching stopped.")
            break
