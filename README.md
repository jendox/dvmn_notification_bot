# 🤖 Devman Notification Bot

Бот для уведомлений о проверке заданий на [Devman](https://dvmn.org). Отправляет сообщения в Telegram, когда ментор проверил вашу работу.

## 📦 Установка

### Установите uv (если еще не установлен)
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Клонируйте репозиторий
```bash
git clone https://github.com/jendox/dvmn_notification_bot.git
cd dvmn_notification_bot
```

### Установите зависимости
```bash
uv sync
```

## ⚙️ Настройка

### Получите токены

#### Telegram Bot Token:

Напишите в Telegram [@BotFather](https://telegram.me/BotFather).

Создайте нового бота командой /newbot.

Сохраните полученный токен.

#### Devman API Token:

Зайдите на [dvmn](https://dvmn.org/api/docs/) (нужна авторизация).

В разделе "Аутентификация" скопируйте и сохраните персональный токен.

### Получите Chat ID

Чтобы получить свой chat_id, напишите в Telegram специальному боту: [@userinfobot](https://telegram.me/userinfobot).

### Настройте переменные окружения

Создайте файл .env в корне проекта:
```bash
touch .env
```

Добавьте в него переменные:
```env
BOT_TOKEN=your_telegram_bot_token_here
API_TOKEN=your_devman_api_token_here
CHAT_ID=your-chat_it
```

## 🚀 Управление

### Запуск

Запустите бота командой:

```bash
uv run python main.py
```

### Остановка

Для корректного завершения работы нажмите `Ctrl+C` в терминале.