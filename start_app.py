import uvicorn
import os
import sys

from dotenv import load_dotenv

# Load env vars
load_dotenv()

def start_tunnel():
    print("Starting ngrok tunnel regarding port 8000...")
    # We use system ngrok command since we have it via brew
    # We'll start it in background and give user instructions
    # Note: capturing output is tricky, we'll try to let it print to stdout or user can see it
    
    # We can try to use popen but ngrok is interactive
    try:
        # Check if running
        import subprocess
        import time
        import requests
        
        # Start ngrok process
        # > /dev/null to hide its interactive UI spam if possible, or let it run in separate window usually
        # But here we want the URL.
        # Best way via API:
        proc = subprocess.Popen(["ngrok", "http", "8000"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("Waiting for ngrok to initialize...")
        time.sleep(3)
        
        # Query local API to get URL
        try:
            resp = requests.get("http://127.0.0.1:4040/api/tunnels")
            public_url = resp.json()['tunnels'][0]['public_url']
            print("="*60)
            print(f"🌍 PUBLIC URL: {public_url}")
            print("="*60)
            print("👉 COPY THIS URL into BotFather -> /mybots -> Bot Settings -> Menu Button -> Set URL")
            print("="*60)
        except:
             print("Could not auto-fetch URL. Check http://127.0.0.1:4040 manually.")
             
    except FileNotFoundError:
        print("Error: 'ngrok' command not found. Please install it manually.")
    except Exception as e:
        print(f"Tunnel error: {e}")

if __name__ == "__main__":
    # Start Tunnel in background thread or just before server
    start_tunnel()
    
    # Start Uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
