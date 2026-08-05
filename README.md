# Movie Rating Service

REST API для управления фильмами, режиссерами, пользователями и отзывами.

Проект написан на **FastAPI** и служит учебным проектом для изучения построения backend-приложений с использованием современной архитектуры.

## Возможности

- Управление фильмами
- Управление режиссерами
- Регистрация пользователей
- Создание и просмотр отзывов
- Валидация данных
- Централизованная обработка ошибок
- Автоматическая документация OpenAPI

## Технологии

- Python 3.13
- FastAPI
- SQLAlchemy (Async)
- PostgreSQL
- Alembic
- Pydantic
- pytest
- Poetry

## Запуск

```bash
git clone https://github.com/breeze-git/movie-rating-service.git

cd movie-rating-service

poetry install

poetry run alembic upgrade head

poetry run uvicorn app.main:app --reload
```

После запуска документация будет доступна по адресам:

- `/docs`
- `/redoc`

## Статус проекта

🚧 Проект находится в активной разработке. Архитектура, функциональность и документация продолжают улучшаться.
