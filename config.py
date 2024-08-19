import os

from dotenv import load_dotenv


def load_settings():
    load_dotenv()
    settings = {
        'TG_TOKEN': os.environ['TG_TOKEN'],
        'QUIZ_FILE': os.environ['QUIZ_FILE'],
        'TG_CHAT_ID': os.environ['TG_CHAT_ID'],
        'TG_LOGGER_TOKEN': os.environ['TG_LOGGER_TOKEN'],
        'VK_TOKEN': os.environ['VK_TOKEN'],
        'PORT': os.environ['PORT'],
        'HOST': os.environ['HOST'],
        'PASSWORD': os.environ['PASSWORD'],
        'DEFAULT_QUIZ_FOLDER_PATH': os.path.abspath('quiz_files')
    }
    return settings
