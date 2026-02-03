from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import uvicorn
import asyncio
import os
from typing import List, Dict

# Import our fetcher modules
from gifts_fetcher import fetcher_instance as gift_service
from price_fetcher import PriceFetcher

app = FastAPI()

# Mount static directory for frontend
app.mount("/static", StaticFiles(directory="static"), name="static")

price_service = PriceFetcher()

# In-memory cache
CACHE = {
    "gifts": [],
    "prices": {},
    "last_updated": 0
}

@app.on_event("startup")
async def startup_event():
    # Check for MOCK_MODE
    if os.getenv("MOCK_MODE") == "true":
        print("!!! RUNNING IN MOCK MODE !!! No Telegram connection required.")
        return

    # Start the Telethon client
    try:
        await gift_service.ensure_started()
    except Exception as e:
        print(f"Warning: Could not start GiftFetcher on startup: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    await gift_service.stop()

@app.get("/")
async def read_root():
    return FileResponse('static/index.html')

@app.get("/api/portfolio")
async def get_portfolio():
    # MOCK MODE DATA
    if os.getenv("MOCK_MODE") == "true":
        return {
            "total_value_ton": 1250.5,
            "total_items": 4,
            "gifts": [
                {
                    "name": "Toy Bear",
                    "details": "Wizard",
                    "image_url": "https://cache.tonapi.io/imgproxy/b2a7eb46522c0926d2d46816027d14df2011158d/aHR0cHM6Ly9uZnQudG9uZGlhbW9uZHMuY29tL25ZnQtZ2lmdHMvYXBpL3YxL3RvbnBsYW5ldC9naWZ0cy8xL2ltYWdl.webp", # Real toy bear url example
                    "price": 50.0,
                    "num": 1337
                },
                {
                    "name": "Lunar Snake",
                    "details": "Albino (1.5%)",
                    "image_url": "https://cache.tonapi.io/imgproxy/4e6221f75960000a6230894ff9c687e35759ce91/aHR0cHM6Ly9uZnQudG9uZGlhbW9uZHMuY29tL25ZnQtZ2lmdHMvYXBpL3YxL3RvbnBsYW5ldC9naWZ0cy8yL2ltYWdl.webp", # Real snake url example
                    "price": 1200.5,
                    "num": 42
                },
                 {
                    "name": "Star",
                    "details": "Meteor",
                    "image_url": "", 
                    "price": 0,
                    "num": 99999
                }
            ],
            "debug_prices": {"Mock": "True"}
        }

    # 1. Fetch Gifts
    # We try to use cached data if fresh enough (TODO), for now fetch fresh
    try:
        user_gifts = await gift_service.get_gifts()
    except Exception as e:
        # If not logged in, we might get an error
        print(f"API Error fetching gifts: {e}")
        return {"error": "Could not fetch gifts. Check server logs/login."}

    # 2. Fetch Prices
    # We fetch from both sources
    # Ideally should run concurrently
    tonnel_prices = price_service.fetch_tonnel_prices()
    portals_prices = price_service.fetch_portals_prices()
    
    # Merge price sources (Naively overwrite or prefer one?)
    # Portals often has more data on new gifts.
    # We need to normalize names. 
    # Mock data keys: "Lunar Snake - Albino (1.5%)"
    # Portals data keys might be "Toy Bear" with properties separate.
    
    # Create a unified pricing dict: { "ModelName": Price } or { "GiftID": Price }
    # Since we don't have perfect ID matching yet, we rely on Name+Model string matching.
    
    market_prices = {}
    
    # Process Tonnel
    if tonnel_prices and isinstance(tonnel_prices, dict):
        market_prices.update(tonnel_prices)
        
    # Process Portals (if it returns list of dicts)
    if portals_prices and isinstance(portals_prices, list):
        for item in portals_prices:
            # item structure?
            name = item.get('name')
            # Portals "gifts-floors" endpoint usually returns breakdown by model
            # Let's assume structure or use mock structure
            # If mock returns list of {name, floor_price}
            p = item.get('floor_price')
            if name and p:
                market_prices[name] = p

    # 3. Match Gifts to Prices
    # We need to parse 'raw_str' or attributes from user_gifts 
    # to find the key in market_prices.
    
    total_value = 0.0
    enriched_gifts = []
    
    for g in user_gifts:
        # Placeholder parsing logic
        # In reality, we need to inspect `g['raw_str']` or properties
        # For prototype, we will just assign a RANDOM match from our prices 
        # if we can't parse, OR just list it as "Unknown".
        
        # DEBUG: Let's assume one is a "Toy Bear" for testing if we find it
        # Real matching logic requires deeper introspection of Pyrogram objects
        
        gift_name = "Unknown" 
        # Try to find name in raw string for demo
        raw_s = g.get('raw_str', '')
        if "Toy Bear" in raw_s: gift_name = "Toy Bear"
        elif "Star" in raw_s: gift_name = "Star"
        elif "Snake" in raw_s: gift_name = "Lunar Snake"
        
        # Find price
        # Try exact match or partial
        price = 0
        best_match_key = None
        
        for key, val in market_prices.items():
            if gift_name in key:
                price = val
                best_match_key = key
                break
        
        total_value += float(price)
        
        enriched_gifts.append({
            "id": g.get("id"),
            "name": gift_name,
            "details": best_match_key or "Common",
            "price": price,
            "raw": str(g)
        })

    return {
        "total_value_ton": total_value,
        "total_items": len(user_gifts),
        "gifts": enriched_gifts,
        "debug_prices": market_prices
    }

if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
