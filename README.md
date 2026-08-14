# Movie Rating Service

Movie Rating Service — это учебный REST API для фильмов, режиссеров, пользователей и отзывов.

Я писал этот проект как портфолио backend-приложение на FastAPI. Основная цель была не просто сделать CRUD, а попробовать собрать более приближенный к реальному проект: с авторизацией, ролями, миграциями, кэшированием, тестами, обработкой ошибок и разделением кода по слоям.

## Что умеет проект

В API сейчас есть такие возможности:

- регистрация и авторизация пользователей;
- access и refresh токены;
- logout с удалением refresh token из Redis;
- роли и permissions для ограничения доступа;
- создание, редактирование, удаление и поиск фильмов;
- создание, редактирование, удаление и поиск режиссеров;
- создание отзывов к фильмам;
- получение отзывов по фильму и по пользователю;
- обновление среднего рейтинга фильма после изменения отзывов;
- списки жанров и стран;
- пагинация и сортировка в списочных эндпоинтах;
- единый формат ответов и ошибок;
- rate limiting через Redis;
- кэширование некоторых GET-запросов;
- автодокументация через OpenAPI.

## Стек

Основное:

- Python 3.11+
- FastAPI
- SQLAlchemy async
- PostgreSQL
- Alembic
- Redis
- Pydantic v2
- PyJWT
- bcrypt
- Poetry
- Docker / Docker Compose

Для тестов и качества кода:

- pytest
- pytest-asyncio
- httpx
- testcontainers
- ruff

## Архитектура проекта

Проект разделен на несколько основных частей:

```text
app/
├── api/              # роутеры и зависимости FastAPI
├── cache/            # декораторы для кэша
├── core/             # настройки, безопасность, ошибки, логирование
├── database/         # модели, сессии, репозитории, Unit of Work
├── schemas/          # Pydantic-схемы
├── services/         # бизнес-логика и ошибки
├── main.py           # создание FastAPI-приложения
└── redis.py          # подключение к Redis
```

Я старался не держать всю логику в роутерах. Роутеры в основном принимают запрос, вызывают сервис и возвращают ответ. Основная логика находится в `services`, а работа с базой вынесена в `repositories`.

Для работы с транзакциями используется Unit of Work. Он создает сессию, репозитории и делает commit или rollback в зависимости от результата операции.

## Основные сущности

В базе есть такие сущности:

- `users` — пользователи;
- `roles` и `permissions` — роли и права;
- `movies` — фильмы;
- `directors` — режиссеры;
- `reviews` — отзывы пользователей на фильмы;
- `genres` — жанры;
- `countries` — страны;
- связующие таблицы для many-to-many связей.

У фильма может быть несколько жанров и стран. У пользователя может быть несколько ролей. У роли может быть несколько permissions.

## Авторизация и права

В проекте используется JWT-аутентификация:

- access token нужен для доступа к защищенным эндпоинтам;
- refresh token хранится в Redis и используется для обновления пары токенов;
- при logout refresh token удаляется из Redis.

Права проверяются через permissions. Например, для создания фильма нужно право `movies:create`, для удаления фильма — `movies:delete`.

Обычный пользователь получает роль `user`. Для админских действий нужна роль `admin`. Сейчас создание администратора не вынесено в отдельный публичный эндпоинт, возможно позже я добавлю отдельный роутер для администрирования проекта.

## Кэш и rate limiting

Redis используется в двух местах:

1. Для хранения refresh tokens.
2. Для кэширования и ограничения количества запросов.

Кэшируются данные, которые часто читаются и редко меняются, например карточка фильма, карточка режиссера, списки жанров и стран.

После изменения фильма, режиссера или отзыва соответствующий кэш инвалидируется. Например, если пользователь поменял рейтинг в отзыве, рейтинг фильма пересчитывается, а кэш фильма удаляется.

Rate limiting сделан отдельно для IP и для авторизованных пользователей. Для админов лимит выше, чем для обычных пользователей.

## Запуск через Docker Compose

Самый простой способ запустить проект — через Docker Compose.

Сначала нужно создать `.env` файл:

```bash
cp .env.example .env
```

После этого можно запустить проект:

```bash
docker compose up --build
```

При запуске контейнер `web` применит миграции Alembic и поднимет API на порту `8000`.

Если в `.env` включен `SHOW_DOCS=True`, документация будет доступна по адресам:

```text
http://localhost:8000/docs
http://localhost:8000/redoc
```

## Локальный запуск без Docker для приложения

Если PostgreSQL и Redis уже запущены локально, можно запустить проект без контейнера приложения.

Установить зависимости:

```bash
poetry install
```

Создать `.env`:

```bash
cp .env.example .env
```

Применить миграции:

```bash
poetry run alembic upgrade head
```

Запустить приложение:

```bash
poetry run uvicorn app.main:app --reload
```

## Переменные окружения

Пример переменных есть в `.env.example`.

Основные переменные:

```env
DATABASE_URL=postgresql+asyncpg://postgres:postgres_password@localhost:5432/movie_rating_service_dev
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=your_secret_key
ALGORITHM=HS256
MODE=DEV
SHOW_DOCS=True
DEBUG=True
LOG_LEVEL=INFO
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7
```

Для разработки можно оставить значения из примера, но для реального окружения `SECRET_KEY` нужно заменить.

## Миграции

Проект использует Alembic.

Применить миграции:

```bash
poetry run alembic upgrade head
```

Откатить все миграции:

```bash
poetry run alembic downgrade base
```

В миграциях также добавляются начальные данные: countries, genres, roles и permissions.

## Тесты

Тесты написаны на pytest и pytest-asyncio. Для PostgreSQL и Redis используются testcontainers, поэтому для запуска тестов должен быть доступен Docker.

Запуск тестов:

```bash
poetry run pytest
```

Проверка линтером:

```bash
poetry run ruff check .
```

## Примеры эндпоинтов

Базовый префикс API:

```text
/api/v1
```

Авторизация:

```text
POST /api/v1/auth/register
POST /api/v1/auth/login
POST /api/v1/auth/refresh
POST /api/v1/auth/logout
```

Пользователи:

```text
GET    /api/v1/users/me
PATCH  /api/v1/users/me
DELETE /api/v1/users/me
GET    /api/v1/users/{user_id}
```

Фильмы:

```text
GET    /api/v1/movies
POST   /api/v1/movies
GET    /api/v1/movies/{movie_id}
PATCH  /api/v1/movies/{movie_id}
DELETE /api/v1/movies/{movie_id}
GET    /api/v1/movies/genres
GET    /api/v1/movies/countries
```

Режиссеры:

```text
GET    /api/v1/directors
POST   /api/v1/directors
GET    /api/v1/directors/{director_id}
PATCH  /api/v1/directors/{director_id}
DELETE /api/v1/directors/{director_id}
```

Отзывы:

```text
GET    /api/v1/reviews/movies/{movie_id}
GET    /api/v1/reviews/users/{user_id}
POST   /api/v1/reviews/{movie_id}
PATCH  /api/v1/reviews/{review_id}
DELETE /api/v1/reviews/{review_id}
```

## Что я хотел показать этим проектом

Этим проектом я хотел продемонстрировать свои навыки и показать, что понимаю не только базовый CRUD, но и другие вещи, которые часто встречаются в backend-разработке:

- работу с асинхронным FastAPI;
- разделение приложения на слои;
- работу с PostgreSQL через SQLAlchemy;
- миграции через Alembic;
- JWT-аутентификацию;
- refresh tokens через Redis;
- роли и permissions;
- централизованную обработку ошибок;
- кэширование и инвалидацию кэша;
- rate limiting;
- интеграционные тесты с отдельными контейнерами базы и Redis.

Проект учебный и находится в активной разработке. Архитектура, функциональность и документация продолжают улучшаться.
