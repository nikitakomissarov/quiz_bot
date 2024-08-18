from fuzzywuzzy import fuzz


def retrive_question(redis_gate, user_id):
    user_question = redis_gate.get(user_id)
    if user_question is None:
        result = 'Вопрос не найден'
    else:
        result = user_question
    return result


def check_answer(quiz, user_answer, user_question):
    correct_solution = quiz.get(user_question.decode('utf-8'))
    ration = fuzz.ratio(correct_solution.lower(), user_answer.lower())
    coincidence_rate = 30 if len(correct_solution.split()) > 1 else 60
    if ration < coincidence_rate:
        result = 'Неправильно… Попробуешь ещё раз?'
    else:
        result = 'Правильно! Поздравляю! Для следующего вопроса нажми «Новый вопрос»'
    return result
