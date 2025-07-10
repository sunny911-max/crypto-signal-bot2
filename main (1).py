import asyncio
import os
import requests
import pandas as pd
from ta.momentum import RSIIndicator
from telegram import Bot
from telegram.error import TelegramError
import time
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configuration
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
SYMBOLS = ["BTCUSDT", "ETHUSDT", "BNBUSDT"]  # Add your trading symbols here
CHECK_INTERVAL = 900  # 15 minutes in seconds

# Validate environment variables
if not BOT_TOKEN or not CHAT_ID:
    raise ValueError("TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID must be set in environment variables")

# Initialize Telegram bot
bot = Bot(token=BOT_TOKEN)

def fetch_data(symbol):
    url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval=15m&limit=100"
    try:
        response = requests.get(url)
        if response.status_code != 200:
            raise ValueError(f"Failed to fetch data: {response.status_code}")

        data = response.json()
        if not data or len(data) < 20:  # RSI needs at least 14 points
            raise ValueError(f"Insufficient data returned for {symbol}")

        df = pd.DataFrame(data, columns=[
            "timestamp", "open", "high", "low", "close", "volume",
            "close_time", "quote_asset_volume", "number_of_trades",
            "taker_buy_base_volume", "taker_buy_quote_volume", "ignore"
        ])
        df["close"] = pd.to_numeric(df["close"])
        df["volume"] = pd.to_numeric(df["volume"])
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
        return df
    except requests.exceptions.RequestException as e:
        raise ValueError(f"Request failed for {symbol}: {str(e)}")
    except ValueError as e:
        raise e
    except Exception as e:
        raise ValueError(f"Unexpected error fetching data for {symbol}: {str(e)}")

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
            error_msg = f"Error for {symbol}: {str(e)}"
            try:
                await bot.send_message(chat_id=CHAT_ID, text=error_msg)
            except TelegramError as te:
                print(f"Failed to send Telegram message: {te}")

async def main():
    print("Starting bot...")
    while True:
        try:
            await analyze_and_send()
            print(f"Analysis completed at {pd.Timestamp.now()}. Waiting {CHECK_INTERVAL} seconds...")
        except Exception as e:
            print(f"Main loop error: {str(e)}")
            try:
                await bot.send_message(chat_id=CHAT_ID, text=f"Main loop error: {str(e)}")
            except TelegramError as te:
                print(f"Failed to send Telegram error message: {te}")
        await asyncio.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    asyncio.run(main())