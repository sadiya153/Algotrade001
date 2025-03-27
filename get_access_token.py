from kiteconnect import KiteConnect

import webbrowser

import config
 
kite = KiteConnect(api_key=config.API_KEY)
 

login_url = kite.login_url()

print("Login URL:", login_url)

webbrowser.open(login_url)
 

request_token = input("Enter Request Token from URL: ").strip()
 

try:

    data = kite.generate_session(request_token, api_secret=config.API_SECRET)

    access_token = data["access_token"]

    print("Access Token:", access_token)
 


    with open("config.py", "w") as f:

        f.write(f'API_KEY = "{config.API_KEY}"\n')

        f.write(f'API_SECRET = "{config.API_SECRET}"\n')

        f.write(f'ACCESS_TOKEN = "{access_token}"\n')
 
    print("Access token saved successfully!")
 
except Exception as e:

    print(f"Error generating access token: {e}")

 
 