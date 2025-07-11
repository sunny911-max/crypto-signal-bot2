import os
import logging
from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

app = Flask(__name__)
bot = Bot(token=BOT_TOKEN)

@app.route('/')
def index():
    return 'Bot is running!'

@app.route('/webhook', methods=['POST'])
def webhook():
    if request.method == "POST":
        update = Update.de_json(request.get_json(force=True), bot)
        application = ApplicationBuilder().token(BOT_TOKEN).build()
        application.process_update(update)
    return 'ok'

# Optional: You can register /start here if needed
