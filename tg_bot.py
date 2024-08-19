import json
import logging
import random
from enum import Enum, auto
from functools import partial
from logging.handlers import TimedRotatingFileHandler

import redis
from telegram import ReplyKeyboardMarkup, Bot
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, ConversationHandler, filters

from config import load_settings
from logger import TelegramLogsHandler
from redis_interaction import check_answer, retrive_question

REPLY_KEYBOARD = [["Новый вопрос", "Сдаться", "Мой счёт"]]
MARKUP = ReplyKeyboardMarkup(REPLY_KEYBOARD,
                             one_time_keyboard=False,
                             input_field_placeholder="Нажмите кнопку")

logger_info = logging.getLogger('loggerinfo')
logger_error = logging.getLogger("loggererror")


class Handlers(Enum):
    handle_new_question_request = auto()
    handle_solution_attempt = auto()
    handle_giveup = auto()


async def start(update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Я бот для викторин.",

                                    reply_markup=MARKUP)
    return Handlers.handle_new_question_request.value


async def cancel(update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Пока!")
    return ConversationHandler.END


async def handle_new_question_request(quiz, redis_gate, update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.chat.id
    question_text = random.choice(list(quiz.keys()))
    context.user_data['correct_solution'] = quiz.get(question_text)
    await update.message.reply_text(question_text, reply_markup=MARKUP)
    redis_gate.set(user_id, question_text)
    return Handlers.handle_solution_attempt.value


async def handle_solution_attempt(quiz, redis_gate, update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.chat.id
    user_answer = update.message.text
    user_question = retrive_question(redis_gate, user_id)
    reply = user_question if user_question == 'Вопрос не найден' else check_answer(quiz, user_answer, user_question)
    await update.message.reply_text(reply, reply_markup=MARKUP)


async def give_up(quiz, redis_gate, update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Правильный ответ: " + context.user_data['correct_solution'])
    await handle_new_question_request(quiz, redis_gate, update, context)


def main():
    settings = load_settings()

    TG_TOKEN = settings['TG_TOKEN']
    QUIZ_FILE = settings['QUIZ_FILE']
    TG_CHAT_ID = settings['TG_CHAT_ID']
    TG_LOGGER_TOKEN = settings['TG_LOGGER_TOKEN']

    PORT = settings['PORT']
    HOST = settings['HOST']
    PASSWORD = settings['PASSWORD']

    logger_bot = Bot(token=TG_LOGGER_TOKEN)

    handler = TimedRotatingFileHandler("app.log",
                                       when='D',
                                       interval=30,
                                       backupCount=1)
    handler_format = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(handler_format)
    logger_info.setLevel(logging.INFO)
    logger_info.addHandler(handler)
    logger_error.setLevel(logging.ERROR)
    logger_error.addHandler(handler)
    telegram_notification_handler = TelegramLogsHandler(logger_bot, TG_CHAT_ID)
    telegram_notification_handler.setFormatter(handler_format)
    logger_error.addHandler(telegram_notification_handler)

    try:
        with open(QUIZ_FILE, "r", encoding='utf-8') as quiz_file:
            quiz = json.load(quiz_file)
        redis_gate = redis.Redis(
            host=HOST,
            port=PORT,
            password=PASSWORD)
        conv_handler = ConversationHandler(
            entry_points=[CommandHandler('start', start)],
            states={
                Handlers.handle_new_question_request.value: [
                    MessageHandler(
                        filters.Regex('Новый вопрос'),
                        partial(handle_new_question_request, quiz, redis_gate))

                ],
                Handlers.handle_solution_attempt.value: [
                    MessageHandler(
                        filters.TEXT & ~filters.Regex('Новый вопрос') & ~filters.Regex('Сдаться') & ~filters.COMMAND,
                        partial(handle_solution_attempt, quiz, redis_gate)),
                    MessageHandler(
                        filters.Regex('Новый вопрос'),
                        partial(handle_new_question_request, quiz, redis_gate)),
                    MessageHandler(
                        filters.Regex('Сдаться'),
                        partial(give_up, quiz, redis_gate))
                ]
            },
            fallbacks=[CommandHandler('cancel', cancel)])

        application = Application.builder().token(TG_TOKEN).build()
        application.add_handler(conv_handler)
        application.run_polling()
        logger_info.info("here we go")

    except Exception:
        logger_error.exception('Error')


if __name__ == '__main__':
    main()
