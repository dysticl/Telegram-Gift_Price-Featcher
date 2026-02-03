import os
import asyncio
from dotenv import load_dotenv
from pyrogram import Client, raw
from pyrogram.errors import FloodWait

# Load environment variables
load_dotenv()

API_ID = os.getenv("TELEGRAM_API_ID")
API_HASH = os.getenv("TELEGRAM_API_HASH")
SESSION_NAME = "gift_fetcher_session"

class GiftFetcher:
    def __init__(self):
        if not API_ID or not API_HASH:
             raise ValueError("API_ID or API_HASH missing in .env")
        
        self.app = Client(SESSION_NAME, api_id=API_ID, api_hash=API_HASH)
        self.started = False

    async def ensure_started(self):
        if not self.started:
            await self.app.start()
            self.started = True

    async def stop(self):
        if self.started:
            await self.app.stop()
            self.started = False

    async def get_gifts(self):
        await self.ensure_started()
        me = await self.app.get_me()
        
        try:
            input_user = await self.app.resolve_peer(me.id)
            
            # Using raw function invoke
            # payments.getUserStarGifts#... user:InputUser offset:string limit:int = payments.UserStarGifts;
            # Note: We need to handle pagination in a real scenario, but for now max 100.
            result = await self.app.invoke(
                raw.functions.payments.GetUserStarGifts(
                    user=input_user,
                    offset="",
                    limit=100
                )
            )
            
            # Convert raw MTProto objects to a friendly dict
            gifts = []
            for gift in result.gifts:
                # Based on looking at Telegram API schemas or Pyrogram objects
                # We need to extract relevant fields.
                # Since we can't inspect the object easily without running, 
                # we'll grab generic attributes and try to map them.
                
                # Check if it has 'gift' attribute which contains the definition
                # or if 'gift' is an ID.
                # Usually: gift_id, message_id, date, etc.
                
                # Let's try to extract as much as possible safely
                
                g_data = {
                    "id": getattr(gift, "id", None),
                    "date": getattr(gift, "date", None),
                    "message": getattr(gift, "message", None),
                    # "amount": getattr(gift, "amount", None), # Some have stars amount
                }
                
                # We also need the GIFT DEFINITION (Name, Model, Rarity)
                # It might be in 'result.gifts' list or we might need to fetch definitions separately?
                # payments.UserStarGifts usually returns a list of UserStarGift
                # which might contain the 'gift_id'. 
                # To get name/model we might need `payments.getStarGifts` generic catalog to map IDs?
                # OR Pyrogram might automatically resolve some entities.
                
                # For prototype, we will return the raw-ish data we found
                # and maybe try to infer.
                
                # If we use `print(gift)` in the CLI we saw objects.
                # Let's assume we can get a string representation or dict 
                # if we can't find exact fields blindly.
                g_data["raw_str"] = str(gift)
                
                gifts.append(g_data)
                
            return gifts

        except Exception as e:
            print(f"Error fetching gifts: {e}")
            return []

# Singleton instance to be used by API
fetcher_instance = GiftFetcher()

if __name__ == "__main__":
    async def run_test():
        print("Testing GiftFetcher...")
        gifts = await fetcher_instance.get_gifts()
        print(f"Found {len(gifts)} gifts.")
        if gifts:
            print(gifts[0])
        await fetcher_instance.stop()

    asyncio.run(run_test())
