import requests
import json
import os
from datetime import datetime

def extract_crypto_data():
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {
        "vs_currency": "usd",
        "order": "market_cap_desc",
        "per_page": 20,
        "page": 1,
        "sparkline": False
    }
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        with open("raw_data.json", "w") as f:
            json.dump(data, f, indent=2)
        print(f"Extracted {len(data)} coins successfully!")
        return data
    except requests.exceptions.RequestException as e:
        print(f"Extraction failed: {e}")
        return []

if __name__ == "__main__":
    data = extract_crypto_data()
    print(data[0])
