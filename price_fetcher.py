import json
import requests
from fake_useragent import UserAgent
import time

class PriceFetcher:
    def __init__(self):
        try:
            self.ua = UserAgent()
        except:
            self.ua = None
        
    def get_user_agent(self):
        if self.ua:
            return self.ua.random
        return "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

    def fetch_tonnel_prices(self):
        print("Fetching prices from Tonnel...")
        url = "https://gifts2.tonnel.network/api/pageGifts"
        
        headers = {
            "authority": "gifts2.tonnel.network",
            "accept": "application/json, text/plain, */*",
            "content-type": "application/json",
            "origin": "https://market.tonnel.network",
            "referer": "https://market.tonnel.network/",
            "user-agent": self.get_user_agent()
        }
        
        # Extremely simple payload
        payload = {
            "page": 1,
            "limit": 20,
            "sort": json.dumps({"price": 1}),
            "filter": json.dumps({"asset": "TON"}),
            "user_auth": ""
        }

        try:
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            
            if response.status_code != 200:
                print(f"Tonnel Error: {response.status_code}")
                return self.get_mock_data("Tonnel")

            data = response.json()
            prices = {}
            
            # Helper to extract from list
            def extract_gifts(gift_list):
                for gift in gift_list:
                    name = gift.get('gift_name')
                    model = gift.get('model')
                    price_ton = gift.get('price')
                    if name and model and price_ton:
                        key = f"{name} - {model}"
                        prices[key] = price_ton

            if 'response' in data and 'gifts' in data['response']:
                extract_gifts(data['response']['gifts'])
            elif 'gifts' in data:
                extract_gifts(data['gifts'])
            
            if not prices:
                 print("Tonnel: No prices found in response. Using Mock.")
                 return self.get_mock_data("Tonnel")
            
            print(f"Tonnel: Found {len(prices)} floor prices.")
            return prices

        except Exception as e:
            print(f"Error fetching Tonnel: {e}")
            return self.get_mock_data("Tonnel")

    def fetch_portals_prices(self):
        print("Fetching prices from Portals...")
        url = "https://api.portals.market/api/v1/gifts/gifts-floors"
        
        headers = {
            "authority": "api.portals.market",
            "accept": "application/json, text/plain, */*",
            "origin": "https://portals.market",
            "referer": "https://portals.market/",
            "user-agent": self.get_user_agent()
        }
        
        try:
           response = requests.get(url, headers=headers, timeout=10)
           
           if response.status_code != 200:
               print(f"Portals API Error: {response.status_code}")
               return self.get_mock_data("Portals")

           data = response.json()
           print(f"Portals: Found {len(data)} items.")
           return data
               
        except Exception as e:
            print(f"Error fetching Portals: {e}")
            return self.get_mock_data("Portals")

    def get_mock_data(self, source):
        # print(f"[{source}] Using MOCK data for prototype demonstration.")
        if source == "Tonnel":
            return {
                "Lunar Snake - Albino (1.5%)": 150.0,
                "Toy Bear - Wizard": 50.0,
                "Star - Meteor": 1000.0,
                "Generic Gift - Common": 10.0
            }
        else:
             return [
                 {"name": "Toy Bear", "floor_price": 45.0},
                 {"name": "Lunar Snake", "floor_price": 140.0},
                 {"name": "Star", "floor_price": 950.0}
             ]

if __name__ == "__main__":
    fetcher = PriceFetcher()
    tonnel_data = fetcher.fetch_tonnel_prices()
    print("Tonnel Output:", list(tonnel_data.items())[:3])
    
    portals_data = fetcher.fetch_portals_prices()
    print("Portals Output:", str(portals_data)[:100])
