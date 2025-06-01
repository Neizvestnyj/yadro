import random
import uuid

from locust import HttpUser, between, tag, task
from locust.clients import Response

MAX_OFFSET = MAX_USER_ID = 10000
USER_UPDATE_PAYLOADS = [
    {"first_name": "Alex", "last_name": "Tester", "email_suffix": "@testdomain.com"},
    {"first_name": "Maria", "last_name": "Load", "email_suffix": "@sample.org"},
    {"first_name": "John", "last_name": "Doe", "email_suffix": "@example.net"},
]


class BaseApiUser(HttpUser):
    """
    Базовый класс для пользователей API с общим временем ожидания.

    Все пути API теперь начинаются с /v1/
    """

    abstract = True
    wait_time = between(0.1, 0.5)

    def on_start(self) -> None:
        """Вызывается при старте каждого Locust-пользователя."""
        pass


class GetUsersUser(BaseApiUser):
    """Locust user для тестирования GET /v1/users."""

    weight = 40

    @task
    @tag("get_list", "read_heavy")
    def get_users(self) -> Response:
        """
        Отправляет GET запрос к "/v1/users" с пагинацией.

        :return: Ответ сервера
        :rtype: Response
        """
        limit = random.choice([10, 50, 100])
        offset = random.randrange(0, MAX_OFFSET, limit)
        with self.client.get("/api/v1/users", params={"limit": limit, "offset": offset}, catch_response=True) as resp:
            if resp.status_code != 200:
                resp.failure(f"Expected 200, got {resp.status_code}")
            elif not isinstance(resp.json(), list):
                resp.failure("Response is not a list")
            return resp


class GetUserByIdUser(BaseApiUser):
    """Locust user для тестирования GET /v1/users/{user_id}."""

    weight = 30

    @task
    @tag("get_by_id", "read_heavy")
    def get_user_by_id(self) -> Response:
        """
        Отправляет GET запрос к "/v1/users/{user_id}".

        :return: Ответ сервера
        :rtype: Response
        """
        user_id = random.randint(1, MAX_USER_ID)
        with self.client.get(f"/api/v1/users/{user_id}", catch_response=True) as resp:
            if resp.status_code not in (200, 404):
                resp.failure(f"Expected 200 or 404, got {resp.status_code}")
            return resp


class RandomUser(BaseApiUser):
    """Locust user для тестирования GET /v1/random."""

    weight = 10

    @task
    @tag("get_random", "read_heavy")
    def get_random(self) -> Response:
        """
        Отправляет GET запрос к "/v1/random".

        :return: Ответ сервера
        :rtype: Response
        """
        with self.client.get("/api/v1/random", catch_response=True) as resp:
            if resp.status_code != 200:
                resp.failure(f"Expected 200, got {resp.status_code}")
            return resp


class PutUser(BaseApiUser):
    """Locust user для тестирования PUT /v1/users/{user_id}."""

    weight = 10

    @task
    @tag("update_user", "write_operations")
    def put_user(self) -> Response:
        """
        Отправляет PUT запрос к "/v1/users/{user_id}".

        :return: Ответ сервера
        :rtype: Response
        """
        user_id = random.randint(1, MAX_USER_ID)
        payload_template = random.choice(USER_UPDATE_PAYLOADS)

        unique_part = str(uuid.uuid4())[:8]
        email = f"{payload_template['first_name'].lower()}_{unique_part}{payload_template['email_suffix']}"

        json_data = {
            "first_name": f"{payload_template['first_name']}_{unique_part}",
            "last_name": f"{payload_template['last_name']}Updated",
            "email": email,
        }
        with self.client.put(f"/api/v1/users/{user_id}", json=json_data, catch_response=True) as resp:
            if resp.status_code not in (200, 404):
                resp.failure(f"Expected 200 or 404, got {resp.status_code}")
            return resp
