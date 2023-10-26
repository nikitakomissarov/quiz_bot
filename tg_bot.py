import json
import random
import os
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, ConversationHandler, filters
from functools import partial
from telegram import ReplyKeyboardMarkup, Update
from redis_interaction import connection, write_in, answer_checker, PORT, HOST, PASSWORD
from enum import Enum, auto
import logging
from logging.handlers import TimedRotatingFileHandler
from logger import TelegramLogsHandler, logger_bot

TG_TOKEN = os.environ['TG_TOKEN']
QUIZ_FILE = os.environ['QUIZ_FILE']


class Handlers(Enum):
    HANDLE_NEW_QUESTION_REQUEST = auto()
    HANDLE_SOLUTION_ATTEMPT = auto()
    HANDLE_GIVEUP = auto()


logger_info = logging.getLogger('loggerinfo')
logger_error = logging.getLogger("loggererror")

reply_keyboard = [["Новый вопрос", "Сдаться", "Мой счёт"]]
markup = ReplyKeyboardMarkup(reply_keyboard,
                             one_time_keyboard=False,
                             input_field_placeholder="Нажмите кнопку")


async def start(update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Я бот для викторин.",

                                    reply_markup=markup)
    return Handlers.HANDLE_NEW_QUESTION_REQUEST.value


async def cancel(update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Пока!")
    return ConversationHandler.END


async def handle_new_question_request(quiz, redis_gate, update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.chat.id
    question_text = random.choice(list(quiz.keys()))
    context.user_data['correct_solution'] = quiz.get(question_text)
    await update.message.reply_text(question_text, reply_markup=markup)
    write_in(redis_gate, user_id, question_text)
    return Handlers.HANDLE_SOLUTION_ATTEMPT.value


async def handle_solution_attempt(quiz, redis_gate, update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.chat.id
    answer = update.message.text
    reply = answer_checker(quiz, redis_gate, user_id, answer)
    await update.message.reply_text(reply, reply_markup=markup)


async def give_up(quiz, redis_gate, update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Правильный ответ: " + context.user_data['correct_solution'])
    await handle_new_question_request(quiz, redis_gate, update, context)


def main():
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
    telegram_notification_handler = TelegramLogsHandler(logger_bot)
    telegram_notification_handler.setFormatter(handler_format)
    logger_error.addHandler(telegram_notification_handler)

    try:
        with open(QUIZ_FILE, "r", encoding='utf-8') as quiz_file:
            quiz = json.load(quiz_file)

        redis_gate = connection(PORT, HOST, PASSWORD)

        conv_handler = ConversationHandler(
            entry_points=[CommandHandler('start', start)],
            states={
                Handlers.HANDLE_NEW_QUESTION_REQUEST.value: [
                    MessageHandler(
                        filters.Regex('Новый вопрос'),
                        partial(handle_new_question_request, quiz, redis_gate))

                ],
                Handlers.HANDLE_SOLUTION_ATTEMPT.value: [
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
