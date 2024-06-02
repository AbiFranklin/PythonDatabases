import requests
from headers import headers  # Import custom headers for the API request

# Base asset ID (e.g., Bitcoin)
asset_id_base = 'btc'

# Quote asset ID (e.g., US Dollar)
asset_id_quote = 'usd'

# Construct the URL for the API request using the base and quote asset IDs
url = f"https://rest.coinapi.io/v1/exchangerate/{asset_id_base}/{asset_id_quote}"

# Make a GET request to the API and parse the response as JSON
data = requests.get(url, headers=headers).json()

# Extract the exchange rate from the response data
rate = data["rate"]

# Print the exchange rate
print(rate)
