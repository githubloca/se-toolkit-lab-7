import argparse
import asyncio
import sys

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    CallbackQueryHandler,
    filters,
)

from handlers.commands.start import (
    start_handler,
    help_handler,
    health_handler,
    labs_handler,
    scores_handler,
)
from services.intent_router import route
import config


def start_keyboard():
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("What labs are available?", callback_data="q:what labs are available?")],
            [InlineKeyboardButton("Show scores for lab 4", callback_data="q:show me scores for lab 4")],
            [InlineKeyboardButton("Which lab has the lowest pass rate?", callback_data="q:which lab has the lowest pass rate?")],
            [InlineKeyboardButton("How many students are enrolled?", callback_data="q:how many students are enrolled")],
        ]
    )


async def wrap_handler(update: Update, func, *args):
    response = await func(*args)
    await update.message.reply_text(response)


async def tg_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    response = await start_handler()
    await update.message.reply_text(response, reply_markup=start_keyboard())


async def tg_help(u, c):
    await wrap_handler(u, help_handler)


async def tg_health(u, c):
    await wrap_handler(u, health_handler)


async def tg_labs(u, c):
    await wrap_handler(u, labs_handler)


async def tg_scores(u, c):
    lab_id = c.args[0] if c.args else None
    await wrap_handler(u, scores_handler, lab_id)


async def tg_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    response = await route(text)
    await update.message.reply_text(response)


async def tg_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data or ""
    if data.startswith("q:"):
        prompt = data[2:]
        response = await route(prompt)
        await query.message.reply_text(response)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--test", type=str)
    args = parser.parse_args()

    if args.test:
        text = args.test.strip()
        if text.startswith("/"):
            cmd = text.split()
            if cmd[0] == "/start":
                print(asyncio.run(start_handler()))
            elif cmd[0] == "/help":
                print(asyncio.run(help_handler()))
            elif cmd[0] == "/health":
                print(asyncio.run(health_handler()))
            elif cmd[0] == "/labs":
                print(asyncio.run(labs_handler()))
            elif cmd[0] == "/scores":
                lab = cmd[1] if len(cmd) > 1 else None
                print(asyncio.run(scores_handler(lab)))
            else:
                print("Unknown command. Try /help")
        else:
            print(asyncio.run(route(text)))
        sys.exit(0)

    app = ApplicationBuilder().token(config.BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", tg_start))
    app.add_handler(CommandHandler("help", tg_help))
    app.add_handler(CommandHandler("health", tg_health))
    app.add_handler(CommandHandler("labs", tg_labs))
    app.add_handler(CommandHandler("scores", tg_scores))
    app.add_handler(CallbackQueryHandler(tg_button))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, tg_text))
    app.run_polling()


if __name__ == "__main__":
    main()
