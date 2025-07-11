import os
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

BOT_TOKEN = os.environ.get("BOT_TOKEN", "7307067620:AAEOHrNskxLEWOcMKvuKtVbrJUYpD0zokMA")

if not BOT_TOKEN or BOT_TOKEN.startswith("YOUR_"):
    raise ValueError("Invalid BOT_TOKEN!")

# Flask setup
app = Flask(__name__)

# Telegram app setup
tg_app = Application.builder().token(BOT_TOKEN).build()

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ Bot is working!")

# Echo for other messages
async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"You said: {update.message.text}")

# Register handlers
tg_app.add_handler(CommandHandler("start", start))
tg_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

# Flask routes
@app.route("/")
def home():
    return "Bot is live ✅"

@app.route("/webhook", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), tg_app.bot)
    tg_app.update_queue.put_nowait(update)
    return "ok"
