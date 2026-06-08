Проект: Распределённая система LLM-консультаций

Система состоит из двух независимых сервисов:
- Auth Service – управление пользователями и выдача JWT-токенов (FastAPI, SQLite, SQLAlchemy).
- Bot Service – Telegram-бот, который принимает сообщения, проверяет JWT, ставит задачи в очередь и возвращает ответы LLM (aiogram, Celery, RabbitMQ, Redis, OpenRouter).

Архитектура построена на принципе разделения ответственности: сервис авторизации ничего не знает о LLM и Telegram, а бот доверяет только валидным JWT.

# Cтруктура катологов

```
final_project_llm_consultation/
├── auth_service/                 # Сервис аутентификации
│   ├── app/
│   │   ├── core/                 # config, security, exceptions
│   │   ├── db/                   # models, session, base
│   │   ├── schemas/              # Pydantic схемы
│   │   ├── repositories/         # работа с БД (users)
│   │   ├── usecases/             # бизнес-логика (auth)
│   │   └── api/                  # эндпоинты, deps
│   ├── tests/                    # unit + интеграционные тесты
│   ├── main.py                    # Точка входа FastAPI
│   ├── .env.example
│   ├── pytest.ini
│   └── pyproject.toml
│
├── bot_service/                  # Сервис Telegram-бота
│   ├── app/
│   │   ├── core/                 # config, jwt (только валидация)
│   │   ├── infra/                # redis, celery_app
│   │   ├── services/             # openrouter_client
│   │   ├── tasks/                # Celery задачи (llm_request)
│   │   └── bot/                  # dispatcher, handlers
│   ├── tests/                    # unit, мок-тесты, интеграция (respx)
│   ├── main.py                    # Точка входа FastAPI
│   ├── run_bot.py                   #  Запуск бота
│   ├── .env.example
│   ├── pytest.ini
│   └── pyproject.toml
│
└── README.txt                     # Описание проекта и запуск
```

# Технологии

* Auth Service: FastAPI, SQLAlchemy 2.0 (async), SQLite/aiosqlite, Pydantic, python-jose, bcrypt
* Bot Service: aiogram 3, Celery, RabbitMQ, Redis, OpenRouter API, httpx (синхронный)
* Общие инструменты: uv (менеджер зависимостей), pytest, fakeredis, respx, pytest-mock
* Инфраструктура: RabbitMQ (брокер), Redis (бэкенд/кэш)

# Установка и запуск

Предварительные требования:
- Python 3.11+ (рекомендуется 3.13)
- Установленный uv (https://docs.astral.sh/uv/)
- Локально или через Docker: RabbitMQ (порт 5672), Redis (порт 6379)

1. Клонирование репозитория
   git clone <url-репозитория>
   cd final_project_llm_consultation

2. Настройка переменных окружения
   Скопируйте примеры .env в каждом сервисе:
     cp auth_service/.env.example auth_service/.env
     cp bot_service/.env.example bot_service/.env
   Отредактируйте их, указав реальные значения.

   Минимально необходимые переменные:
   Auth Service .env:
     JWT_SECRET=ваш-секретный-ключ-минимум-32-символа
     JWT_ALG=HS256
     ACCESS_TOKEN_EXPIRE_MINUTES=30
     SQLITE_PATH=./auth_db.sqlite

   Bot Service .env:
     BOT_TOKEN=токен_от_BotFather
     JWT_SECRET=точно_такой_же_как_в_Auth_Service
     JWT_ALG=HS256
     OPENROUTER_API_KEY=sk-or-v1-...
     RABBITMQ_URL=amqp://guest:guest@localhost:5672/
     REDIS_URL=redis://localhost:6379/0
     
     Создайте своего бота через @BotFather, получите токен и поместите его в BOT_TOKEN в .env.

3. Установка зависимостей
   cd auth_service
   uv sync
   cd ../bot_service
   uv sync

4. Запуск инфраструктуры (RabbitMQ + Redis)
   Вариант А: через Docker
     docker run -d --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:3.13-management
     docker run -d --name redis -p 6379:6379 redis

   Вариант Б: локально без Docker (macOS/Linux)
     brew install rabbitmq && brew services start rabbitmq
     brew install redis && brew services start redis

5. Запуск Auth Service
   cd auth_service
   uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 
   Сервер будет доступен по адресу: http://localhost:8000

6. Запуск Bot Service (три компонента)

   6.1. Celery worker:
        cd bot_service
        uv run celery -A app.infra.celery_app worker --loglevel=info --without-mingle --without-gossip --without-heartbeat --pool=solo

   6.2. Telegram-бот:
        uv run python run_bot.py 

   6.3. (Опционально) FastAPI healthcheck:
        uv run uvicorn app.main:app --port 8001

# Пользовательский сценарий

1. Регистрация в Auth Service через Swagger (POST /auth/register).
2. Логин (POST /auth/login) – получаем access_token.
3. В Telegram-боте  выполнить команду /token <ваш_токен>.
4. Отправить боту любое текстовое сообщение – оно уйдёт в очередь RabbitMQ, Celery-воркер обратится к OpenRouter, результат вернётся пользователю.

# Тестирование

## Auth Service:
  cd auth_service
  uv run pytest -v
  - Модульные тесты: tests/test_security.py
  - Интеграционные тесты API: tests/test_api.py (с in-memory SQLite)

## Bot Service:
  cd bot_service
  uv run pytest -v
  - Модульные тесты: tests/test_jwt.py
  - Мок-тесты хендлеров: tests/test_handlers.py (fakeredis + мок Celery)
  - Интеграционные тесты клиента OpenRouter: tests/test_openrouter_client.py (respx)

Тесты не требуют запущенных RabbitMQ, Redis или доступа к реальному OpenRouter.

# Скриншоты

## Регистрация
![Регистрация](screens/register.png)

## Логин и получение JWT
![Логин и получение JWT](screens/login.png)

## Аутентификация через Swagger
![Результат аутентификации](screens/OAuth2.png)

## Получение токена текущего пользователя
![Результат текущий пользователь](screens/get_me.png)

## Проверка подключения
![Результат проверки подключения](screens/health.png)

## Telegram bot
![Результат работы Telegram-бота](screens/telegram.png)

## RabbitMQ
![Результат работы RabbitMQ](screens/RabbitMQ.png)

## Тестирование auth_service
![Результат тестирования auth_service](screens/test_auth_service.png)

## Тестирование bot_service
![Результат тестирования auth_service](screens/test_bot_service.png)



# Примечания

- JWT-секрет (JWT_SECRET) обязан совпадать в Auth Service и Bot Service, иначе бот не сможет проверить токен.
- Для бесплатного доступа к OpenRouter установите OPENROUTER_DEFAULT_MODEL=openrouter/free.
- Если при запуске Celery возникают ошибки transient_nonexcl_queues, используйте флаги --without-mingle --without-gossip --without-heartbeat или RabbitMQ версии 3.13.
- Обязательно добавьте .env в .gitignore, чтобы не закоммитить секреты.

