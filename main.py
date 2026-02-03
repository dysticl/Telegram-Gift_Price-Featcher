import asyncio
import os
from dotenv import load_dotenv
from gifts_fetcher import main as fetch_gifts
from price_fetcher import PriceFetcher

# Load environment variables
load_dotenv()

async def main():
    print("=== Telegram Gift Price Fetcher Prototype ===")
    
    # Check for credentials
    if not os.getenv("TELEGRAM_API_ID") or not os.getenv("TELEGRAM_API_HASH"):
        print("\n[!] CRITICAL: API_ID or API_HASH missing in .env")
        print("Please open .env and add your Telegram credentials.")
        print("Get them from: https://my.telegram.org")
        return

    print("\n--- 1. Fetching Your Gifts ---")
    try:
        # We need to adapt gifts_fetcher to return data instead of just printing
        # For now, we'll just run it to see output
        await fetch_gifts()
    except Exception as e:
        print(f"Error in Gift Fetcher: {e}")

    print("\n--- 2. Fetching Market Prices ---")
    try:
        pf = PriceFetcher()
        
        # Test Tonnel
        tonnel_prices = pf.fetch_tonnel_prices()
        print(f"Tonnel: Retrieved {len(tonnel_prices)} price points.")
        
        # Test Portals
        portals_prices = pf.fetch_portals_prices()
        if isinstance(portals_prices, list):
             print(f"Portals: Retrieved {len(portals_prices)} price points.")
        elif isinstance(portals_prices, dict):
             print(f"Portals: Retrieved {len(portals_prices)} keys.")

    except Exception as e:
        print(f"Error in Price Fetcher: {e}")

    print("\n=== Done ===")

if __name__ == "__main__":
    asyncio.run(main())
