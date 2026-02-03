# Konzept v2: Telegram Gift Price Fetcher (Mini App)

## 1. Challenge & Solution for Hidden Gifts

### Problem
Hidden gifts on a user's Telegram profile are **invisible** to standard bots and public scrapers (like `gift_charts`).

### Solutions
#### Option A: Userbot Backend (Selected for Cousin/Admin)
- **Mechanik:** Der Server läuft mit einem "echten" User-Client (Pyrogram), eingeloggt als der Nutzer (Cousin).
- **Vorteil:** Sieht ALLES, auch versteckte Gifts, genau wie der offizielle Telegram Client.
- **Nachteil:** Benötigt Session-String (Login via Telefonnummer).
- **Anwendung:** Ideal für den "Admin-Modus" oder eine private Instanz.

#### Option B: TON Connect (Selected for Public Users)
- **Mechanik:** User verbindet ihr TON Wallet in der Mini App.
- **Vorteil:** Liest NFTs direkt von der Blockchain. Privacy-Einstellungen im Telegram-Profil sind egal.
- **Nachteil:** Nur gemintete Gifts (NFTs) sichtbar. Noch nicht umgewandelte "Star Gifts" fehlen.

### Entscheidung
Wir bauen eine **Hybrid-Lösung**:
1.  **Backend (FastAPI):** Verwaltet Sessions. Für den Cousin/Admin wird eine feste MTProto-Session hinterlegt, die seine versteckten Gifts scannt.
2.  **Frontend (Mini App):** Zeigt die Daten an. Für fremde User könnte später TON Connect integriert werden.

---

## 2. Architektur

### Backend (Python/FastAPI)
- **`main.py`:** API Server.
- **`gifts_fetcher.py`:** MTProto Client (Pyrogram) läuft im Hintergrund/auf Anfrage.
- **`price_fetcher.py`:** Holt Preise von Portals/Tonnel (bereits implementiert).
- **Database:** SQLite zum Caching von:
    - User Gifts (damit nicht bei jedem Request neu gefetcht werden muss).
    - Marktpreisen (um Rate Limits zu schonen).

### Frontend (Html/JS)
- **`index.html`:** Einfache Single-Page App.
- **`script.js`:**
    - Holt Daten vom Backend (`/api/portfolio`).
    - Zeigt Liste und Gesamtwert an.
    - Nutzt Telegram WebApp API für Theme-Infos.

---

## 3. Implementation Plan (Revised)

1.  **Backend API Setup:**
    - Endpoint: `GET /api/portfolio` -> Liefert JSON mit Gifts & Werten.
    - Endpoint: `POST /api/refresh` -> Trigger für erneutes Fetchen via MTProto.
2.  **Frontend Basic:**
    - Anzeige der JSON-Daten als hübsche Liste (TailwindCSS/CSS).
3.  **Deploy:**
    - Lokal testen via `ngrok` oder Tunneling, um es in Telegram als Mini App zu öffnen.

---

## 4. API Response Structure (Draft)

```json
{
  "total_value_ton": 1250.5,
  "total_items": 65,
  "gifts": [
    {
      "name": "Toy Bear",
      "model": "Wizard",
      "image": "url...",
      "floor_price": 50.0,
      "source": "Tonnel"
    },
    ...
  ]
}
```
