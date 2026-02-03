import os
from dotenv import load_dotenv
from telethon import TelegramClient

# Load environment variables
load_dotenv()

API_ID = os.getenv("TELEGRAM_API_ID")
API_HASH = os.getenv("TELEGRAM_API_HASH")
SESSION_NAME = "telethon_session"

async def main():
    print(f"Testing session: {SESSION_NAME}...")
    client = TelegramClient(SESSION_NAME, int(API_ID), API_HASH)
    
    try:
        await client.connect()
        if await client.is_user_authorized():
            me = await client.get_me()
            print(f"SUCCESS: Session is valid! Logged in as: {me.first_name} ({me.id})")
        else:
            print("FAILURE: Session connected but NOT authorized.")
    except Exception as e:
        print(f"ERROR: Could not connect: {e}")
    finally:
        await client.disconnect()

import asyncio
if __name__ == "__main__":
    asyncio.run(main())
