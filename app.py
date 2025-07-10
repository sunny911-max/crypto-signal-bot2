from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import Dispatcher, CommandHandler
import asyncio
import logging

# === BOT CONFIGURATION ===
BOT_TOKEN = "7307067620:AAEOHrNskxLEWOcMKvuKtVbrJUYpD0zokMA"
CHAT_ID = -4932382154  # Your group/chat ID

bot = Bot(token=BOT_TOKEN)
app = Flask(__name__)

# === COMMAND HANDLER ===
async def start(update: Update, context):
    await update.message.reply_text("👋 Bot is live and ready!")

# === DISPATCHER ===
dispatcher = Dispatcher(bot, None, workers=0, use_context=True)
dispatcher.add_handler(CommandHandler("start", start))

# === WEBHOOK ENDPOINT ===
@app.route('/webhook', methods=["POST"])
def webhook_handler():
    if request.method == "POST":
        update = Update.de_json(request.get_json(force=True), bot)
        asyncio.run(dispatcher.process_update(update))
    return "OK"

# === ROOT ENDPOINT ===
@app.route('/')
def index():
    return "👋 Crypto Signal Bot is Running!"

# === OPTIONAL SIGNAL TESTING ===
# Add your custom `analyze_and_send()` here if you want automated alerts
