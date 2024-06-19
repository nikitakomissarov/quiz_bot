from dotenv import load_dotenv
import os
from fuzzywuzzy import fuzz

load_dotenv()

PORT = os.environ['PORT']
HOST = os.environ['HOST']
PASSWORD = os.environ['PASSWORD']

def check_answer(quiz, redis_gate, user_id, user_answer):
    user_question = redis_gate.get(user_id)
    if user_question is None:
        result = 'Вопрос не найден'
        return result
    else:
        correct_solution = quiz.get(user_question.decode('utf-8'))
        ration = fuzz.ratio(correct_solution.lower(), user_answer.lower())
        coincidence_rate = 30 if len(correct_solution.split()) > 1 else 60
        if ration < coincidence_rate:
            result = 'Неправильно… Попробуешь ещё раз?'
        else:
            result = 'Правильно! Поздравляю! Для следующего вопроса нажми «Новый вопрос»'
        return result
