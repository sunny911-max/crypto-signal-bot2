from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import os
import asyncio

# --- Bot Config ---
BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN or "your" in BOT_TOKEN:
    raise Exception("🚨 Set a valid BOT_TOKEN in your Render environment variables")

# --- Flask App ---
app = Flask(__name__)

# --- Telegram Bot App ---
telegram_app = Application.builder().token(BOT_TOKEN).build()

# --- Command: /start ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ Bot is alive and webhook is working!")

# --- Echo handler ---
async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"📨 You said: {update.message.text}")

# --- Register Handlers ---
telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

# --- Webhook endpoint ---
@app.route("/webhook", methods=["POST"])
async def webhook():
    update = Update.de_json(request.get_json(force=True), telegram_app.bot)
    await telegram_app.process_update(update)
    return "ok"

# --- Health check ---
@app.route("/", methods=["GET"])
def index():
    return "⚡ Bot is deployed and running!"
