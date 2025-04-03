from kiteconnect import KiteConnect
import pandas as pd
#import pandas_ta as ta
 
# Zerodha API credentials
API_KEY = "tvvurc35y2qhc26f"
ACCESS_TOKEN = "K6YiueNMbdB7mmMUyhLQbZtfLSx0SxQp"
 
# Initialize KiteConnect
kite = KiteConnect(api_key=API_KEY)
kite.set_access_token(ACCESS_TOKEN)
 
# Nifty 50 instrument token (check on Zerodha API)
NIFTY50_TOKEN = 256265  # Instrument token for Nifty 50
INTERVAL = "5minute"  # 5-minute candle
LOOKBACK = 100  # Number of historical candles to fetch
 
# Fetch historical data from Kite API
def fetch_data():
    df = pd.DataFrame(kite.historical_data(NIFTY50_TOKEN,
                                           pd.Timestamp.now() - pd.Timedelta(days=1),
                                           pd.Timestamp.now(),
                                           INTERVAL))
    df["timestamp"] = pd.to_datetime(df["date"])
    df.set_index("timestamp", inplace=True)
    return df
 
# Calculate indicators
def calculate_indicators(df):
    df["VWAP"] = ta.vwap(df["high"], df["low"], df["close"], df["volume"])
    df["VWMA"] = ta.vwma(df["close"], df["volume"])
    df["SuperTrend"] = ta.supertrend(df["high"], df["low"], df["close"])["SUPERT_7_3.0"]
    return df
 
# Generate Buy/Sell signals
def generate_signals(df):
    buy_signals, sell_signals = [], []
 
    for i in range(1, len(df)):
        close = df["close"].iloc[i]
        prev_close = df["close"].iloc[i - 1]
 
        # Buy Condition: If the last candle closes above any indicator
        if prev_close <= df["VWAP"].iloc[i - 1] and close > df["VWAP"].iloc[i]:
            buy_signals.append(f"BUY at {close} (VWAP breakout)")
        elif prev_close <= df["VWMA"].iloc[i - 1] and close > df["VWMA"].iloc[i]:
            buy_signals.append(f"BUY at {close} (VWMA breakout)")
        elif prev_close <= df["SuperTrend"].iloc[i - 1] and close > df["SuperTrend"].iloc[i]:
            buy_signals.append(f"BUY at {close} (SuperTrend breakout)")
 
        # Sell Condition: If the last candle closes below all indicators
        if close < df["VWAP"].iloc[i] and close < df["VWMA"].iloc[i] and close < df["SuperTrend"].iloc[i]:
            sell_signals.append(f"SELL at {close}")
 
    return buy_signals, sell_signals
 
# Main function
def main():
    df = fetch_data()
    df = calculate_indicators(df)
 
    buy_signals, sell_signals = generate_signals(df)
 
    print("\nBUY Signals:")
    for signal in buy_signals:
        print(signal)
 
    print("\nSELL Signals:")
    for signal in sell_signals:
        print(signal)
 
# Run the script
if __name__ == "__main__":
    main()
 