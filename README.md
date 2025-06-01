# RandomUser API Application

Веб-приложение для работы с API randomuser.me с пагинацией и детальной информацией о
пользователях. [![Coverage Status](https://coveralls.io/repos/github/Neizvestnyj/yadro/badge.svg?branch=master)](https://coveralls.io/github/Neizvestnyj/yadro?branch=master)

## 📑 Содержание

- [🛠 Технологический стек](#-технологический-стек)
- [⚙️ Требования](#-требования)
- [🚀 Запуск приложения](#-запуск-приложения)
  - [💻 Локальный запуск](#-локальный-запуск)
  - [🐳 Docker-запуск](#-docker-запуск)
- [📡 API Endpoints](#-api-endpoints)
- [🧪 Тестирование](#-тестирование)
  - [Интеграционные тесты](#интеграционные-тесты)
  - [Нагрузочное тестирование](#нагрузочное-тестирование)
  - [Проверка доступности контейнеров с метриками](#проверка-доступности-контейнеров-с-метриками)
- [📊 Мониторинг с Grafana Dashboard](#-мониторинг-с-grafana-dashboard)
- [✨ Особенности](#-особенности)

## 🛠 Технологический стек

| Компонент       | Технологии                | Обоснование выбора                                                     |
|-----------------|---------------------------|------------------------------------------------------------------------|
| Бэкенд          | FastAPI                   | Асинхронность, встроенная документация OpenAPI                         |
| База данных     | PostgreSQL                | Надежность, поддержка сложных запросов                                 |
| ORM             | SQLAlchemy + asyncpg      | Асинхронный доступ к БД                                                |
| Кэш             | Redis                     | Быстрый доступ к данным, поддержка pub/sub                             |
| Фронтенд        | React                     | Компонентный подход, быстрый рендеринг                                 |
| Веб-сервер	     | Nginx                     | Высокая производительность, статическая отдача, проксирование запросов |
| Мониторинг      | Prometheus, Grafana, Loki | Комплексный мониторинг метрик и логов                                  |
| Контейнеризация | Docker                    | Упрощение развертывания                                                |
| Тестирование    | Pytest                    | Поддержка моков и асинхронных тестов                                   |

## ⚙️ Требования

- Python 3.11+
- PostgreSQL 17+
- Node.js 18+
- Docker

## 🚀 Запуск приложения

### 💻 Локальный запуск

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
   ```psql
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

6. Запустите REdis
   ```shell
   docker run --rm -d --name redis_test -p 6379:6379 redis:7 redis-server --save "" --appendonly no
   ```

7. Запустите серверы:
   ```shell
   # Бэкенд
   uvicorn app.main:app --reload
   
   # Фронтенд (в новом терминале)
   npm start
   ```

После запуска:

- Фронтенд: [http://localhost:3001](http://localhost:3001)
- API документация: [http://localhost:3001/docs](http://localhost:3001/docs)

### 🐳 Docker-запуск

```shell
docker plugin install grafana/loki-docker-driver:latest --alias loki --grant-all-permissions
docker-compose up -d --build
```

После запуска:

- Фронтенд: [http://localhost](http://localhost)
- API документация: [http://localhost/docs](http://localhost/docs)

## 📡 API Endpoints

| Метод  | Путь                           | Описание                                   |
|--------|--------------------------------|--------------------------------------------|
| GET    | api/v1/users?limit=10&offset=0 | Список пользователей с пагинацией          |
| POST   | api/v1/users/fetch?count=100   | Загрузка пользователей из API              |
| GET    | api/v1/users/{user_id}         | Детали конкретного пользователя            |
| PUT    | api/v1/users/{user_id}         | Обновление данных конкретного пользователя |
| DELETE | api/v1/users/{user_id}         | Удаление конкретного пользователя          |
| GET    | api/v1/users/random            | Случайный пользователь                     |

## 🧪 Тестирование

### Интеграционные тесты

```shell
pytest tests/ -v
```

### Нагрузочное тестирование

Запросите дополнительно пользователей для теста (выполните 3 раза, должно быть > 10000 пользователей)

```shell
curl -X POST "http://localhost/v1/users/fetch?count=5000"
```

```shell
locust -f tests/load/locustfile.py --host=http://localhost --users 100 --spawn-rate 10 --headless --run-time 3m --csv=results
```

или с веб-интерфейсом

```shell
locust -f tests/load/locustfile.py --host=http://localhost --web-host=localhost
```

| Конфигурация | RPS   | Медианное время ответа (мс) | Количество запросов | Среднее время ответа (мс) |
|--------------|-------|-----------------------------|---------------------|---------------------------|
| Без Redis    | 198.3 | 210                         | 32413               | 235.79                    |
| С Redis      | 217.5 | 180                         | 34009               | 211.31                    |

### Проверка доступности контейнеров с метриками

```shell
# ready
curl http://localhost:3100/ready

curl http://localhost:9090/targets

curl http://localhost:8000/metrics
```

## 📊 Мониторинг с Grafana Dashboard

1. Откройте Grafana: [http://localhost:3000](http://localhost:3000)
    - Логин: `admin`
    - Пароль: `admin`

2. Импортируйте дашборды:
   Dashboards → New → Import → Upload JSON
    - [Backend-dashboard.json](backend/monitoring/grafana/dashboards/Backend-dashboard.json): [Grafana Labs - 16110](https://grafana.com/grafana/dashboards/16110-fastapi-observability/)
    - [Redis-dashboard.json](backend/monitoring/grafana/dashboards/Redis-dashboard.json): [Grafana Labs - 763](https://grafana.com/grafana/dashboards/763-redis-dashboard-for-prometheus-redis-exporter-1-x/)
    - [Docker_Container_and_Host_Metrics.json](backend/monitoring/grafana/dashboards/Docker_Container_and_Host_Metrics.json): [Grafana Labs - 10619](https://grafana.com/grafana/dashboards/10619-docker-host-container-overview/) -
      *только на Unix системах, на Windows часть метрик будет недоступна*
    - [NGINX-1748555632072.json](backend/monitoring/grafana/dashboards/NGINX.json): [GitHub - nginx-prometheus-exporter](https://github.com/nginx/nginx-prometheus-exporter/blob/main/grafana/dashboard.json)

- **Prometheus**: Собирает метрики FastAPI (`http://localhost:8000/metrics`).
- **Loki**: Собирает JSON-логи приложения.
- **Grafana**: Визуализирует метрики и логи (`http://localhost:3000`).

## ✨ Особенности

- Автоматическая загрузка 1000 пользователей при старте
- Кэширование данных на бекенде/клиенте
- Полная валидация запросов/ответов
- Адаптивный интерфейс
- Мониторинг метрик и логов в Grafana
