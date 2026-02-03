import asyncio
import os
from dotenv import load_dotenv
from portalsapi import update_auth, giftsFloors, search

load_dotenv()

API_ID = os.getenv("TELEGRAM_API_ID")
API_HASH = os.getenv("TELEGRAM_API_HASH")

async def main():
    print(f"Authenticating with Portals using ID: {API_ID}...")
    try:
        # 1. Get Auth Token using Pyrogram (uses same session file but might conflict if locked, let's see)
        # Pyrogram defaults to "my_account", allow it to create a session
        auth_data = await update_auth(API_ID, API_HASH)
        print(f"Auth Success! Token len: {len(auth_data)}")
        
        # 2. Fetch Floors
        print("Fetching Floor Prices...")
        floors = giftsFloors(authData=auth_data)
        
        if floors:
            print(f"Found {len(floors)} collections with floor prices.")
            print("Sample:", list(floors.items())[:3])
        else:
            print("No floor prices found.")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
