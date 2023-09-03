import time
import re
import json


quiz = dict()

for number in range(1, 4):
    filename = str(number) + '.txt'
    with open(filename, 'r', encoding='KOI8-R') as quiz_set:
        quiz_set = quiz_set.read()
        question_text = re.findall(r'Вопрос \d+:\s*(.*?)(?=Ответ:)', quiz_set, re.DOTALL)
        answer_text = re.findall(r'Ответ:\s*(.*)', quiz_set)
        question_text = [q.replace('\n', ' ') for q in question_text]
        answer_text = [a.replace('\n', ' ') for a in answer_text]
        next_quiz = {key: value for key, value in zip(question_text, answer_text)}
        quiz.update(next_quiz)


with open('quiz_file.json', 'w', encoding='utf-8') as f:
    json.dump(quiz, f, ensure_ascii=False, indent=4)


print(quiz)
