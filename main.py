import asyncio
import logging
import os

import anyio
from dotenv import load_dotenv

from devman import devman_long_poll, Attempt
from tg_bot import bot_polling

logger = logging.getLogger(__file__)


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
        attempts_queue: asyncio.Queue[Attempt] = asyncio.Queue()
        async with anyio.create_task_group() as tg:
            tg.start_soon(devman_long_poll, api_token, attempts_queue)
            tg.start_soon(bot_polling, bot_token, chat_id, attempts_queue)
    except ValueError as e:
        logger.error(str(e))
        return


if __name__ == "__main__":
    load_dotenv()
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.WARNING,
    )
    try:
        anyio.run(main)
    except KeyboardInterrupt:
        logging.info("Завершение работы")
