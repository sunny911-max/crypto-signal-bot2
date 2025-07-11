import os
from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, ContextTypes

BOT_TOKEN = os.environ.get("BOT_TOKEN")

# Safety check
if not BOT_TOKEN:
    raise ValueError("Missing BOT_TOKEN in environment variables")

bot = Bot(token=BOT_TOKEN)
app = Flask(__name__)
telegram_app = Application.builder().token(BOT_TOKEN).build()

# Command handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ Bot is alive!")

telegram_app.add_handler(CommandHandler("start", start))

@app.route("/", methods=["GET"])
def home():
    return "✅ Bot running."

@app.route("/webhook", methods=["POST"])
async def webhook():
    data = request.get_json(force=True)
    update = Update.de_json(data, bot)
    await telegram_app.process_update(update)
    return "ok"
