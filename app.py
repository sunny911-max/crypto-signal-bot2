import os
import asyncio
import logging
from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, ContextTypes

from signal_generator import analyze_and_send  # Your custom logic
from threading import Thread

# Environment variables
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # e.g. https://your-bot-url.onrender.com/webhook

# Telegram Bot + Flask App
app = Flask(__name__)
application = Application.builder().token(BOT_TOKEN).build()
bot = Bot(BOT_TOKEN)

logging.basicConfig(level=logging.INFO)

# === Flask Route to Receive Webhook Updates ===
@app.post("/webhook")
async def webhook() -> tuple:
    """Webhook endpoint to receive Telegram updates"""
    update = Update.de_json(request.get_json(force=True), bot)
    await application.process_update(update)
    return "ok", 200

# === Telegram Command Handler ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🚀 Bot is online and ready to send high-risk crypto signals!")

application.add_handler(CommandHandler("start", start))

# === Background Task to Run Trading Signal Loop ===
def run_signal_loop():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    while True:
        try:
            loop.run_until_complete(analyze_and_send(bot, CHAT_ID))
            asyncio.sleep(60)  # Check every 60s
        except Exception as e:
            print(f"Error in loop: {e}")

# === Startup Hook to Set Webhook ===
@app.before_first_request
def setup():
    asyncio.get_event_loop().run_until_complete(bot.set_webhook(url=WEBHOOK_URL))
    Thread(target=run_signal_loop).start()

# === Render Web Service Ping Route ===
@app.route("/", methods=["GET"])
def home():
    return "✅ Bot running", 200

# === Run Flask app ===
if __name__ == "__main__":
    app.run(debug=False, port=10000, host="0.0.0.0")
