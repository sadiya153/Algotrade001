from kiteconnect import KiteConnect
import time
from datetime import datetime, timedelta


# Initialize KiteConnect API
API_KEY = "tvvurc35y2qhc26f"
API_SECRET = "ib0skvn0vood7w5v5bezfigx5paa87gq"
ACCESS_TOKEN = "vH4LGjXd6DCK8Lj0khYg3v9kndvigXqD"
REQUEST_TOKEN = "nHO7osfA7aY3IIMJj4Uvu7ZuGBxs5YDj"

kite = KiteConnect(api_key=API_KEY)

# Generate session and get access token
request_token = REQUEST_TOKEN  # Obtain this from the login flow

# Set the access token
kite.set_access_token(ACCESS_TOKEN)

# Example: Fetch user profile
try:
    profile = kite.profile()

    # Fetch Nifty50 live value
    instruments = kite.instruments("NSE")
    while 1:
        nifty50_instrument = next((item for item in instruments if item["tradingsymbol"] == "NIFTY 50"), None)
        if not nifty50_instrument:
            print("Debug: Instruments fetched:", instruments[:5])  # Print the first 5 instruments for debugging

        if nifty50_instrument:
            print("Nifty50 instrument found.")
        else:
            print("Nifty50 instrument not found. Please check if the market is open or if the tradingsymbol is correct.")
            
            
        # Fetch 1-minute historical data for Nifty50
        if nifty50_instrument:

            # Define the time range for the last 1 minute
            to_date = datetime.now()
            from_date = to_date - timedelta(minutes=1)

            # Fetch historical data
            historical_data = kite.historical_data(
            instrument_token=nifty50_instrument["instrument_token"],
            from_date=from_date,
            to_date=to_date,
            interval="minute"
            )

            if historical_data:
                print("Nifty50 1-Minute Data:", historical_data[-1])  # Print the latest 1-minute data
            else:
                print("No 1-minute data available for Nifty50.")

        time.sleep(5)

    print("User Profile:", profile)
except Exception as e:
    print("Error fetching profile:", e)