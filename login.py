import os
from dotenv import load_dotenv
from telethon import TelegramClient

# Load environment variables
load_dotenv()

API_ID = os.getenv("TELEGRAM_API_ID")
API_HASH = os.getenv("TELEGRAM_API_HASH")
SESSION_NAME = "telethon_session"

if not API_ID or not API_HASH:
    print("Error: TELEGRAM_API_ID or TELEGRAM_API_HASH not found in .env")
    exit(1)

def main():
    print("Starting Telethon Client for Login...")
    client = TelegramClient(SESSION_NAME, int(API_ID), API_HASH)
    
    # This will trigger the interactive login flow
    client.start()
    
    print("\nSUCCESS! You are now logged in.")
    print(f"Session file '{SESSION_NAME}.session' created.")
    print("You can now run the server without login issues.")
    
    client.disconnect()

if __name__ == "__main__":
    main()
