import asyncio
import logging


class TelegramLogsHandler(logging.Handler):

    def __init__(self, bot_logger, tg_chat_id):
        super().__init__()
        self.bot_logger = bot_logger
        self.tg_chat_id = tg_chat_id

    def emit(self, record):
        log_entry = self.format(record)
        loop = asyncio.get_event_loop()
        if loop.is_running():
            loop.create_task(self.bot_logger.send_message(chat_id=self.tg_chat_id, text=log_entry))
        else:
            loop.run_until_complete(self.bot_logger.send_message(chat_id=self.tg_chat_id, text=log_entry))
