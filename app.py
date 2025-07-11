import os
from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import Dispatcher, CommandHandler, MessageHandler, filters

# Set up Flask app
app = Flask(__name__)

# Use your environment variable or directly paste your token here
BOT_TOKEN = os.environ.get("BOT_TOKEN", "7307067620:AAEOHrNskxLEWOcMKvuKtVbrJUYpD0zokMA")

# Check if token is valid
if not BOT_TOKEN or BOT_TOKEN.startswith("YOUR_"):
    raise ValueError("❌ Invalid BOT_TOKEN provided")

# Set up bot and dispatcher
bot = Bot(token=BOT_TOKEN)
dispatcher = Dispatcher(bot=bot, update_queue=None, workers=1, use_context=True)

# Simple /start command
def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="✅ Bot is working!")

# Fallback for any text
def echo(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="You said: " + update.message.text)

# Add handlers
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

# Flask routes
@app.route("/")
def index():
    return "Bot is live ✅"

@app.route("/webhook", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return "ok"
