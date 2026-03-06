import os
from dotenv import load_dotenv
from supabase import create_client, Client
from datetime import datetime, timezone

load_dotenv()

supabase: Client = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

def load_crypto_data(records):
    if not records:
        print("No records to load")
        return

    try:
        for record in records:
            data = {
                "coin_id": record["id"],
                "symbol": record["symbol"],
                "name": record["name"],
                "current_price": record["current_price"],
                "market_cap": record["market_cap"],
                "total_volume": record["total_volume"],
                "price_change_24h": record["price_change_24h"],
                "market_cap_rank": int(record["market_cap_rank"]),
                "volatility_score": record["volatility_score"],
                "extracted_at": record["extracted_at"]
            }
            supabase.table("crypto_market").upsert(
                data,
                on_conflict="coin_id"
            ).execute()

        print(f"Loaded {len(records)} records into database successfully!")

    except Exception as e:
        print(f"Load failed: {e}")

if __name__ == "__main__":
    from extract import extract_crypto_data
    from transform import transform_crypto_data
    raw = extract_crypto_data()
    records = transform_crypto_data(raw)
    load_crypto_data(records)
