import argparse
import sys
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from handlers.start import start_handler, help_handler
import config

async def tg_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    response = await start_handler()
    await update.message.reply_text(response)

async def tg_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    response = await help_handler()
    await update.message.reply_text(response)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--test", type=str, help="Run in test mode")
    args = parser.parse_args()

    # Режим теста (P0.2)
    if args.test:
        if args.test == "/start":
            print(asyncio.run(start_handler()))
        elif args.test == "/help":
            print(asyncio.run(help_handler()))
        elif args.test == "/health":
            print("Backend status: OK")
        else:
            print(f"Command {args.test} not implemented yet.")
        sys.exit(0)

    if not config.BOT_TOKEN or "ВАШ_ТОКЕН" in config.BOT_TOKEN:
        print("Error: Invalid BOT_TOKEN")
        sys.exit(1)

    print("Starting Telegram bot... (real mode)")
    application = ApplicationBuilder().token(config.BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", tg_start))
    application.add_handler(CommandHandler("help", tg_help))
    application.run_polling()

if __name__ == "__main__":
    main()
