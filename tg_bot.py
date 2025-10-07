import asyncio
from textwrap import dedent

import telegram

from devman import Attempt


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


async def bot_polling(
    token: str,
    chat_id: str,
    queue: asyncio.Queue
) -> None:
    bot = telegram.Bot(token)
    while True:
        try:
            attempt: Attempt = await queue.get()
            await bot.send_message(
                chat_id=chat_id,
                text=format_review_message_html(attempt),
                parse_mode="HTML",
                disable_web_page_preview=True,
            )
        except asyncio.QueueShutDown:
            break
