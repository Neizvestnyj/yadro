# RandomUser API Application
[![Coverage Status](https://coveralls.io/repos/github/your-username/your-repo-name/badge.svg?branch=master)](https://coveralls.io/github/your-username/your-repo-name?branch=master)
Backend-часть приложения для работы с API randomuser.me

## Технологический стек

- **FastAPI** - современный асинхронный фреймворк для Python
- **PostgreSQL** - реляционная СУБД для хранения данных пользователей
- **SQLAlchemy** + **asyncpg** - асинхронный доступ к базе данных
- **Locust** - нагрузочное тестирование (опционально)
- **Docker** - контейнеризация приложения

## Запуск приложения

### Вариант 1: Локальный запуск

1. Установите зависимости:

```bash
poetry install --with dev
```

2. Создайте и настройте БД PostgreSQL:

```bash
createdb randomuser_db
```

3. Запустите приложение:

```bash
uvicorn app.main:app --reload
```

### Вариант 2: Запуск через Docker

1. Соберите и запустите контейнеры:

```bash
docker-compose up -d --build
```

2. Приложение будет доступно по адресу: `http://localhost:8000`

## API Endpoints

- `GET /` - Главная страница с формой
- `GET /users` - Список пользователей (пагинация)
- `POST /users/fetch` - Загрузка новых пользователей
- `GET /users/{user_id}` - Информация о конкретном пользователе
- `GET /users/random` - Случайный пользователь

## Тестирование

Запуск тестов:

```bash
pytest tests
```

Тесты включают:

- Интеграционные тесты API
- Моки внешних API

## Особенности реализации

1. **Асинхронная загрузка** данных из внешнего API
2. **Пагинация** для работы с большими объемами данных
3. **Автоматическая загрузка** 1000 пользователей при старте
4. **Оптимизированные запросы** к БД
5. **Валидация** всех входящих данных

## Документация API

После запуска доступны:

- Swagger UI: `http://localhost:8000/docs`
