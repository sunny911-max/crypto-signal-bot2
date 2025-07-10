import asyncio
import os
import requests
import pandas as pd
from ta.momentum import RSIIndicator
from telegram import Bot
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
SYMBOLS = ["BTCUSDT", "ETHUSDT", "BNBUSDT"]  # Add more symbols as needed
CHECK_INTERVAL = 900  # 15 minutes in seconds

# Initialize Telegram bot
bot = Bot(token=TELEGRAM_BOT_TOKEN)

def fetch_data(symbol):
    url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval=15m&limit=100"
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raises exception for 4xx/5xx errors
    except requests.exceptions.RequestException as e:
        raise ValueError(f"Failed to fetch data: {str(e)}")

    try:
        data = response.json()
    except ValueError:
        raise ValueError("Invalid JSON response from Binance API")

    if not data or len(data) < 14:  # RSI needs at least 14 points
        raise ValueError(f"Insufficient data returned for {symbol}")

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

async def main():
    while True:
        try:
            print("Running analysis...")
            await analyze_and_send()
            print(f"Waiting {CHECK_INTERVAL} seconds until next check...")
            await asyncio.sleep(CHECK_INTERVAL)
        except Exception as e:
            print(f"Main loop error: {str(e)}")
            await bot.send_message(chat_id=CHAT_ID, text=f"Main loop error: {str(e)}")
            await asyncio.sleep(CHECK_INTERVAL)  # Wait before retrying

if __name__ == "__main__":
    asyncio.run(main())