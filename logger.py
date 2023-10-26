import logging
import asyncio
import os
from telegram.ext import Application


TG_CHAT_ID = os.environ['TG_CHAT_ID']
TG_LOGGER_TOKEN = os.environ['TG_LOGGER_TOKEN']

logger_bot = Application.builder().token(TG_LOGGER_TOKEN).build().bot


class TelegramLogsHandler(logging.Handler):

    def __init__(self, bot_logger):
        super().__init__()
        self.bot_logger = bot_logger

    def emit(self, record):
        log_entry = self.format(record)
        loop = asyncio.get_event_loop()
        if loop.is_running():
            loop.create_task(self.bot_logger.send_message(chat_id=TG_CHAT_ID, text=log_entry))
        else:
            loop.run_until_complete(self.bot_logger.send_message(chat_id=TG_CHAT_ID, text=log_entry))
