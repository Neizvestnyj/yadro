# Makefile для управления проектом url-alias-service
#
# Команды:
#   make build         Собрать Docker-образы
#   make up            Запустить контейнеры в фоновом режиме
#   make down          Остановить и удалить контейнеры
#   make rebuild       Пересобрать образы и запустить контейнеры
#   make logs          Показать логи контейнеров
#   make test          Запустить тесты
#   make lint          Запустить линтер (ruff)
#   make format        Форматировать код (ruff)
#   make migrate       Выполнить миграции базы данных
#   make fetch         Получить пользователей через API (count=5000)
#   make load-test-ui  Запустить нагрузочное тестирование с веб-интерфейсом

COMPOSE := docker compose

.PHONY: all build up down rebuild logs test lint format migrate fetch

# Сборка Docker-образов
build:
	@echo "Building Docker images..."
	$(COMPOSE) -f docker-compose.yml build

# Запуск контейнеров
up:
	@echo "Starting containers..."
	$(COMPOSE) -f docker-compose.yml up -d

# Пересборка и запуск контейнеров
rebuild:
	@echo "Rebuilding and starting containers..."
	$(COMPOSE) -f docker-compose.yml up -d --build

# Остановка и удаление контейнеров
down:
	@echo "Stopping and removing containers..."
	$(COMPOSE) -f docker-compose.yml down

# Показ логов
logs:
	@echo "Showing container logs..."
	$(COMPOSE) -f docker-compose.yml logs -f

# Запуск тестов
test:
	@echo "Running tests..."
	@(cd backend && poetry run pytest tests -v --cov=app --cov-report=html)

# Запуск линтера
lint:
	@echo "Running linter..."
	poetry run ruff check app tests

# Форматирование кода
format:
	@echo "Formatting code..."
	@(cd backend && poetry run ruff format app tests)

# Выполнение миграций базы данных
migrate:
	@echo "Running database migrations..."
	@(cd backend && poetry run alembic upgrade head)

# Запрос пользователей через API
fetch:
	@echo "Fetching users (count=5000)..."
	curl -X POST "http://localhost/v1/users/fetch?count=5000"

# Запуск нагрузочного теста Locust с веб-интерфейсом
load-test-ui:
	@echo "Starting load test with web UI..."
	@(cd backend && locust -f tests/load/locustfile.py --host=http://localhost --web-host=localhost)
