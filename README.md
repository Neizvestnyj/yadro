# RandomUser API Application

Веб-приложение для работы с API randomuser.me с пагинацией и детальной информацией о
пользователях. [![Coverage Status](https://coveralls.io/repos/github/Neizvestnyj/yadro/badge.svg?branch=master)](https://coveralls.io/github/Neizvestnyj/yadro?branch=master)

> Note: Последняя [версия проекта до дедлайна 24.05.2025](https://github.com/Neizvestnyj/yadro/tree/2cd6567d2afaa1b5ba2f3414f5504aec8f3954fb) без Nginx, Prometheus, Grafana, Loki, Redis

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
make rebuild
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
make test
```

### Нагрузочное тестирование

Запросите дополнительно пользователей для теста (выполните 3 раза, должно быть > 10000 пользователей)

```shell
make fetch
```

Запуск тестов через веб-интерфейс

```shell
make load-test-ui
```

| Кол-во пользователей | Время | spawn-rate | Конфигурация | Количество запросов | Медианное время ответа (мс) | Среднее время ответа (мс) | Mix (ms) | Max (ms) | RPS   | % Ошибок |
|----------------------|-------|------------|--------------|---------------------|-----------------------------|---------------------------|----------|----------|-------|----------|
| 100                  | 3m    | 50         | Без Redis    | 33426               | 220                         | 231.98                    | 5        | 1436     | 186.4 | 1        |
| 200                  | 3m    | 50         | Без Redis    | 32260               | 770                         | 799.53                    | 6        | 3546     | 166.8 | 1        |
| 100                  | 3m    | 50         | С Redis      | 36701               | 160                         | 184.84                    | 4        | 1116     | 207   | 1        |
| 200                  | 3m    | 50         | С Redis      | 35704               | 280                         | 691.31                    | 5        | 6920     | 203.9 | 1        |

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
    - [K8s Node Metrics _ Multi Clusters.json](backend/monitoring/grafana/dashboards/K8s%20Node%20Metrics%20_%20Multi%20Clusters.json): [Grafana Labs - 22413](https://grafana.com/grafana/dashboards/22413-k8s-node-metrics-multi-clusters-node-exporter-prometheus-grafana11-2025-en/) - *только на Unix системах, на Windows часть метрик будет недоступна*
    - [Docker - cAdvisor Compute Resources.json](backend/monitoring/grafana/dashboards/Docker%20-%20cAdvisor%20Compute%20Resources.json): [Grafana Labs - 21361](https://grafana.com/grafana/dashboards/21361-docker-cadvisor-compute-resources/) - *только на Unix системах, на Windows часть метрик будет недоступна*
    - [NGINX-1748555632072.json](backend/monitoring/grafana/dashboards/NGINX.json): [GitHub - nginx-prometheus-exporter](https://github.com/nginx/nginx-prometheus-exporter/blob/main/grafana/dashboard.json)
    - [PostgreSQL.json](backend/monitoring/grafana/dashboards/PostgreSQL.json): [Grafana Labs - 9628](https://grafana.com/grafana/dashboards/9628-postgresql-database/)

- **Prometheus**: Собирает метрики FastAPI (`http://localhost:8000/metrics`).
- **Loki**: Собирает JSON-логи приложения.
- **Grafana**: Визуализирует метрики и логи (`http://localhost:3000`).

## ✨ Особенности

- Автоматическая загрузка 1000 пользователей при старте
- Кэширование данных на бекенде/клиенте
- Полная валидация запросов/ответов
- Адаптивный интерфейс
- Мониторинг метрик и логов в Grafana
