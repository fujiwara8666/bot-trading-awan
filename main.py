import ccxt
import pandas as pd
from datetime import datetime

# === KONFIGURASI BOT TRADING JALUR AWAN RENDER ===
SYMBOL = "BTC/USDT"
TIMEFRAME = "15m"
CANDLE_LIMIT = 150
RISK_REWARD_RATIO = 1.7

# Data Telegram Resmi Bosq
TELEGRAM_TOKEN = "8944761291:AAHUutWCcbuWs49UIIUQkCuwm39t74QNApM"
TELEGRAM_CHAT_ID = "5923279542"

exchange = ccxt.binance({
    "enableRateLimit": True,
    "options": {"defaultType": "future"}
})

def send_telegram_message(message):
    import requests
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        payload = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message,
            "parse_mode": "Markdown"
        }
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"Eror Telegram: {e}")

def run_bot():
    print("=== BOT TRADING JALUR RENDER AMAN AKTIF ===")
    
    try:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ohlcv = exchange.fetch_ohlcv(SYMBOL, TIMEFRAME, limit=CANDLE_LIMIT)
        df = pd.DataFrame(ohlcv, columns=["Timestamp", "Open", "High", "Low", "Close", "Volume"])
        
        df["EMA_50"] = df["Close"].ewm(span=50, adjust=False).mean()
        
        if len(df) < 52:
            print("Data candle kurang dari batasan EMA 50!")
            return
            
        ticker = exchange.fetch_ticker(SYMBOL)
        current_price = ticker["last"]
        
        o1, h1, l1, c1 = df["Open"].iloc[-2], df["High"].iloc[-2], df["Low"].iloc[-2], df["Close"].iloc[-2]
        o2, h2, l2, c2 = df["Open"].iloc[-3], df["High"].iloc[-3], df["Low"].iloc[-3], df["Close"].iloc[-3]
        current_ema = df["EMA_50"].iloc[-2]
        
        # Logika Deteksi Sinyal Engulfing Terfilter EMA 50
        if (c1 > o1) and (c2 < o2) and (c1 >= o2) and (o1 <= c2) and (c1 > current_ema):
            sl = l2
            tp = c1 + ((c1 - sl) * RISK_REWARD_RATIO)
            msg = f"🟢 *[RENDER NOTIF] BUY TERFILTER!*\n\n🪙 Koin: {SYMBOL}\n📈 Harga Masuk: {c1}\n🛑 Batas Rugi (SL): {sl:.2f}\n🎯 Target Untung (TP): {tp:.2f}\n💡 _[INFO] Tren sedang Bullish di atas EMA 50._"
            send_telegram_message(msg)
            print(f"[{now}] Sinyal BUY Terkirim!")
            
        elif (c1 < o1) and (c2 > o2) and (o1 >= c2) and (c1 <= o2) and (c1 < current_ema):
            sl = h2
            tp = c1 - ((sl - c1) * RISK_REWARD_RATIO)
            msg = f"🔴 *[RENDER NOTIF] SELL TERFILTER!*\n\n🪙 Koin: {SYMBOL}\n📈 Harga Masuk: {c1}\n🛑 Batas Rugi (SL): {sl:.2f}\n🎯 Target Untung (TP): {tp:.2f}\n💡 _[INFO] Tren sedang Bearish di bawah EMA 50._"
            send_telegram_message(msg)
            print(f"[{now}] Sinyal SELL Terkirim!")
            
        else:
            # Mengirim status online berkala ke Telegram agar kamu tahu bot tetap hidup meronda
            status_msg = f"🚀 *BOT TRADING JALUR RENDER ONLINE!*\nBot berhasil meronda pasar pada {now}. Kondisi pasar: *Belum ada sinyal Engulfing yang valid.* Memantau aman, Bosq!"
            send_telegram_message(status_msg)
            print(f"[{now}] Ronda selesai, tidak ada sinyal. Status ONLINE terkirim.")
            
    except Exception as e:
        print(f"Ada kendala pembacaan pasar: {e}")

if __name__ == "__main__":
    run_bot()
