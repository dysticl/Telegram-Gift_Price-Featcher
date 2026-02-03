import asyncio
import json
import os
from dotenv import load_dotenv
try:
    from aportalsmp import update_auth, giftsFloors
except ImportError:
    print("Error: aportalsmp not found. Please install it.")
    exit(1)

# Load env vars
load_dotenv()

API_ID = os.getenv("TELEGRAM_API_ID")
API_HASH = os.getenv("TELEGRAM_API_HASH")

async def update_prices():
    print("--- Starting Price Update (Portals) ---")
    
    auth_data = ""
    # 1. Authenticate
    # Try to load existing auth if possible? The library uses Pyrogram session internally.
    # update_auth creates/reuses the session.
    try:
        print(f"Authenticating with ID: {API_ID}...")
        auth_data = await update_auth(API_ID, API_HASH)
        print("Authentication successful.")
    except Exception as e:
        print(f"Authentication failed: {e}")
        return

    # 2. Fetch Floors
    try:
        print("Fetching floor prices...")
        floors_obj = await giftsFloors(authData=auth_data)
        
        if floors_obj:
            # Convert GiftsFloors object to dict
            floors = floors_obj.toDict()
            print(f"Successfully fetched {len(floors)} prices.")
            
            # 3. Save to JSON
            # Structure: {"Gift Name": price, ...}
            # Portals API returns formatted JSON. Let's see structure.
            # Usually it's key: val or list of objects.
            # Based on docs/code: returns dict { "Collection Name": floor_price, ... } or similar.
            
            # Map known names if needed, but usually Portals uses standard names.
            
            with open("market_prices.json", "w") as f:
                json.dump(floors, f, indent=4)
                
            print("Prices saved to market_prices.json")
        else:
            print("No prices returned.")
            
    except Exception as e:
        print(f"Error fetching prices: {e}")

if __name__ == "__main__":
    if not API_ID or not API_HASH:
        print("Error: Missing API_ID or API_HASH in .env")
    else:
        asyncio.run(update_prices())
