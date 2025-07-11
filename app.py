import os
from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Replace with your actual token and chat ID
BOT_TOKEN = "your_real_token_here"
CHAT_ID = your_real_chat_id_here

# Create Flask app
app = Flask(__name__)

# Create Telegram app
telegram_app = Application.builder().token(BOT_TOKEN).build()

# Example command handler (optional)
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Bot is alive!")

telegram_app.add_handler(CommandHandler("start", start))

# Webhook route
@app.route("/webhook", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), Bot(BOT_TOKEN))
    telegram_app.update_queue.put_nowait(update)
    return "OK", 200

# Root route
@app.route("/", methods=["GET"])
def root():
    return "Bot is running via webhook!", 200

# Run the webhook server if running locally (not used in production gunicorn)
if __name__ == "__main__":
    telegram_app.run_webhook(
        listen="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        webhook_url=f"https://your-render-url.onrender.com/webhook"
    )
