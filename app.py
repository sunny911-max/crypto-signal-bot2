from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, ContextTypes
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=BOT_TOKEN)

# Flask app
app = Flask(__name__)

# Telegram app
telegram_app = Application.builder().token(BOT_TOKEN).build()

# Command handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello, I am your crypto bot!")

telegram_app.add_handler(CommandHandler("start", start))

# Webhook endpoint
@app.route("/webhook", methods=["POST"])
async def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    await telegram_app.process_update(update)
    return "OK"

# Health check route
@app.route("/", methods=["GET"])
def index():
    return "Bot is running."

# Only for local testing
if __name__ == "__main__":
    app.run(port=5000)
