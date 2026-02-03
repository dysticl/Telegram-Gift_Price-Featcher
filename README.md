# 🎁 Telegram Gift Valuation Bot

A sophisticated Telegram Bot that calculates the real-time market value of a user's Telegram Gift portfolio using direct market data from **Portals.to**.

**Language:** Python 🐍  
**Interface:** Russian 🇷🇺 (Telegram Bot)  
**Core Libs:** `Telethon`, `aportalsmp`, `asyncio`

---

## ✨ Features

- **Real-Time Valuation:** Fetches accurate Floor Prices from the Portals Marketplace (via `aportalsmp`).
- **Multi-User Support:** Users can securely log in via the bot (Phone + Code) to scan their *private* and *public* gifts.
- **Portals Auth:** Includes scripts to authenticate as a developer to fetch high-fidelity market data.
- **Persistent Sessions:** Sessions are stored locally (`session_USERID.session`) so users only log in once.
- **Privacy First:** Sessions are used strictly for reading gift data. Users can logout (`/logout`) at any time.

## 🚀 Installation

### 1. Clone & Install
```bash
git clone https://github.com/YOUR_USERNAME/Telegram-Gift-Price-Fetcher.git
cd Telegram-Gift-Price-Fetcher
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
*(Note: Ensure `telethon`, `curl_cffi`, `python-dotenv` are installed)*

### 2. Configuration (.env)
Create a `.env` file in the root directory:
```ini
# Get these from https://my.telegram.org/apps
TELEGRAM_API_ID=12345678
TELEGRAM_API_HASH=your_api_hash_here

# Get this from @BotFather
TELEGRAM_BOT_TOKEN=123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11
```

### 3. Fetch Market Data
Before starting the bot, fetch the initial price list (requires one-time developer login):
```bash
python fetch_real_prices.py
```
*Follow the prompt to log in with your developer account. This creates `market_prices.json`.*

### 4. Run the Bot
```bash
python bot.py
```

## 🤖 Usage

Open your bot in Telegram and start it:

- **/start** — Shows the Main Menu.
- **📱 Авторизоваться** — Log in (Share Contact -> Receive Code -> Enter Code).
    - *Note:* When entering the code, use spaces (e.g., `1 2 3 4 5`) to bypass Telegram's phishing filter.
- **💰 Мое Портфолио** — Scans your profile and calculates total value in TON.
- **🚪 Выйти** — Deletes your local session file.

## ⚠️ Disclaimer
This project is unofficial and not affiliated with Telegram or Portals. Use at your own risk. Be careful when handling session files (`*.session`). Never commit them to GitHub!

## 🛡 Security
- `.gitignore` is configured to exclude `*.session`, `.env`, and `*.log`.
- User codes are only used for immediate session creation and are not stored.
