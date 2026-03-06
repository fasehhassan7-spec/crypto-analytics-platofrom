import pandas as pd
from datetime import datetime

def transform_crypto_data(raw_data):
    if not raw_data:
        print("No data to transform")
        return []

    df = pd.DataFrame(raw_data)

    columns_needed = [
        "id", "symbol", "name", "current_price",
        "market_cap", "total_volume", "price_change_24h", "market_cap_rank"
    ]
    df = df[columns_needed]

    df = df.dropna()

    df["current_price"] = pd.to_numeric(df["current_price"], errors="coerce")
    df["market_cap"] = pd.to_numeric(df["market_cap"], errors="coerce")
    df["total_volume"] = pd.to_numeric(df["total_volume"], errors="coerce")
    df["price_change_24h"] = pd.to_numeric(df["price_change_24h"], errors="coerce")
    df["market_cap_rank"] = pd.to_numeric(df["market_cap_rank"], errors="coerce")

    df["volatility_score"] = abs(df["price_change_24h"]) * df["total_volume"]

    df["extracted_at"] = datetime.utcnow().isoformat()

    df = df.dropna()

    records = df.to_dict(orient="records")
    print(f"Transformed {len(records)} records successfully!")
    return records

if __name__ == "__main__":
    from extract import extract_crypto_data
    raw = extract_crypto_data()
    records = transform_crypto_data(raw)
    print(records[0])

