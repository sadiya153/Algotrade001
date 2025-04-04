import pandas as pd
import time
import os
from kiteconnect import KiteConnect
import config

kite = KiteConnect(api_key=config.API_KEY)
kite.set_access_token(config.ACCESS_TOKEN)

CSV_FILE = "/Users/sadiya/Desktop/Desktop - Sadiya’s MacBook Air/Algotrade001/nifftyy_data.csv"
LOG_FILE = "buy.txt" 

logged_timestamps = set()

def log_message(message, timestamp):
   
    if timestamp in logged_timestamps:
        return  

    with open(LOG_FILE, "a") as log_file:
        log_file.write(f"{message}\n")
    print(message)  # Also print to console

    logged_timestamps.add(timestamp)  # Store logged timestamp

def read_csv():
    try:
        df = pd.read_csv(CSV_FILE)
        return df
    except FileNotFoundError:
        print(f"File not found: {CSV_FILE}. Waiting for next update...")
        return None
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return None

def should_buy(previous_row, current_row):
    ce_price = current_row["ce_price"]
    ce_vwap = current_row["ce_vwap"]
    ce_vwma = current_row["ce_vwma"]
    super_trend_ce = current_row["super_trend_ce"]

    prev_ce_price = previous_row["ce_price"]

    buy_signal = None

    if prev_ce_price < ce_vwap and ce_price > ce_vwap:
        buy_signal = "BUY CALL - CE price crossed above VWAP"
    elif prev_ce_price < ce_vwma and ce_price > ce_vwma:
        buy_signal = "BUY CALL - CE price crossed above VWMA"
    elif prev_ce_price < super_trend_ce and ce_price > super_trend_ce:
        buy_signal = "BUY CALL - CE price crossed above SuperTrend"

    return buy_signal

def trade_bot():
    print("\nStarting Buy Bot...\n")

    while True:
        df = read_csv()
        if df is None or len(df) < 2:
            print("Not enough data found in CSV. Waiting for next update...\n")
            time.sleep(10)  # Wait before checking again
            continue

        # Check for crossing condition
        for i in range(1, len(df)):  # Loop through all rows
            previous_row = df.iloc[i - 1]
            current_row = df.iloc[i]
            timestamp = current_row["timestamp"]

            # Print the row used for checking
            print("\nLatest Row Used for Checking:")
            print(current_row.to_string(), "\n")

            buy_signal = should_buy(previous_row, current_row)
            if buy_signal:
                log_message(f"[{timestamp}] {buy_signal}", timestamp)
            else:
                print("No Buy Signal.\n")

        time.sleep(60)  # Wait before checking the next update

if __name__ == "__main__":
    try:
        trade_bot()
    except KeyboardInterrupt:
        print("\n Buy bot stopped manually.")
