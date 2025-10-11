import html
import logging
import queue
from textwrap import dedent

import anyio
import telegram
from anyio.abc import ObjectReceiveStream
from telegram.constants import ParseMode

from devman import Attempt

BOT_LOGGER_NAME = "bot"
QUEUE_SLEEP_TIME = 1.5


def format_review_message_html(attempt: Attempt) -> str:
    if attempt.is_negative:
        main_text = "Есть что улучшить 🔧"
        icon = "📋"
    else:
        main_text = "Всё отлично! ✨"
        icon = "🌟"

    return dedent(
        f"""\
        {icon} <b>Проверка завершена!</b>

        <b>Тема:</b> {attempt.lesson_title}
        <b>Результат:</b> {main_text}

        📎 <a href="{attempt.lesson_url}">Открыть урок</a>
        """
    )


def format_logger_message_html(record: logging.LogRecord) -> str:
    level_icon = {
        "CRITICAL": "🚨",
        "ERROR": "❌",
        "WARNING": "⚠️",
        "INFO": "ℹ️",
        "DEBUG": "🐞",
    }.get(record.levelname, "❗")

    message = html.escape(record.getMessage())
    logger_name = html.escape(record.name)
    exc_info = ""

    if record.exc_info:
        import traceback
        tb = "".join(traceback.format_exception(*record.exc_info))
        exc_info = f"\n\n<pre>{html.escape(tb[-1500:])}</pre>"

    return dedent(
        f"""\
        {level_icon} <b>Логгер</b>
        
        <b>Уровень:</b> {record.levelname}
        <b>Источник:</b> {logger_name}
    
        <b>Сообщение:</b> {message}{exc_info}
        """
    )


class TelegramBot:
    def __init__(self, token: str, chat_id: str):
        self._bot = telegram.Bot(token)
        self._chat_id = chat_id
        self.logger = logging.getLogger(BOT_LOGGER_NAME)

    async def _send_html_message(
        self,
        message: str,
    ) -> None:
        await self._bot.send_message(
            chat_id=self._chat_id,
            text=message,
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True,
        )

    async def logs_polling(
        self,
        logs_queue: queue.Queue[logging.LogRecord],
    ) -> None:
        while True:
            try:
                record = logs_queue.get(block=False)
                message = format_logger_message_html(record)
                await self._send_html_message(message)
            except queue.Empty:
                await anyio.sleep(QUEUE_SLEEP_TIME)

    async def attempts_polling(
        self,
        stream: ObjectReceiveStream[Attempt],
    ) -> None:
        try:
            async for attempt in stream:
                message = format_review_message_html(attempt)
                await self._send_html_message(message)
        except anyio.EndOfStream:
            return
