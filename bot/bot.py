import argparse, sys, asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from handlers.commands.start import start_handler, help_handler, health_handler, labs_handler, scores_handler
import config

async def wrap_handler(update: Update, func, *args):
    response = await func(*args)
    await update.message.reply_text(response)

async def tg_start(u, c): await wrap_handler(u, start_handler)
async def tg_help(u, c): await wrap_handler(u, help_handler)
async def tg_health(u, c): await wrap_handler(u, health_handler)
async def tg_labs(u, c): await wrap_handler(u, labs_handler)
async def tg_scores(u, c):
    lab_id = c.args[0] if c.args else None
    await wrap_handler(u, scores_handler, lab_id)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--test", type=str)
    args = parser.parse_args()

    if args.test:
        cmd = args.test.split()
        if cmd[0] == "/start": print(asyncio.run(start_handler()))
        elif cmd[0] == "/help": print(asyncio.run(help_handler()))
        elif cmd[0] == "/health": print(asyncio.run(health_handler()))
        elif cmd[0] == "/labs": print(asyncio.run(labs_handler()))
        elif cmd[0] == "/scores":
            lab = cmd[1] if len(cmd) > 1 else None
            print(asyncio.run(scores_handler(lab)))
        sys.exit(0)

    app = ApplicationBuilder().token(config.BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", tg_start))
    app.add_handler(CommandHandler("help", tg_help))
    app.add_handler(CommandHandler("health", tg_health))
    app.add_handler(CommandHandler("labs", tg_labs))
    app.add_handler(CommandHandler("scores", tg_scores))
    app.run_polling()

if __name__ == "__main__":
    main()
