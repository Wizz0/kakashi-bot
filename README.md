# Kakashi Bot

Бот для отслеживания очереди на уборку кошачьего лотка. Напоминает, кто должен убрать, начисляет штрафы за неуборку, генерирует очередь на неделю с учетом штрафов.

## Features

- **Ежедневные напоминания** - каждый вечере отправляет в группу сообщение, чья сегодня очередь убирать лоток
- **Отметка об уборке** - кнопка "Убрал" прямо в сообщении, нажать может любой участник группы
- **Штрафы** - если не убрал, +1 дополнительный день уборки на следующей неделе
- **Расписание** - каждую неделю генерируется очередь с учетом штрафов
- **Личные команды** - `/my_queue` и `/my_penalties` в личке бота

## Как работают штрафы

- 1 штраф = 1 дополнительный день уборки
- 2 штрафа = 2 дополнительных дня уборки
- 3+ штрафа = вся неделя уборки
- после отработки, штрафы обнуляются

## Команды

| Команда | Где | Описание |
|---------|-----|----------|
| `/start` | Личка/Группа | Информация о боте |
| `/my_queue` | Личка | Мои дни уборки на неделе |
| `/my_penalties` | Личка | Мои штрафы |
| `/today_queue` | Группа | Чья очередь сегодня |
| `/week_queue` | Группа | Недельное расписание |

## API

Есть API на FastAPI для "админки". Swagger доступен по `/docs`

| Метод | Путь | Описание |
|-------|------|----------|
| GET | `/api/users` | Список пользователей |
| POST | `/api/users` | Добавить пользователя |
| PUT | `/api/users/{id}` | Изменить пользователя |
| DELETE | `/api/users/{id}` | Удалить пользователя |
| GET | `/api/queue/today` | Кто убирает сегодня |
| GET | `/api/queue/week` | Расписание на неделю |
| POST | `/api/queue/add` | Добавить запись в очередь |
| POST | `/api/queue/{id}/clean` | Отметить уборку |
| POST | `/api/users/{id}/penalty` | Добавить штраф |

## Установка

### Требования

- Docker и Docker Compose
- Telegram бот (создать через [@BotFather](https://t.me/BotFather))

### Настройка

1. Клонирование репозитория:
```bash
git clone github.com/Wizz0/kakashi-bot
cd kakashi-bot
```

2. Создание .env
```bash
cp .env.example .env
```

Содержимое файла:
```
BOT_TOKEN=Токен с BotFather
GROUP_CHAT_ID=ID группы
API_PORT=8000
TIMEZONE=Asia/Yakutsk (часовой пояс)

# Во сколько отправлять напоминания (в 20:00)
REMINDER_HOUR=20
REMINDER_MINUTE=0

# Во сколько проверять убрано или нет для начисления штрафа (в 23:59)
CHECK_HOUR=23
CHECK_MINUTE=59

# Когда гененировать новую очередь (в 0:00 понедельник)
SCHEDULE_DAY=monday
```

3. Запуск контейнеров:
```bash
docker compose up -d --build
```

4. Настройка бота:
- В BotFather: /mybots → Bot Settings → Group Privacy → Disabled
- Добавить бота в группу
- Назначить админом

5. Добавить пользователей
- перейти в `/docs`
- добавить пользователя через `Create User`, в `name` вписать Telegram-тег пользователя
<img width="1442" height="645" alt="image" src="https://github.com/user-attachments/assets/ca0d5bda-acab-428e-a0ae-46a64439fd2f" />
- при необходимости составить очередь через `Add Queue Entry`

## Структура проекта
```
kakashi-bot/
├── app/
│   ├── api/
│   │   └── routes.py
│   ├── bot/
│   │   ├── handlers.py
│   │   ├── keyboards.py
│   │   └── scheduler.py
│   ├── config.py
│   ├── crud.py
│   ├── database.py
│   ├── main.py
│   ├── models.py
│   └── schemas.py
├── data/              # SQLite БД
├── .env
├── docker-compose.yml
├── Dockerfile
└── requirements.txt
```

## TODO
- [ ] Админские команды
- [ ] Напоминания в личку
- [ ] Напоминания каждый час, пока пользователь не отметится

## Заказчик проекта
(серьезный дядя)
<img width="1280" height="964" alt="photo_2026-07-13_13-21-35" src="https://github.com/user-attachments/assets/fcd56735-88b8-4ffa-9344-431b9eab9f59" />
