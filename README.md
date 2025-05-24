# RandomUser API Application

Веб-приложение для работы с API randomuser.me с пагинацией и детальной информацией о
пользователях. [![Coverage Status](https://coveralls.io/repos/github/Neizvestnyj/yadro/badge.svg?branch=master)](https://coveralls.io/github/Neizvestnyj/yadro?branch=master)

## 🛠 Технологический стек

| Компонент       | Технологии                | Обоснование выбора                             |
|-----------------|---------------------------|------------------------------------------------|
| Бэкенд          | FastAPI                   | Асинхронность, встроенная документация OpenAPI |
| База данных     | PostgreSQL                | Надежность, поддержка сложных запросов         |
| ORM             | SQLAlchemy + asyncpg      | Асинхронный доступ к БД                        |
| Фронтенд        | React                     | Компонентный подход, быстрый рендеринг         |
| Мониторинг      | Prometheus, Grafana, Loki | Комплексный мониторинг метрик и логов          |
| Контейнеризация | Docker                    | Упрощение развертывания                        |
| Тестирование    | Pytest                    | Поддержка моков и асинхронных тестов           |

## ⚙️ Требования

- Python 3.11+
- PostgreSQL 16+
- Node.js 16+
- Docker

## 🚀 Запуск приложения

### Локальный запуск

1. Клонируйте репозиторий:
   ```bash
   git clone https://github.com/Neizvestnyj/yadro.git
   cd yadro
   ```

2. Установите зависимости:
   ```bash
   # Бэкенд
   poetry install --with dev
   
   # Фронтенд
   npm install
   ```

3. Настройте БД:
   ```bash
   createdb randomuser_db
   ```

4. Создайте `.env` файл:
   ```env
   DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/randomuser_db
   ```

5. Примените миграции:
   ```bash
   alembic upgrade head
   ```

6. Запустите серверы:
   ```bash
   # Бэкенд
   uvicorn app.main:app --reload
   
   # Фронтенд (в новом терминале)
   npm start
   ```

Приложение будет доступно по адресу: [http://localhost:3001](http://localhost:3001)

### Docker-запуск

```bash
docker plugin install grafana/loki-docker-driver:latest --alias loki --grant-all-permissions
docker-compose up -d --build
```

После запуска:

- Фронтенд: [http://localhost:3001](http://localhost:3001)
- API документация: [http://localhost:8000/docs](http://localhost:8000/docs)

## 📡 API Endpoints

| Метод | Путь                     | Описание                          |
|-------|--------------------------|-----------------------------------|
| GET   | /users?limit=10&offset=0 | Список пользователей с пагинацией |
| POST  | /users/fetch?count=100   | Загрузка пользователей из API     |
| GET   | /users/{user_id}         | Детали конкретного пользователя   |
| GET   | /users/random            | Случайный пользователь            |

## 🧪 Тестирование

```bash
pytest tests/ -v
```

Тесты включают:

- Модульные тесты сервисов
- Интеграционные тесты API
- Моки внешнего API

### Проверка доступности контейнеров с метриками
```shell
# ready
curl http://localhost:3100/ready

curl http://localhost:9090/targets

curl http://localhost:8000/metrics
```

## 🔍 Документация

- Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)

## 📊 Мониторинг с Grafana Dashboard

1. Откройте Grafana: [http://localhost:3000](http://localhost:3000)
   - Логин: `admin`
   - Пароль: `admin`

2. Импортируйте дашборд:
   Dashboards → New → Import → Upload JSON файла [Backend-dashboard.json](backend/monitoring/grafana/Backend-dashboard.json)

- **Prometheus**: Собирает метрики FastAPI (`http://localhost:8000/metrics`).
- **Loki**: Собирает JSON-логи приложения.
- **Grafana**: Визуализирует метрики и логи (`http://localhost:3000`).

## ✨ Особенности

- Автоматическая загрузка 1000 пользователей при старте
- Клиентское кэширование данных
- Полная валидация запросов/ответов
- Оптимизированные SQL-запросы
- Адаптивный интерфейс
