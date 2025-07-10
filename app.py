
import os
import threading
import time
from flask import Flask
import requests
import pandas as pd
from ta.momentum import RSIIndicator
from telegram import Bot

app = Flask(__name__)

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
SYMBOLS = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT"]  # Add more pairs if needed
TIMEFRAME = "15m"
RSI_BUY = 30
RSI_SELL = 70

bot = Bot(token=TOKEN)

def get_klines(symbol, interval="15m", limit=100):
    url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit={limit}"
    response = requests.get(url)
    data = response.json()
    df = pd.DataFrame(data, columns=[
        'timestamp', 'open', 'high', 'low', 'close',
        'volume', 'close_time', 'quote_asset_volume',
        'num_trades', 'taker_buy_base', 'taker_buy_quote', 'ignore'
    ])
    df['close'] = df['close'].astype(float)
    df['volume'] = df['volume'].astype(float)
    return df

def check_signal(symbol):
    df = get_klines(symbol, TIMEFRAME)
    rsi = RSIIndicator(close=df['close'], window=14).rsi()
    last_rsi = rsi.iloc[-1]
    avg_volume = df['volume'][:-1].mean()
    last_volume = df['volume'].iloc[-1]

    conf = 0
    if last_rsi < RSI_BUY:
        conf += 0.6
    if last_volume > avg_volume * 1.5:
        conf += 0.4
    confidence = round(conf * 100)

    if confidence >= 70:
        direction = "Buy" if last_rsi < RSI_BUY else "Sell"
        msg = f"""
🚨 {direction} Signal: {symbol} ({TIMEFRAME})
📊 RSI = {round(last_rsi, 2)}
📈 Volume: {round(last_volume)} (+{round((last_volume/avg_volume)*100 - 100)}%)
✅ Confidence: {confidence}%

🔄 Entry Price: ${df['close'].iloc[-1]}
🧠 Reason: RSI {'oversold' if last_rsi < 30 else 'overbought'} + volume surge
        """
        bot.send_message(chat_id=CHAT_ID, text=msg)

def run_bot_loop():
    while True:
        for symbol in SYMBOLS:
            try:
                check_signal(symbol)
            except Exception as e:
                bot.send_message(chat_id=CHAT_ID, text=f"Error for {symbol}: {str(e)}")
        time.sleep(900)  # 15 minutes

@app.route('/')
def home():
    return "Multi-Currency Crypto Signal Bot is running!"

if __name__ == "__main__":
    threading.Thread(target=run_bot_loop, daemon=True).start()
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
