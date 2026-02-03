
import asyncio
import os
import json
import logging
import re
from dotenv import load_dotenv
from telethon import TelegramClient, events, Button
from telethon.errors import SessionPasswordNeededError
from gifts_fetcher import GiftFetcher

# Configure Logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Load Environment Variables
load_dotenv()
API_ID = int(os.getenv("TELEGRAM_API_ID"))
API_HASH = os.getenv("TELEGRAM_API_HASH")
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Global Cache
MARKET_PRICES = {}
PENDING_LOGINS = {}

# --- MENU BUTTONS (CONSTANTS) ---
BTN_STATS = "💰 Мое Портфолио"
BTN_CONCEPT = "📄 О Проекте"
BTN_LOGOUT = "🚪 Выйти"
BTN_LOGIN = "📱 Авторизоваться"

MAIN_MENU = [
    [Button.text(BTN_STATS, resize=True), Button.text(BTN_CONCEPT, resize=True)],
    [Button.text(BTN_LOGOUT, resize=True)]
]

def load_prices():
    global MARKET_PRICES
    if os.path.exists("market_prices.json"):
        try:
            with open("market_prices.json", "r") as f:
                MARKET_PRICES = json.load(f)
            logger.info(f"Loaded {len(MARKET_PRICES)} prices from cache.")
        except Exception as e:
            logger.error(f"Error loading prices: {e}")
    else:
        logger.warning("No market_prices.json found! Prices will be 0.")

async def get_user_gifts_safe(user_client):
    fetcher = GiftFetcher() 
    fetcher.client = user_client 
    return await fetcher.get_gifts()

async def generate_report(user_id, client):
    load_prices()
    gifts = await get_user_gifts_safe(client)
    
    total_val = 0.0
    def normalize(s): return str(s).lower().replace(" ", "").replace("-", "").replace("'", "")

    populated_gifts = []
    for g in gifts:
        name = g.get('name', 'Unknown')
        price = 0.0
        n_name = normalize(name)
        
        for p_name, p_val in MARKET_PRICES.items():
            if normalize(p_name) == n_name:
                price = float(p_val)
                break
        
        g['price'] = price
        populated_gifts.append(g)
        total_val += price

    populated_gifts.sort(key=lambda x: x['price'], reverse=True)
    
    msg = f"✨ **Ваше Портфолио Подарков** ✨\n\n"
    
    # Top 3 Emojis
    medals = ["🥇", "🥈", "🥉"]
    
    for i, g in enumerate(populated_gifts[:15]):
         icon = medals[i] if i < 3 else "🎁"
         p_str = f"💎 `{g['price']:,.1f}` TON" if g['price'] > 0 else "---"
         msg += f"{icon} **{g['name']}** — {p_str}\n"
         
    if len(populated_gifts) > 15:
        msg += f"\n...и еще {len(populated_gifts)-15} подарков.\n"
        
    msg += f"\n━━━━━━━━━━━━━━━━━━━━\n"
    msg += f"💰 **Итоговая стоимость:** `{total_val:,.1f} TON`\n"
    msg += f"📦 **Всего подарков:** `{len(populated_gifts)}`"
    
    return msg

CONCEPT_TEXT = """
📄 **О Проекте**

**Что это такое?**
Бот для оценки стоимости вашей коллекции Telegram Gifts по рыночным ценам (Portals).

**Безопасность**
Мы используем вашу сессию *только для чтения* списка подарков. Вы можете в любой момент завершить сессию кнопкой "Выйти".

_Разработано с ❤️_
"""

async def main():
    logger.info("Initializing Bot (UI V2)...")
    bot = TelegramClient('bot_session', API_ID, API_HASH)
    await bot.start(bot_token=BOT_TOKEN)
    
    # Helper to check auth
    def is_logged_in(user_id):
        return os.path.exists(f"session_{user_id}.session")

    @bot.on(events.NewMessage(pattern='/start'))
    async def start_handler(event):
        user_id = event.sender_id
        
        if is_logged_in(user_id):
            await event.respond(
                f"👋 **С возвращением!**\n\n"
                f"Выберите действие в меню ниже 👇",
                buttons=MAIN_MENU
            )
        else:
            await event.respond(
                "👋 **Привет!** Я помогу узнать рыночную стоимость твоих подарков.\n\n"
                "👇 **Нажми кнопку ниже, чтобы авторизоваться:**",
                buttons=[[Button.request_phone(BTN_LOGIN, resize=True)]]
            )

    # Handler for Menu Buttons + Commands
    @bot.on(events.NewMessage)
    async def general_handler(event):
        text = event.text.strip()
        user_id = event.sender_id
        
        # 1. Login Logic (Contact or Code)
        if event.message.contact:
            # Handle Phone
            phone = event.message.contact.phone_number
            await event.respond(f"📱 Номер получен: `{phone}`\n🔄 Вхожу...", buttons=Button.clear())
            
            client = TelegramClient(f"session_{user_id}", API_ID, API_HASH)
            await client.connect()
            try:
                send_code = await client.send_code_request(phone)
                PENDING_LOGINS[user_id] = {'client': client, 'phone': phone, 'phone_code_hash': send_code.phone_code_hash}
                
                await event.respond(
                    "✅ **Код отправлен!**\n"
                    "Введите код **с пробелами** (чтобы Telegram не ругался).\n"
                    "Пример: `1 2 3 4 5`",
                    buttons=Button.clear()
                )
            except Exception as e:
                await event.respond(f"❌ Ошибка: {e}")
                await client.disconnect()
            return

        elif user_id in PENDING_LOGINS:
            # Handle Code input
            code = "".join(re.findall(r'\d+', text))
            if len(code) < 5: return # Just chatting?

            data = PENDING_LOGINS[user_id]
            client = data['client']
            try:
                await client.sign_in(data['phone'], code, phone_code_hash=data['phone_code_hash'])
                await event.respond(
                    "🎉 **Успешно!** Вы вошли.\nПользуйтесь меню ниже 👇",
                    buttons=MAIN_MENU
                )
                await client.disconnect() # clean disconnect
                del PENDING_LOGINS[user_id]
            except Exception as e:
                await event.respond(f"❌ Ошибка входа: {e}")
                await client.disconnect()
            return
            
        # 2. Authenticated Actions
        if not is_logged_in(user_id):
            if text == "/start": return # Handled above
            # If not logged in and sending random text, prompt login again
            await event.respond("🔒 Для начала нужно авторизоваться.", buttons=[[Button.request_phone(BTN_LOGIN, resize=True)]])
            return

        # Menu Handlers
        if text == BTN_STATS or text == "/stats":
            msg = await event.respond("⏳ **Считаю...**")
            client = TelegramClient(f"session_{user_id}", API_ID, API_HASH)
            await client.connect()
            try:
                if not await client.is_user_authorized():
                    await event.respond("❌ Сессия истекла.", buttons=[[Button.request_phone(BTN_LOGIN, resize=True)]])
                else:
                    rep = await generate_report(user_id, client)
                    await bot.edit_message(msg, rep)
            except Exception as e:
                await bot.edit_message(msg, f"❌ Ошибка: {e}")
            finally:
                await client.disconnect()
                
        elif text == BTN_CONCEPT or text == "/concept":
            await event.respond(CONCEPT_TEXT, buttons=MAIN_MENU)
            
        elif text == BTN_LOGOUT or text == "/logout":
            if os.path.exists(f"session_{user_id}.session"):
                os.remove(f"session_{user_id}.session")
            await event.respond("✅ **Вышли.**", buttons=Button.clear())
            # Show login button again
            await event.respond("👇 Нажми чтобы войти снова:", buttons=[[Button.request_phone(BTN_LOGIN, resize=True)]])

    logger.info("Bot started...")
    await bot.run_until_disconnected()

if __name__ == '__main__':
    asyncio.run(main())
