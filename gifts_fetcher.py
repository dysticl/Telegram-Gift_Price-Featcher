import os
import asyncio
from dotenv import load_dotenv
from telethon import TelegramClient
from telethon.tl.functions.payments import GetSavedStarGiftsRequest
from telethon.tl.types import InputPeerSelf

# Load environment variables
load_dotenv()

API_ID = os.getenv("TELEGRAM_API_ID")
API_HASH = os.getenv("TELEGRAM_API_HASH")
SESSION_NAME = "telethon_session"

class GiftFetcher:
    def __init__(self):
        if not API_ID or not API_HASH:
             raise ValueError("API_ID or API_HASH missing in .env")
        
        # Telethon client
        self.client = TelegramClient(SESSION_NAME, int(API_ID), API_HASH)
        self.started = False

    async def ensure_started(self):
        if not self.client.is_connected():
            await self.client.connect()
        
        # Check if authorized
        if not await self.client.is_user_authorized():
            # This requires interactive login if not authorized
            # We can't easily do it inside API call without blocking
            # The server startup event handles this if run in terminal
            print("Client not authorized. Waiting for interactive login...")
            # Use specific method to trigger login flow if needed, 
            # here we assume start() handles it or we call it explicitly
            await self.client.start()

    async def stop(self):
        await self.client.disconnect()

    async def get_gifts(self):
        await self.ensure_started()
        
        try:
            # GetSavedStarGiftsRequest(peer, offset, limit, ...)
            # peer=InputPeerSelf() targets the current user
            result = await self.client(GetSavedStarGiftsRequest(
                peer=InputPeerSelf(),
                offset="",
                limit=100
            ))
            
            # Result is likely payments.SavedStarGifts
            # It has .gifts (List of SavedStarGift) and .users (List of User) and .chats...
            
            # We need to parse this into a friendly format
            gifts = []
            
            # If result has 'gifts' attribute
            if hasattr(result, 'gifts'):
                for gift in result.gifts:
                    # gift is Likely 'SavedStarGift'
                    # Attributes: date, crypto_amount, crypto_currency, ...
                    # AND crucially: 'gift' (The generic StarGift definition)
                    
                    # We try to extract info
                    g_data = {
                        "date": getattr(gift, "date", None),
                        "message_id": getattr(gift, "msg_id", None),
                    }
                    
                    # The actual definition might be in gift.gift (StarGift)
                    # or referenced ID.
                    # Telethon objects have .to_dict() which is useful for debugging
                    if hasattr(gift, 'to_dict'):
                        g_data["raw"] = gift.to_dict()
                    else:
                        g_data["raw_str"] = str(gift)
                        
                    gifts.append(g_data)
            
            return gifts

        except Exception as e:
            error_msg = f"Error fetching gifts (Telethon): {e} | Type: {type(e)}"
            print(error_msg)
            with open("debug.log", "a") as f:
                f.write(error_msg + "\n")
            return []

# Singleton instance to be used by API
fetcher_instance = GiftFetcher()

if __name__ == "__main__":
    async def run_test():
        print("Testing GiftFetcher (Telethon)...")
        try:
            gifts = await fetcher_instance.get_gifts()
            print(f"Found {len(gifts)} gifts.")
            if gifts:
                print("Sample:", gifts[0])
        except Exception as e:
            print(f"Test Error: {e}")
        finally:
            await fetcher_instance.stop()

    asyncio.run(run_test())
