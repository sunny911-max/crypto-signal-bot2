import asyncio
import logging
from flask import Flask
from telegram import Bot
from ta.momentum import RSIIndicator
import pandas as pd
import requests
import os

app = Flask(__name__)
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
bot = Bot(token=BOT_TOKEN)

SYMBOLS = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT"]
INTERVAL = "15m"
LIMIT = 100

import asyncio
import logging
from flask import Flask
from telegram import Bot
from ta.momentum import RSIIndicator
import pandas as pd
import requests
import os

app = Flask(__name__)
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
bot = Bot(token=BOT_TOKEN)

SYMBOLS = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT"]
INTERVAL = "15m"
LIMIT = 100

def fetch_data(symbol):
    url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={INTERVAL}&limit={LIMIT}"
    response = requests.get(url)
    data = response.json()
    df = pd.DataFrame(data, columns=[
        "timestamp", "open", "high", "low", "close", "volume",
        "close_time", "quote_asset_volume", "number_of_trades",
        "taker_buy_base_volume", "taker_buy_quote_volume", "ignore"
    ])
    df["close"] = pd.to_numeric(df["close"])
    df["volume"] = pd.to_numeric(df["volume"])
    return df

async def analyze_and_send():
    for symbol in SYMBOLS:
        try:
            df = fetch_data(symbol)
            if df.empty:
                raise ValueError("No data received")

            rsi = RSIIndicator(df["close"], window=14).rsi().iloc[-1]
            volume = df["volume"].iloc[-1]
            avg_volume = df["volume"].mean()

            if rsi < 30 and volume > avg_volume * 1.5:
                msg = f"📉 Oversold Signal\nSymbol: {symbol}\nRSI: {rsi:.2f}\nVolume: {volume:.2f}"
                await bot.send_message(chat_id=CHAT_ID, text=msg)
            elif rsi > 70 and volume > avg_volume * 1.5:
                msg = f"📈 Overbought Signal\nSymbol: {symbol}\nRSI: {rsi:.2f}\nVolume: {volume:.2f}"
                await bot.send_message(chat_id=CHAT_ID, text=msg)

        except Exception as e:
            await bot.send_message(chat_id=CHAT_ID, text=f"Error for {symbol}: {str(e)}")
def home():
    loop = asyncio.get_event_loop()
    if loop.is_closed():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    loop.create_task(analyze_and_send())
    return "Bot is analyzing and running!"

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=10000)

async def analyze_and_send():
    for symbol in SYMBOLS:
        try:
            df = fetch_data(symbol)
            rsi = RSIIndicator(df["close"], window=14).rsi().iloc[-1]
            volume = df["volume"].iloc[-1]
            avg_volume = df["volume"].mean()
            if rsi < 30 and volume > avg_volume * 1.5:
                msg = f"📉 Oversold Signal\\nSymbol: {symbol}\\nRSI: {rsi:.2f}\\nVolume: {volume:.2f}"
                await bot.send_message(chat_id=CHAT_ID, text=msg)
            elif rsi > 70 and volume > avg_volume * 1.5:
                msg = f"📈 Overbought Signal\\nSymbol: {symbol}\\nRSI: {rsi:.2f}\\nVolume: {volume:.2f}"
                await bot.send_message(chat_id=CHAT_ID, text=msg)
        except Exception as e:
            await bot.send_message(chat_id=CHAT_ID, text=f"Error for {symbol}: {str(e)}")

@app.route('/')
def home():
    loop = asyncio.get_event_loop()
    if loop.is_closed():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    loop.create_task(analyze_and_send())
    return "Bot is analyzing and running!"

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=10000)
