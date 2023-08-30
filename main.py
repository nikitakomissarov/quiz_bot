import json
from dotenv import dotenv_values
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

config = dotenv_values('.env')
TG_TOKEN = config['TG_TOKEN']


async def start(update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Здравстуйте")


async def reply(update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text=text)


def main():
    application = Application.builder().token(TG_TOKEN).build()
    application.add_handler(CommandHandler('start', start))
    application.add_handler(MessageHandler(filters.TEXT, reply))
    application.run_polling()


if __name__ == '__main__':
    main()
