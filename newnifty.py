import time
import csv
import os
import pandas as pd
from datetime import datetime, timedelta
from kiteconnect import KiteConnect
import config
 
kite = KiteConnect(api_key=config.API_KEY)
kite.set_access_token(config.ACCESS_TOKEN)
 
all_instruments = pd.DataFrame(kite.instruments("NFO"))
 
def get_nearest_strike_price(price, step=50):
    return round(price / step) * step
 
def get_option_symbol(atm_strike, option_type):
    option_row = all_instruments[
        (all_instruments["tradingsymbol"].str.startswith("NIFTY")) &
        (all_instruments["tradingsymbol"].str.contains(str(atm_strike))) &
        (all_instruments["tradingsymbol"].str.endswith(option_type))
    ]
    if not option_row.empty:
        tradingsymbol = option_row.iloc[0]["tradingsymbol"]
        instrument_token = int(option_row.iloc[0]["instrument_token"])
        return tradingsymbol, instrument_token
    return None, None
 
def wait_until_next_minute():
    now = datetime.now()
    next_minute = (now + timedelta(minutes=1)).replace(second=0, microsecond=0)
    wait_time = (next_minute - now).total_seconds()
    time.sleep(wait_time)
 
def write_to_csv(data, filename="nifttyy.csv"):
    file_exists = os.path.isfile(filename)
    with open(filename, mode='a', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=data.keys())
        if not file_exists:
            writer.writeheader()
        writer.writerow(data)
 
def fetch_nifty_data():
    print("\nFetching live NIFTY 50 data...\n")
    wait_until_next_minute()
 
    while True:
        try:
            interval = "minute"
            from_date = pd.Timestamp.now() - pd.Timedelta(minutes=10)
            to_date = pd.Timestamp.now()
 
            nifty_historical = kite.historical_data(256265, from_date, to_date, interval)
            nifty_df = pd.DataFrame(nifty_historical)
 
            if nifty_df.empty:
                print("No data for NIFTY 50. Retrying...")
                time.sleep(5)
                continue
 
            last_candle = nifty_df.iloc[-1]
            nifty_price = last_candle["close"]
            nifty_open = last_candle["open"]
            nifty_high = last_candle["high"]
            nifty_low = last_candle["low"]
            nifty_close = last_candle["close"]
 
            atm_strike = get_nearest_strike_price(nifty_price)
 
            ce_symbol, ce_token = get_option_symbol(atm_strike, "CE")
            pe_symbol, pe_token = get_option_symbol(atm_strike, "PE")
 
            if not ce_symbol or not pe_symbol:
                print(f"No valid option contracts found for ATM {atm_strike}. Retrying...")
                time.sleep(60)
                continue
 
            option_data = kite.quote([f"NFO:{ce_symbol}", f"NFO:{pe_symbol}"])
 
            ce_price = option_data[f"NFO:{ce_symbol}"]["last_price"]
            pe_price = option_data[f"NFO:{pe_symbol}"]["last_price"]
 
            ce_vwap = option_data[f"NFO:{ce_symbol}"].get("average_price", "N/A")
            pe_vwap = option_data[f"NFO:{pe_symbol}"].get("average_price", "N/A")
 
            current_time = datetime.now().replace(second=0, microsecond=0).strftime("%Y-%m-%d %H:%M:%S")
 
            print("\n" + " " * 32 + "--- Live NIFTY 50 Market Data ---")
            print(f"{' ' * 28}Current Time           : {current_time}")
            print(f"{' ' * 28}NIFTY 50 Index Value   : {nifty_price}")
            print(f"{' ' * 28}ATM Strike Price       : {atm_strike}\n")
            print(f"Open Price             : {nifty_open}")
            print(f"High Price             : {nifty_high}")
            print(f"Low Price              : {nifty_low}")
            print(f"Close Price            : {nifty_close}")
            print(f"ATM CE Value ({ce_symbol}): {str(ce_price):<20} | ATM PE Value ({pe_symbol}): {pe_price}")
            print(f"VWAP CE                : {str(ce_vwap):<20}          | VWAP PE                : {pe_vwap}")
 
            data = {
                "timestamp": current_time,
                "nifty_value": nifty_price,
                "atm_strike": atm_strike,
                "open": nifty_open,
                "high": nifty_high,
                "low": nifty_low,
                "close": nifty_close,
                "ce_price": ce_price,
                "pe_price": pe_price,
                "ce_vwap": ce_vwap,
                "pe_vwap": pe_vwap
            }
 
            write_to_csv(data)
 
            wait_until_next_minute()
 
        except KeyboardInterrupt:
            print("\nStopped by user.")
            break
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(5)
 
if __name__ == "__main__":
    fetch_nifty_data()

    # Calculate VWMA (Volume Weighted Moving Average) for CE and PE
    def calculate_vwma(data, price_key, vwap_key, period=10):
        if len(data) < period:
            return None
        weighted_sum = sum(row[price_key] * row[vwap_key] for row in data[-period:])
        volume_sum = sum(row[vwap_key] for row in data[-period:])
        return weighted_sum / volume_sum if volume_sum != 0 else None

    # Read the CSV file to calculate VWMA
    try:
        historical_data = pd.read_csv("nifttyy.csv")
        vwma_ce = calculate_vwma(historical_data.to_dict('records'), "ce_price", "ce_vwap")
        vwma_pe = calculate_vwma(historical_data.to_dict('records'), "pe_price", "pe_vwap")

        print("\n" + " " * 32 + "--- VWMA Indicator ---")
        print(f"{' ' * 28}VWMA CE: {vwma_ce}")
        print(f"{' ' * 28}VWMA PE: {vwma_pe}")
    except Exception as e:
        print(f"Error calculating VWMA: {e}")
        # Calculate and display VWMA after each data fetch
        try:
            historical_data = pd.read_csv("nifttyy.csv")
            vwma_ce = calculate_vwma(historical_data.to_dict('records'), "ce_price", "ce_vwap")
            vwma_pe = calculate_vwma(historical_data.to_dict('records'), "pe_price", "pe_vwap")

            print("\n" + " " * 32 + "--- VWMA Indicator ---")
            print(f"{' ' * 28}VWMA CE: {vwma_ce}")
            print(f"{' ' * 28}VWMA PE: {vwma_pe}")
        except Exception as e:
            print(f"Error calculating VWMA: {e}")
            # Calculate and display VWMA after each data fetch
            try:
                historical_data = pd.read_csv("nifttyy.csv")
                vwma_ce = calculate_vwma(historical_data.to_dict('records'), "ce_price", "ce_vwap")
                vwma_pe = calculate_vwma(historical_data.to_dict('records'), "pe_price", "pe_vwap")

                print(f"VWMA CE                : {str(vwma_ce):<20}          | VWMA PE                : {vwma_pe}")
            except Exception as e:
                print(f"Error calculating VWMA: {e}")