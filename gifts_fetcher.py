import os
import asyncio
import logging
from datetime import datetime
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
        self.client = TelegramClient(SESSION_NAME, int(API_ID), API_HASH)
        self.logging_file = "debug.log"

    async def _log(self, message):
        """Logs message to a file and console."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        print(log_entry)
        with open(self.logging_file, "a") as f:
            f.write(log_entry + "\n")

    async def ensure_connected(self):
        """Ensures the client is connected and authorized."""
        if not self.client.is_connected():
            await self.client.connect()
        
        if not await self.client.is_user_authorized():
            raise Exception("Client is NOT authorized. Please run login.py first!")

    async def ensure_started(self):
         # Just an alias/wrapper if needed by server setup
         await self.ensure_connected()

    async def get_gifts(self):
        """
        Fetches the current user's saved Star Gifts using Telethon.
        Returns a list of dictionaries with parsed gift data.
        """
        await self.ensure_connected()
        
        try:
            # Import specific types for isinstance checks
            from telethon.tl.types import StarGiftUnique, StarGift, StarGiftAttributeModel, StarGiftAttributePattern, StarGiftAttributeBackdrop
            
            # Fetch saved gifts
            result = await self.client(GetSavedStarGiftsRequest(
                peer='me',
                offset="",
                limit=100
            ))
            
            parsed_gifts = []
            
            for saved_gift in result.gifts:
                try:
                    # The inner gift object can be StarGift or StarGiftUnique
                    gift = saved_gift.gift
                    gift_id = getattr(gift, 'id', 'unknown')
                    
                    parsed_item = {
                        "id": gift_id,
                        "name": "Unknown Gift", 
                        "details": "Common",
                        "price": 0, 
                        "num": None,
                        "image_url": "", 
                        "raw_obj": str(gift)
                    }
                    
                    # 1. Image Handling
                    # We check if image exists locally to avoid re-downloading
                    # Filename: static/images/{gift_id}.tgs (or .webp if converted? Python doesn't display TGS natively well on web without JS lib)
                    # Telethon downloads stickers usually as .tgs (Lottie) or .webp
                    # Let's try downloading thumb or document.
                    
                    # NOTE: Star Gifts often use .tgs (Animated). 
                    # For web display, we might need the static thumbnail or use a TGS player.
                    # Getting the `thumbs` from attributes if available.
                    
                    image_filename = f"{gift_id}.png" # We try to force png/jpg for simple display if possible, or let telethon decide extension
                    local_path = f"static/images/{gift_id}" # Telethon adds extension automatically if not specified? 
                    # Actually, better to specify exact path if we can.
                    
                    # Find a photo/document
                    media_to_download = None
                    if getattr(gift, 'sticker', None):
                         media_to_download = gift.sticker
                         # Check thumbs to get a static image (easier for <img> tag)
                         if hasattr(gift.sticker, 'thumbs') and gift.sticker.thumbs:
                             # Use the largest thumb? Or just download the doc and let thumb logic handle it?
                             # Telethon download_media with 'thumb=-1' downloads the largest thumbnail!
                             pass 
                    
                    # Check if already exists (any extension)
                    # We'll just check for .jpg or .png for now
                    if os.path.exists(f"static/images/{gift_id}.jpg"):
                        parsed_item["image_url"] = f"/static/images/{gift_id}.jpg"
                    elif os.path.exists(f"static/images/{gift_id}.png"):
                        parsed_item["image_url"] = f"/static/images/{gift_id}.png"
                    else:
                        # Download logic
                        if media_to_download:
                            # Verify valid file
                            print(f"Downloading image for gift {gift_id}...")
                            # Download thumbnail (static image)
                            file_path = await self.client.download_media(
                                media_to_download, 
                                file=f"static/images/{gift_id}",
                                thumb=-1 # Download largest thumb (static)
                            )
                            if file_path:
                                # Convert absolute path to relative for URL
                                # file_path might be absolute. ensure we get relative.
                                rel_path = os.path.relpath(file_path, os.getcwd())
                                # Ensure it starts with / for web
                                parsed_item["image_url"] = "/" + rel_path
                            else: 
                                print(f"Warning: No media downloaded for {gift_id}")

                    # 2. Parsing Logic
                    if isinstance(gift, StarGiftUnique):
                        print(f"Parsing Unique Gift: {gift.title}")
                        parsed_item["name"] = gift.title
                        parsed_item["num"] = gift.num
                        
                        models = []
                        if hasattr(gift, 'attributes'):
                            for attr in gift.attributes:
                                if isinstance(attr, StarGiftAttributeModel):
                                    models.append(attr.name)
                                elif isinstance(attr, StarGiftAttributePattern):
                                    models.append(attr.name)
                                elif isinstance(attr, StarGiftAttributeBackdrop):
                                    models.append(attr.name)
                        
                        if models:
                            parsed_item["details"] = " - ".join(models)
                        else:
                            parsed_item["details"] = "Unique"

                    elif isinstance(gift, StarGift):
                        print(f"Parsing Standard Gift ID: {gift.id}")
                        parsed_item["name"] = "Star Gift"
                        parsed_item["details"] = f"{gift.stars} Stars"
                        if getattr(gift, 'limited', False):
                             parsed_item["details"] += " (Limited)"
                    
                    parsed_gifts.append(parsed_item)

                except Exception as inner_e:
                    print(f"Error parsing individual gift: {inner_e}")
                    continue

            return parsed_gifts
             
        except Exception as e:
            await self._log(f"Error fetching gifts: {e}")
            return []

# Singleton instance to be used by API
fetcher_instance = GiftFetcher()

if __name__ == "__main__":
    fetcher = GiftFetcher()
    async def run():
        gifts = await fetcher.get_gifts()
        print(f"Fetched {len(gifts)} gifts.")
        print(gifts)
    
    asyncio.run(run())
