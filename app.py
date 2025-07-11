from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import asyncio

# === BOT CONFIG ===
BOT_TOKEN = "7307067620:AAEOHrNskxLEWOcMKvuKtVbrJUYpD0zokMA"
CHAT_ID = -4932382154  # Group or user ID

app = Flask(__name__)
bot = Bot(token=BOT_TOKEN)

# === Command: /start ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ Bot is live and responding!")

# === Create Application ===
application = ApplicationBuilder().token(BOT_TOKEN).build()
application.add_handler(CommandHandler("start", start))

# === Flask Route for Webhook ===
@app.route("/webhook", methods=["POST"])
async def webhook():
    data = request.get_json(force=True)
    update = Update.de_json(data, bot)
    await application.process_update(update)
    return "OK", 200

# === Root test ===
@app.route("/")
def index():
    return "👋 Bot is running."
