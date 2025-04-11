from kiteconnect import KiteConnect
import time
from datetime import datetime, timedelta
import signal
import sys
import logging
import config

kite = KiteConnect(api_key=config.API_KEY)
kite.set_access_token(config.ACCESS_TOKEN)

log_file = "buySell.txt"

def log_message(msg):
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}: {msg}\n")

def handle_exit(sig, frame):
    log_message("User exited the code")
    sys.exit(0)

signal.signal(signal.SIGINT, handle_exit)

log_message("Log started ")

def round_to_nearest_50(x):
    return int(round(x / 50.0) * 50)

def calculate_vwap(candle):
    return round((candle["high"] + candle["low"] + candle["close"]) / 3, 2)

def get_atm_option_tokens():
    try:
        instruments = kite.instruments("NFO")
        index_price = kite.ltp("NSE:NIFTY 50")["NSE:NIFTY 50"]["last_price"]
        atm_strike = round_to_nearest_50(index_price)

        today = datetime.now().date()
        expiry_dates = sorted(list(set(
            i["expiry"] for i in instruments
            if i["name"] == "NIFTY" and i["expiry"] >= today
        )))

        nearest_expiry = expiry_dates[0]

        ce_token = None
        pe_token = None

        for inst in instruments:
            if (inst["name"] == "NIFTY" and
                inst["expiry"] == nearest_expiry and
                inst["strike"] == atm_strike):
                if inst["instrument_type"] == "CE":
                    ce_token = inst["instrument_token"]
                elif inst["instrument_type"] == "PE":
                    pe_token = inst["instrument_token"]
            if ce_token and pe_token:
                break

        return ce_token, pe_token
    except Exception as e:
        log_message(f"Error in fetching tokens: {e}")
        sys.exit(1)

in_trade = False
entry_price = 0
sl = 0
tp = 0
direction = ""
trade_type = ""

ce_token, pe_token = get_atm_option_tokens()

while True:
    while datetime.now().second != 0:
        time.sleep(0.2)

    now = datetime.now()
    to_time = now
    from_time = to_time - timedelta(minutes=2)

    try:
        ce_data = kite.historical_data(ce_token, from_time, to_time, "minute")
        pe_data = kite.historical_data(pe_token, from_time, to_time, "minute")
    except Exception as e:
        log_message(f"Error fetching data: {str(e)}")
        time.sleep(2)
        continue

    if len(ce_data) < 2 or len(pe_data) < 2:
        log_message("Not enough data yet...")
        time.sleep(2)
        continue

    prev_ce = ce_data[-2]
    curr_ce = ce_data[-1]
    prev_pe = pe_data[-2]
    curr_pe = pe_data[-1]

    prev_ce_close = prev_ce["close"]
    curr_ce_close = curr_ce["close"]
    prev_pe_close = prev_pe["close"]
    curr_pe_close = curr_pe["close"]

    # Calculate VWAP manually
    prev_ce_vwap = calculate_vwap(prev_ce)
    curr_ce_vwap = calculate_vwap(curr_ce)
    prev_pe_vwap = calculate_vwap(prev_pe)
    curr_pe_vwap = calculate_vwap(curr_pe)

    if not in_trade:
        if prev_ce_close < prev_ce_vwap and curr_ce_close > curr_ce_vwap:
            entry_price = curr_ce_close
            sl = round(entry_price * 0.95, 2)
            tp = round(entry_price * 1.10, 2)
            trade_type = "BUY"
            direction = "CALL"
            in_trade = True
            log_message(f"BUY CALL (Cross UP) — Entry: {entry_price}, SL: {sl}, TP: {tp}")
            continue

        if prev_pe_close > prev_pe_vwap and curr_pe_close < curr_pe_vwap:
            entry_price = curr_pe_close
            sl = round(entry_price * 0.95, 2)
            tp = round(entry_price * 1.10, 2)
            trade_type = "BUY"
            direction = "PUT"
            in_trade = True
            log_message(f"BUY PUT (Cross DOWN) — Entry: {entry_price}, SL: {sl}, TP: {tp}")
            continue

        if prev_ce_close > prev_ce_vwap and curr_ce_close < curr_ce_vwap:
            entry_price = curr_ce_close
            sl = round(entry_price * 1.05, 2)
            tp = round(entry_price * 0.90, 2)
            trade_type = "SELL"
            direction = "CALL"
            in_trade = True
            log_message(f"SELL CALL (Cross DOWN) — Entry: {entry_price}, SL: {sl}, TP: {tp}")
            continue

        if prev_pe_close < prev_pe_vwap and curr_pe_close > curr_pe_vwap:
            entry_price = curr_pe_close
            sl = round(entry_price * 1.05, 2)
            tp = round(entry_price * 0.90, 2)
            trade_type = "SELL"
            direction = "PUT"
            in_trade = True
            log_message(f"SELL PUT (Cross UP) — Entry: {entry_price}, SL: {sl}, TP: {tp}")
            continue

    else:
        ltp = curr_ce_close if direction == "CALL" else curr_pe_close

        if trade_type == "BUY":
            if ltp <= sl:
                log_message(f"STOP LOSS Hit — LTP: {ltp}, SL: {sl}, {direction}")
                break
            elif ltp >= tp:
                log_message(f"TARGET Hit — LTP: {ltp}, TP: {tp}, {direction}")
                break
            else:
                log_message(f"Active BUY — {direction}, LTP: {ltp}, SL: {sl}, TP: {tp}")

        elif trade_type == "SELL":
            if ltp >= sl:
                log_message(f"STOP LOSS Hit — LTP: {ltp}, SL: {sl}, {direction}")
                break
            elif ltp <= tp:
                log_message(f"TARGET Hit — LTP: {ltp}, TP: {tp}, {direction}")
                break
            else:
                log_message(f"Active SELL — {direction}, LTP: {ltp}, SL: {sl}, TP: {tp}")

    while datetime.now().second != 0:
        time.sleep(0.2)
