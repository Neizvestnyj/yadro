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
- Node.js 18+
- Docker

## 🚀 Запуск приложения

### Локальный запуск

1. Клонируйте репозиторий:
   ```shell
   git clone https://github.com/Neizvestnyj/yadro.git
   cd yadro
   ```

2. Установите зависимости [backend](backend)/[frontend](frontend):
   ```shell
   # Бэкенд
   pip install poetry
   poetry install --with dev
   
   # Фронтенд
   npm install
   ```

3. Настройте БД:
   ```shell
   createdb randomuser_db
   ```

4. Создайте `.env` файл *(не обязательно)*:
   ```env
   DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/randomuser_db
   ```

5. Примените миграции:
   ```shell
   alembic upgrade head
   ```

6. Запустите серверы:
   ```shell
   # Бэкенд
   uvicorn app.main:app --reload
   
   # Фронтенд (в новом терминале)
   npm start
   ```

Приложение будет доступно по адресу: [http://localhost:3001](http://localhost:3001)

### Docker-запуск

```shell
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

### Интеграционные тесты

```shell
pytest tests/ -v
```

### Нагрузочное тестирование

Запросите дополнительно пользователей для теста (выполните 3 раза, должно быть > 10000 пользователей)

```shell
curl -X POST "http://localhost:8000/v1/users/fetch?count=5000"
```

```shell
locust -f tests/locustfile.py --host=http://localhost:8000 --users 1000 --spawn-rate 50 --headless --run-time 3m --csv=results
```

или с веб-интерфейсом

```shell
locust -f tests/locustfile.py --host=http://localhost:8000 --web-host=localhost
```

| Конфигурация | RPS   | Медианное время ответа (мс) | Количество запросов | Среднее время ответа (мс) |
|--------------|-------|-----------------------------|---------------------|---------------------------|
| Без Redis    | 211.4 | 3900                        | 38616               | 4269.85                   |
| С Redis      | 188.5 | 4400                        | 33420               | 4924.32                   |

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

2. Импортируйте дашборды:
   Dashboards → New → Import → Upload JSON
   файла [Backend-dashboard.json](backend/monitoring/grafana/Backend-dashboard.json) - [Grafana Labs - 16110](https://grafana.com/grafana/dashboards/16110-fastapi-observability/), [Redis-dashboard.json](backend/monitoring/grafana/Redis-dashboard.json) - [Grafana Labs - 763](https://grafana.com/grafana/dashboards/763-redis-dashboard-for-prometheus-redis-exporter-1-x/)

- **Prometheus**: Собирает метрики FastAPI (`http://localhost:8000/metrics`).
- **Loki**: Собирает JSON-логи приложения.
- **Grafana**: Визуализирует метрики и логи (`http://localhost:3000`).

## ✨ Особенности

- Автоматическая загрузка 1000 пользователей при старте
- Кэширование данных на бекенде/клиенте
- Полная валидация запросов/ответов
- Адаптивный интерфейс
- Мониторинг метрик и логов в Grafana
