import argparse
import asyncio
import logging
import os

import anyio
from dotenv import load_dotenv

from devman import devman_long_poll
from tg_bot import bot_polling

load_dotenv()

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
)


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Бот для уведомлений о проверке заданий на Devman",
        epilog="Пример использования: python bot.py --chat_id 123456789",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "-c", "--chat_id",
        type=str,
        required=True,
        help="ID чата в Telegram для отправки уведомлений"
    )

    return parser.parse_args()


def get_env_vars() -> tuple[str, str]:
    bot_token = os.getenv("BOT_TOKEN")
    api_token = os.getenv("API_TOKEN")
    if not all((bot_token, api_token)):
        raise ValueError("Не найдены BOT_TOKEN и (или) API_TOKEN в переменных окружения")
    return bot_token, api_token


async def main():
    try:
        args = parse_arguments()
        bot_token, api_token = get_env_vars()
    except ValueError as e:
        logging.error(str(e))
        return
    else:
        attempts_queue = asyncio.Queue()
        async with anyio.create_task_group() as tg:
            tg.start_soon(devman_long_poll, api_token, attempts_queue)
            tg.start_soon(bot_polling, bot_token, args.chat_id, attempts_queue)


if __name__ == "__main__":
    try:
        anyio.run(main)
    except KeyboardInterrupt:
        logging.info("Завершение работы")
