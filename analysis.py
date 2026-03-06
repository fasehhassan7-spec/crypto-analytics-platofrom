import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

supabase: Client = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

def get_top_gainers():
    response = supabase.table("crypto_market")\
        .select("name, symbol, price_change_24h, current_price")\
        .order("price_change_24h", desc=True)\
        .limit(5)\
        .execute()
    return response.data

def get_top_by_market_cap():
    response = supabase.table("crypto_market")\
        .select("name, symbol, market_cap, current_price")\
        .order("market_cap", desc=True)\
        .limit(5)\
        .execute()
    return response.data

def get_average_market_cap():
    response = supabase.table("crypto_market")\
        .select("market_cap")\
        .execute()
    caps = [r["market_cap"] for r in response.data if r["market_cap"]]
    return sum(caps) / len(caps) if caps else 0

def get_total_market_value():
    response = supabase.table("crypto_market")\
        .select("market_cap")\
        .execute()
    return sum(r["market_cap"] for r in response.data if r["market_cap"])

def get_volatility_ranking():
    response = supabase.table("crypto_market")\
        .select("name, symbol, volatility_score")\
        .order("volatility_score", desc=True)\
        .limit(10)\
        .execute()
    return response.data

if __name__ == "__main__":
    print("Top 5 Gainers:")
    for coin in get_top_gainers():
        print(f"  {coin['name']}: {coin['price_change_24h']:.2f}%")

    print("\nTop 5 by Market Cap:")
    for coin in get_top_by_market_cap():
        print(f"  {coin['name']}: ${coin['market_cap']:,}")

    print(f"\nAverage Market Cap: ${get_average_market_cap():,.2f}")
    print(f"Total Market Value: ${get_total_market_value():,.2f}")

    print("\nVolatility Ranking:")
    for coin in get_volatility_ranking():
        print(f"  {coin['name']}: {coin['volatility_score']:.2f}")
