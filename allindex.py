
import time

from kiteconnect import KiteConnect

import config
 
# Initialize Kite API

kite = KiteConnect(api_key=config.API_KEY)

kite.set_access_token(config.ACCESS_TOKEN)
 
# Define index symbols and their correct exchange codes

INDEX_MAPPING = {

    "1": ("NIFTY 50", "NSE", "NIFTY"),

    "2": ("BANKNIFTY", "NSE", "BANKNIFTY"),

    "3": ("SENSEX", "BSE", "SENSEX"),

    "4": ("FINNIFTY", "NSE", "FINNIFTY"),

    "5": ("BANKEX", "BSE", "BANKEX"),

    "6": "ALL"

}
 
def get_nearest_strike(price, step=50):

    """Calculate the nearest ATM strike price."""

    return round(price / step) * step
 
def get_option_symbol(index, atm_strike, option_type):

    """Find the correct CE/PE option contract symbol."""

    try:

        instruments = kite.instruments("NFO")

        for instrument in instruments:

            if (index in instrument["tradingsymbol"] and

                str(atm_strike) in instrument["tradingsymbol"] and

                instrument["instrument_type"] == option_type):

                return instrument["tradingsymbol"]

    except Exception as e:

        print(f"Error fetching option symbol: {e}")

    return None
 
def fetch_live_data(symbol, exchange, option_symbol):

    """Fetch live index price and ATM options prices."""

    try:

        # Fetch index price

        quote = kite.ltp(f"{exchange}:{symbol}")

        index_price = quote[f"{exchange}:{symbol}"]["last_price"]

        # Calculate ATM strike price

        atm_strike = get_nearest_strike(index_price)

        # Get CE and PE symbols

        ce_symbol = get_option_symbol(option_symbol, atm_strike, "CE")

        pe_symbol = get_option_symbol(option_symbol, atm_strike, "PE")
 
        if not ce_symbol or not pe_symbol:

            print(f"No valid option contracts found for {symbol} at {atm_strike}. Skipping...")

            return index_price, atm_strike, None, None
 
        # Fetch option prices

        option_data = kite.ltp([f"NFO:{ce_symbol}", f"NFO:{pe_symbol}"])

        ce_price = option_data.get(f"NFO:{ce_symbol}", {}).get("last_price")

        pe_price = option_data.get(f"NFO:{pe_symbol}", {}).get("last_price")
 
        return index_price, atm_strike, ce_price, pe_price
 
    except Exception as e:

        print(f"Error fetching data for {symbol}: {e}")

        return None, None, None, None
 
def display_data(choice):

    """Fetch and display live market data."""

    if choice == "6":  # ALL INDICES

        print("\n Live Market Data:")

        print("Index       Index Value     ATM Strike  ATM CE Value  ATM PE Value  ")

        print("===============================================================")

        for key in INDEX_MAPPING:

            if key == "6":

                continue

            index_name, exchange, option_symbol = INDEX_MAPPING[key]

            index_price, atm_strike, ce_price, pe_price = fetch_live_data(index_name, exchange, option_symbol)
 
            # Handle None values properly

            index_price = index_price if index_price is not None else "N/A"

            atm_strike = atm_strike if atm_strike is not None else "N/A"

            ce_price = ce_price if ce_price is not None else "N/A"

            pe_price = pe_price if pe_price is not None else "N/A"
 
            print(f"{index_name:<12}{index_price:<15.2f}{atm_strike:<12.1f}{ce_price:<12.1f}{pe_price:<12.1f}")
 
    else:

        index_name, exchange, option_symbol = INDEX_MAPPING[choice]

        index_price, atm_strike, ce_price, pe_price = fetch_live_data(index_name, exchange, option_symbol)
 
        print(f"\n Live Data for {index_name}:")

        print(f" Index Value: {index_price if index_price is not None else 'N/A':.2f}")

        print(f" ATM Strike Price: {atm_strike if atm_strike is not None else 'N/A':.1f}")

        print(f" ATM CE Value: {ce_price if ce_price is not None else 'N/A':.1f}")

        print(f" ATM PE Value: {pe_price if pe_price is not None else 'N/A':.1f}")
 
def main():

    """Main function to display menu and fetch data."""

    while True:

        print("\n Select an index to fetch live data:")

        print("1 - NIFTY 50")

        print("2 - BANKNIFTY")

        print("3 - SENSEX")

        print("4 - FINNIFTY")

        print("5 - BANKEX")

        print("6 - ALL INDICES")

        print("7 - EXIT")

        choice = input("Enter choice (1-7): ")
 
        if choice == "7":

            print(" Exiting program. Have a great day!")

            break

        elif choice in INDEX_MAPPING:

            display_data(choice)

        else:

            print(" Invalid choice. Try again.")
 
# Run the program

main()
 