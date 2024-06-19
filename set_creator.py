import json
import re
import argparse
import os

DEFAULT_QUIZ_FOLDER_PATH = os.path.abspath('quiz_files')


def main():
    parser = argparse.ArgumentParser(
        description='Программам создает сет вопросов для бота-викторины'
    )
    parser.add_argument('-f', '--file_path', default=DEFAULT_QUIZ_FOLDER_PATH, help='Пользовательский путь к файлу')
    args = parser.parse_args()

    quiz = dict()

    for preset_file in os.listdir(path=args.file_path):
        preset_file = os.path.join(args.file_path, preset_file)
        with open(preset_file, 'r', encoding='KOI8-R') as quiz_set:
            quiz_set = quiz_set.read()

        question_text = re.findall(r'Вопрос \d+:\s*(.*?)(?=Ответ:)', quiz_set, re.DOTALL)
        answer_text = re.findall(r'Ответ:\s*(.*)', quiz_set)
        question_text = [q.replace('\n', ' ') for q in question_text]
        answer_text = [a.replace('\n', ' ') for a in answer_text]
        next_quiz = {key: value for key, value in zip(question_text, answer_text)}
        quiz.update(next_quiz)

    with open('quiz_file.json', 'w', encoding='utf-8') as f:
        json.dump(quiz, f, ensure_ascii=False)


if __name__ == '__main__':
    main()
