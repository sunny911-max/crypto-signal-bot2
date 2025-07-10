import logging
import os
from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, ContextTypes

# Telegram bot token and chat ID from environment
TOKEN = os.getenv("TELEGRAM_TOKEN") or "YOUR_BOT_TOKEN"
CHAT_ID = os.getenv("CHAT_ID") or "YOUR_CHAT_ID"

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Flask app
flask_app = Flask(__name__)
bot = Bot(token=TOKEN)

# Telegram bot application
tg_app = Application.builder().token(TOKEN).build()

# Command handler: /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Welcome! High-risk scalping signals coming soon!")

# Command handler: /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Use /start to begin. Bot will auto-post high-risk scalping signals.")

# Add handlers
tg_app.add_handler(CommandHandler("start", start))
tg_app.add_handler(CommandHandler("help", help_command))

# Example function to simulate a crypto signal (you can expand this)
async def send_crypto_signal():
    try:
        msg = "⚡️ New Signal: Buy BTCUSDT (1m) - RSI oversold + high volume"
        await bot.send_message(chat_id=CHAT_ID, text=msg)
    except Exception as e:
        logger.error(f"Failed to send message: {e}")

# Flask webhook route
@flask_app.route('/webhook', methods=['POST'])
def webhook():
    if request.method == "POST":
        update = Update.de_json(request.get_json(force=True), bot)
        tg_app.update_queue.put_nowait(update)
        return 'ok'
    return 'not allowed'

# Root check
@flask_app.route('/', methods=['GET'])
def root():
    return "🚀 Crypto Signal Bot Running!"

# Start everything
if __name__ == '__main__':
    import asyncio
    from threading import Thread

    async def run_bot():
        await tg_app.initialize()
        await tg_app.start()
        logger.info("Telegram Bot is running...")

    Thread(target=lambda: asyncio.run(run_bot())).start()
    flask_app.run(host='0.0.0.0', port=10000)
