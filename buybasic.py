import pandas as pd
import time
from kiteconnect import KiteConnect
import config

kite = KiteConnect(api_key=config.API_KEY)
kite.set_access_token(config.ACCESS_TOKEN)

CSV_FILE = "nifttyy_data.csv"
LOG_FILE = "buy.txt"


def trade_bot():
    vwap = float(input("\nEnter VWAP value: "))
    vwma = float(input("\nEnter VWMA value: "))
    st = float(input("\nEnter ST value: "))
    val = float(input("\nEnter VAL: "))

    if val < vwap and val < vwma and val < st:
        print("BUY CALL")
    elif val > vwap and val > vwma and val > st:
        print("BUY PUT")
    else:
        print("NO PUT/CALL")

if __name__ == "__main__":
    trade_bot()
