import logging
import os
from queue import Queue

import anyio
from dotenv import load_dotenv

from devman import devman_long_poll
from logs import setup_logging
from tg_bot import TelegramBot


def get_env_vars() -> tuple[str, str, str]:
    bot_token = os.getenv("BOT_TOKEN")
    api_token = os.getenv("API_TOKEN")
    chat_id = os.getenv("CHAT_ID")
    if not all((bot_token, api_token, chat_id)):
        raise ValueError("Не настроены необходимые переменные окружения")
    return bot_token, api_token, chat_id


async def main():
    try:
        bot_token, api_token, chat_id = get_env_vars()
        attempts_send, attempts_recv = anyio.create_memory_object_stream()
        logs_queue = Queue()

        bot = TelegramBot(bot_token, chat_id)
        setup_logging(logs_queue)

        async with anyio.create_task_group() as tg:
            tg.start_soon(bot.logs_polling, logs_queue)
            tg.start_soon(bot.attempts_polling, attempts_recv)
            tg.start_soon(devman_long_poll, api_token, attempts_send)
    except ValueError as e:
        logging.error(str(e))
        return


if __name__ == "__main__":
    load_dotenv()
    try:
        anyio.run(main)
    except KeyboardInterrupt:
        logging.info("Завершение работы")
