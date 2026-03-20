import argparse
import sys
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from handlers.start import start_handler
import config

async def tg_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    response = await start_handler()
    await update.message.reply_text(response)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--test", type=str, help="Run in test mode")
    args = parser.parse_args()

    if args.test:
        if args.test == "/start":
            print(asyncio.run(start_handler()))
        sys.exit(0)

    if not config.BOT_TOKEN or "ВАШ_ТОКЕН" in config.BOT_TOKEN:
        print("Error: Invalid or missing BOT_TOKEN in .env.bot.secret")
        sys.exit(1)

    print("Starting Telegram bot... (real mode)")
    
    # Добавляем увеличенные тайм-ауты для стабильности
    application = (
        ApplicationBuilder()
        .token(config.BOT_TOKEN)
        .read_timeout(30)
        .connect_timeout(30)
        .build()
    )
    
    application.add_handler(CommandHandler("start", tg_start))
    application.run_polling()

if __name__ == "__main__":
    main()
