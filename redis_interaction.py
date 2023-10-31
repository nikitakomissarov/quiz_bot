import os
import redis
from fuzzywuzzy import fuzz

PORT = os.environ['PORT']
HOST = os.environ['HOST']
PASSWORD = os.environ['PASSWORD']


def connection(PORT, HOST, PASSWORD):
    connection = redis.Redis(
        host=HOST,
        port=PORT,
        password=PASSWORD)
    return connection


def write_in(redis_gate, user_id, question):
    redis_gate.set(user_id, question)


def answer_checker(quiz, redis_gate, user_id, user_answer):
    user_question = redis_gate.get(user_id).decode("utf-8")
    correct_solution = quiz.get(user_question)
    ration = fuzz.ratio(correct_solution.lower(), user_answer.lower())
    coincidence_rate = 30 if len(correct_solution.split()) > 1 else 60
    if ration < coincidence_rate:
        result = 'Неправильно… Попробуешь ещё раз?'
    else:
        result = 'Правильно! Поздравляю! Для следующего вопроса нажми «Новый вопрос»'
    return result
