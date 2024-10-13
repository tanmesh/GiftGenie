from apify_client import ApifyClient
import os
from dotenv import load_dotenv

# Initialize the ApifyClient with your API token
load_dotenv()

api_token = os.getenv('APIFY_API_TOKEN')
client = ApifyClient(api_token)

keyword = 'phone charger'
# Prepare the Actor input
run_input = {
    "categoryOrProductUrls": [{ "url": f"https://www.amazon.com/s?k={keyword}" }],
    "maxItemsPerStartUrl": 10,
    "proxyCountry": "AUTO_SELECT_PROXY_COUNTRY",
    "maxOffers": 0,
    "scrapeSellers": False,
    "useCaptchaSolver": False,
    "scrapeProductVariantPrices": False,
}

print(f'Running Actor with input: {run_input}')

# Run the Actor and wait for it to finish
run = client.actor("BG3WDrGdteHgZgbPK").call(run_input=run_input)

# Fetch and print Actor results from the run's dataset (if there are any)
for item in client.dataset(run["defaultDatasetId"]).iterate_items():
    print(item)