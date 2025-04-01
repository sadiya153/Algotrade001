import time
import pandas as pd
from datetime import datetime  
from kiteconnect import KiteConnect
import config
from csv_writer import write_to_csv  # Import the function from csv_writer.py

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

def calculate_super_trend(df, period=10, multiplier=3):
    high = df["high"]
    low = df["low"]
    close = df["close"]

    df["TR"] = pd.concat([high - low, abs(high - close.shift()), abs(low - close.shift())], axis=1).max(axis=1)
    df["ATR"] = df["TR"].rolling(window=period).mean()

    df["Upper_Band"] = (high + low) / 2 + (multiplier * df["ATR"])
    df["Lower_Band"] = (high + low) / 2 - (multiplier * df["ATR"])

    df["SuperTrend"] = df["Upper_Band"]

    for i in range(1, len(df)):
        if close.iloc[i - 1] > df.loc[i - 1, "SuperTrend"]:
            df.loc[i, "SuperTrend"] = min(df.loc[i, "Upper_Band"], df.loc[i - 1, "SuperTrend"])
        else:
            df.loc[i, "SuperTrend"] = max(df.loc[i, "Lower_Band"], df.loc[i - 1, "SuperTrend"])

    return df["SuperTrend"].iloc[-1] 


def fetch_nifty_data():
    print("\nFetching live data for NIFTY 50...\n")
    
    while True:
        try:
            quote = kite.quote("NSE:NIFTY 50")
            nifty_price = quote["NSE:NIFTY 50"]["last_price"]

            atm_strike = get_nearest_strike_price(nifty_price)

            ce_symbol, ce_token = get_option_symbol(atm_strike, "CE")
            pe_symbol, pe_token = get_option_symbol(atm_strike, "PE")

            if not ce_symbol or not pe_symbol:
                print(f"No valid option contracts found for ATM {atm_strike}. Retrying...")
                time.sleep(1)
                continue

            option_data = kite.quote([f"NFO:{ce_symbol}", f"NFO:{pe_symbol}"])

            ce_price = option_data[f"NFO:{ce_symbol}"]["last_price"]
            pe_price = option_data[f"NFO:{pe_symbol}"]["last_price"]

            ce_vwap = option_data[f"NFO:{ce_symbol}"].get("average_price", "VWAP not available")
            pe_vwap = option_data[f"NFO:{pe_symbol}"].get("average_price", "VWAP not available")

            ce_volume = option_data[f"NFO:{ce_symbol}"].get("volume", 0)
            pe_volume = option_data[f"NFO:{pe_symbol}"].get("volume", 0)

            ce_vwma = round(ce_vwap * ce_volume / max(ce_volume, 1), 2) if isinstance(ce_vwap, (int, float)) else ce_vwap
            pe_vwma = round(pe_vwap * pe_volume / max(pe_volume, 1), 2) if isinstance(pe_vwap, (int, float)) else pe_vwap

            interval = "minute"
            from_date = pd.Timestamp.now() - pd.Timedelta(minutes=10)
            to_date = pd.Timestamp.now()

            try:
                ce_historical = kite.historical_data(ce_token, from_date, to_date, interval)
                pe_historical = kite.historical_data(pe_token, from_date, to_date, interval)

                ce_df = pd.DataFrame(ce_historical)
                pe_df = pd.DataFrame(pe_historical)

                if not ce_df.empty and not pe_df.empty:
                    super_trend_ce = calculate_super_trend(ce_df)
                    super_trend_pe = calculate_super_trend(pe_df)
                else:
                    super_trend_ce = "Super Trend not available"
                    super_trend_pe = "Super Trend not available"

            except Exception as e:
                print(f"Error fetching historical data: {e}")
                super_trend_ce = "Super Trend not available"
                super_trend_pe = "Super Trend not available"

            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Print data to console (optional)
            print("\n--- Live NIFTY 50 Market Data ---")
            print(f"Current Time           : {current_time}")
            print(f"NIFTY 50 Index Value   : {nifty_price}")
            print(f"ATM Strike Price       : {atm_strike}")
            print(f"ATM CE Value ({ce_symbol}): {ce_price}")
            print(f"ATM PE Value ({pe_symbol}): {pe_price}")
            print(f"VWAP CE ({ce_symbol})  : {ce_vwap}")
            print(f"VWAP PE ({pe_symbol})  : {pe_vwap}")
            print(f"VWMA CE ({ce_symbol})  : {ce_vwma}")
            print(f"VWMA PE ({pe_symbol})  : {pe_vwma}")
            print(f"Super Trend CE ({ce_symbol})  : {super_trend_ce}")
            print(f"Super Trend PE ({pe_symbol})  : {super_trend_pe}")

            # Prepare data to write to CSV
            data = {
                "timestamp": current_time,
                "nifty_value": nifty_price,
                "atm_strike": atm_strike,
                "ce_price": ce_price,
                "pe_price": pe_price,
                "ce_vwap": ce_vwap,
                "pe_vwap": pe_vwap,
                "ce_vwma": ce_vwma,
                "pe_vwma": pe_vwma,
                "super_trend_ce": super_trend_ce,
                "super_trend_pe": super_trend_pe
            }

            write_to_csv(data)  # Write data to CSV

            time.sleep(1)  # Wait for 1 second before fetching new data

        except KeyboardInterrupt:
            print("\nNIFTY 50 data fetching stopped.")
            break
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(1)

if __name__ == "__main__":
    fetch_nifty_data()
