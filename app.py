import asyncio
import os
import logging
import requests
import pandas as pd
from ta.momentum import RSIIndicator
from telegram import Bot
from telegram.error import NetworkError as TelegramNetworkError
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Configuration
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
SYMBOLS = ["BTCUSDT", "ETHUSDT", "BNBUSDT"]  # Add more symbols as needed
CHECK_INTERVAL = 900  # 15 minutes in seconds

# Validate environment variables
if not TELEGRAM_BOT_TOKEN or not CHAT_ID:
    raise ValueError("TELEGRAM_BOT_TOKEN and CHAT_ID must be set in environment variables")

# Initialize Telegram bot
bot = Bot(token=TELEGRAM_BOT_TOKEN)

def fetch_data(symbol):
    url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval=15m&limit=100"
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raises exception for 4xx/5xx errors
    except requests.exceptions.RequestException as e:
        raise ValueError(f"Failed to fetch data for {symbol}: {str(e)}")

    try:
        data = response.json()
    except ValueError:
        raise ValueError(f"Invalid JSON response from Binance API for {symbol}")

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
                logger.info(f"Sent oversold signal for {symbol}: RSI={rsi:.2f}, Volume={volume:.2f}")
            elif rsi > 70 and volume > avg_volume * 1.5:
                msg = f"📈 Overbought Signal\nSymbol: {symbol}\nRSI: {rsi:.2f}\nVolume: {volume:.2f}"
                await bot.send_message(chat_id=CHAT_ID, text=msg)
                logger.info(f"Sent overbought signal for {symbol}: RSI={rsi:.2f}, Volume={volume:.2f}")

        except Exception as e:
            error_msg = f"Error for {symbol}: {str(e)}"
            logger.error(error_msg)
            try:
                await bot.send_message(chat_id=CHAT_ID, text=error_msg)
            except TelegramNetworkError as te:
                logger.error(f"Failed to send Telegram error message: {str(te)}")

async def main():
    loop = asyncio.get_event_loop()
    if loop.is_closed():
        logger.warning("Event loop was closed, creating a new one")
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    while True:
        try:
            logger.info("Starting analysis cycle")
            await analyze_and_send()
            logger.info(f"Completed analysis cycle, waiting {CHECK_INTERVAL} seconds")
            await asyncio.sleep(CHECK_INTERVAL)
        except Exception as e:
            logger.error(f"Main loop error: {str(e)}")
            try:
                await bot.send_message(chat_id=CHAT_ID, text=f"Main loop error: {str(e)}")
            except TelegramNetworkError as te:
                logger.error(f"Failed to send main loop error to Telegram: {str(te)}")
            await asyncio.sleep(CHECK_INTERVAL)  # Wait before retrying

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Shutting down gracefully")
    except Exception as e:
        logger.error(f"Fatal error in main: {str(e)}")