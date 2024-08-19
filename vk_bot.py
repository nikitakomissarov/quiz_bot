import json
import logging
import random
from logging.handlers import TimedRotatingFileHandler

import redis
import vk_api
from telegram import Bot
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.longpoll import VkLongPoll, VkEventType

from config import load_settings
from logger import TelegramLogsHandler
from redis_interaction import check_answer, retrive_question

logger_info = logging.getLogger('loggerinfo')
logger_error = logging.getLogger("loggererror")


def handle_new_question_request(vk,
                                quiz,
                                redis_gate,
                                user_id, keyboard,
                                giveup_solution=False):
    question_text = random.choice(list(quiz.keys()))
    correct_solution = quiz.get(question_text)
    redis_gate.set(user_id, question_text)
    reply(user_id, vk, question_text, keyboard, giveup_solution)
    return question_text, correct_solution


def handle_solution_attempt(quiz, redis_gate, user_id, text, vk, keyboard, user_question=None):
    user_id = user_id
    user_answer = text
    user_question = retrive_question(redis_gate, user_id)
    result = user_question if user_question == 'Вопрос не найден' else check_answer(quiz, user_answer, user_question)
    reply(user_id, vk, result, keyboard)


def reply(user_id, vk, text, keyboard, correct_solution=False):
    vk.messages.send(user_id=user_id,
                     message=(correct_solution + '\n\n' +
                              text if correct_solution != False else text),
                     keyboard=keyboard.get_keyboard(),
                     random_id=random.randint(1, 1000))


def handle_vk_events(longpoll, vk, quiz, redis_gate, keyboard):
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            text = event.text
            user_id = event.user_id
            if text == "Новый вопрос":
                question_text, correct_solution = handle_new_question_request(
                    vk, quiz, redis_gate, user_id, keyboard)
            elif text == "Сдаться":
                try:
                    giveup_solution = "Правильный ответ: " + correct_solution
                    question_text, correct_solution = handle_new_question_request(
                        vk, quiz, redis_gate, user_id, keyboard, giveup_solution)
                except UnboundLocalError:
                    refused_surrendering = 'Вы не можете сдаться, пока не зададите вопрос.'
                    reply(user_id, vk, keyboard, refused_surrendering)
            elif text == "Привет":
                greeting_text = "Привет! Я бот для викторин. Нажми кнопку «Новый вопрос», чтобы проверить свои знания."
                reply(user_id, vk, keyboard, greeting_text)
            else:
                handle_solution_attempt(quiz, redis_gate, user_id, text, vk, keyboard)


def main():
    settings = load_settings()

    VK_TOKEN = settings['VK_TOKEN']
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

    keyboard = VkKeyboard(one_time=True)
    keyboard.add_button('Новый вопрос', color=VkKeyboardColor.POSITIVE)
    keyboard.add_button('Сдаться', color=VkKeyboardColor.NEGATIVE)
    keyboard.add_button('Мой счёт', color=VkKeyboardColor.PRIMARY)

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
            handle_vk_events(longpoll, vk, quiz, redis_gate, keyboard)

        except Exception:
            logger_error.exception('Error')


if __name__ == '__main__':
    main()
