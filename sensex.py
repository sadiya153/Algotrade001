import time
from kiteconnect import KiteConnect
import config

kite = KiteConnect(api_key=config.API_KEY)
kite.set_access_token(config.ACCESS_TOKEN)

def get_instrument_token(symbol, exchange="BSE"):
    instruments = kite.instruments(exchange)
    for instrument in instruments:
        if instrument["tradingsymbol"] == symbol:
            return instrument["instrument_token"]
    print(f"⚠️ Instrument token not found for {symbol}")
    return None

def get_nearest_strike_price(price, step=100):
    return round(price / step) * step

def get_option_symbol(atm_strike, option_type):
    instruments = kite.instruments("BFO")
    for instrument in instruments:
        if "SENSEX" in instrument["tradingsymbol"] and str(atm_strike) in instrument["tradingsymbol"] and option_type in instrument["tradingsymbol"]:
            return instrument["tradingsymbol"]
    return None

def fetch_live_sensex_data():
    symbol = "SENSEX"
    exchange = "BSE"

    print(f"\nFetching live data for {symbol}...\n")

    while True:
        try:
            quote = kite.ltp(f"{exchange}:{symbol}")
            sensex_price = quote[f"{exchange}:{symbol}"]["last_price"]
            atm_strike = get_nearest_strike_price(sensex_price, step=100)

            ce_symbol = get_option_symbol(atm_strike, "CE")
            pe_symbol = get_option_symbol(atm_strike, "PE")

            if not ce_symbol or not pe_symbol:
                print(f"⚠️ No valid option contracts found for ATM {atm_strike}. Retrying...")
                time.sleep(5)
                continue

            option_data = kite.ltp([f"BFO:{ce_symbol}", f"BFO:{pe_symbol}"])

            ce_price = option_data[f"BFO:{ce_symbol}"]["last_price"]
            pe_price = option_data[f"BFO:{pe_symbol}"]["last_price"]

            print("\n--- Live Market Data ---")
            print(f"SENSEX Index Value  : {sensex_price}")
            print(f"ATM Strike Price    : {atm_strike}")
            print(f"ATM CE Value ({ce_symbol}): {ce_price}")
            print(f"ATM PE Value ({pe_symbol}): {pe_price}")

            time.sleep(1)

        except KeyboardInterrupt:
            while True:
                choice = input("\nDo you want to exit? (Yes/No): ").strip().lower()
                if choice == "yes":
                    print("\nExiting.")
                    return
                elif choice == "no":
                    print("\nResuming data fetching...\n")
                    break
                else:
                    print("Invalid input! Please enter 'Yes' or 'No'.")

        except Exception as e:
            print(f"Error fetching data: {e}")
            time.sleep(5)

fetch_live_sensex_data()
