import json
import logging
from dotenv import load_dotenv
import os
import redis
import random
from logging.handlers import TimedRotatingFileHandler
from telegram.ext import Application

import vk_api
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.longpoll import VkLongPoll, VkEventType

from logger import TelegramLogsHandler
from redis_interaction import check_answer, PORT, HOST, PASSWORD

load_dotenv()

VK_TOKEN = os.environ['VK_TOKEN']
QUIZ_FILE = os.environ['QUIZ_FILE']
TG_CHAT_ID = os.environ['TG_CHAT_ID']
TG_LOGGER_TOKEN = os.environ['TG_LOGGER_TOKEN']

logger_bot = Application.builder().token(TG_LOGGER_TOKEN).build().bot

logger_info = logging.getLogger('loggerinfo')
logger_error = logging.getLogger("loggererror")

keyboard = VkKeyboard(one_time=True)
keyboard.add_button('Новый вопрос', color=VkKeyboardColor.POSITIVE)
keyboard.add_button('Сдаться', color=VkKeyboardColor.NEGATIVE)
keyboard.add_button('Мой счёт', color=VkKeyboardColor.PRIMARY)


def handle_new_question_request(vk,
                                quiz,
                                redis_gate,
                                user_id,
                                giveup_solution=False):
    question_text = random.choice(list(quiz.keys()))
    correct_solution = quiz.get(question_text)
    redis_gate.set(user_id, question_text)
    reply(user_id, vk, question_text, giveup_solution)
    return question_text, correct_solution


def handle_solution_attempt(quiz, redis_gate, user_id, text, vk):
    user_id = user_id
    user_answer = text
    result = check_answer(quiz, redis_gate, user_id, user_answer)
    reply(user_id, vk, result)


def reply(user_id, vk, text, correct_solution=False):
    vk.messages.send(user_id=user_id,
                     message=(correct_solution + '\n\n' +
                              text if correct_solution != False else text),
                     keyboard=keyboard.get_keyboard(),
                     random_id=random.randint(1, 1000))


def handle_vk_events(longpoll, vk, quiz, redis_gate):
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            text = event.text
            user_id = event.user_id
            if text == "Новый вопрос":
                question_text, correct_solution = handle_new_question_request(
                    vk, quiz, redis_gate, user_id)
            elif text == "Сдаться":
                try:
                    giveup_solution = "Правильный ответ: " + correct_solution
                    question_text, correct_solution = handle_new_question_request(
                        vk, quiz, redis_gate, user_id, giveup_solution)
                except UnboundLocalError:
                    refused_surrendering = 'Вы не можете сдаться, пока не зададите вопрос.'
                    reply(user_id, vk, refused_surrendering)
            elif text == "Привет":
                greeting_text = "Привет! Я бот для викторин. Нажми кнопку «Новый вопрос», чтобы проверить свои знания."
                reply(user_id, vk, greeting_text)
            else:
                handle_solution_attempt(quiz, redis_gate, user_id, text, vk)


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
    telegram_notification_handler = TelegramLogsHandler(logger_bot, TG_CHAT_ID)
    telegram_notification_handler.setFormatter(handler_format)
    logger_error.addHandler(telegram_notification_handler)

    while True:
        try:
            with open(QUIZ_FILE, "r", encoding='utf-8') as quiz_file:
                quiz = json.load(quiz_file)

            redis_gate = redis.Redis(
            host=HOST,
            port=PORT,
            password=PASSWORD)

            vk_session = vk_api.VkApi(token=VK_TOKEN)
            longpoll = VkLongPoll(vk_session)
            vk = vk_session.get_api()

            logger_info.info("here we go")
            handle_vk_events(longpoll, vk, quiz, redis_gate)

        except Exception:
            logger_error.exception('Error')


if __name__ == '__main__':
    main()
