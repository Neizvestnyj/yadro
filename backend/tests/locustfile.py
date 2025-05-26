import random

from locust import HttpUser, between, task
from locust.clients import Response

MAX_OFFSET = MAX_USER_ID = 10000

class GetUsersUser(HttpUser):
    """
    Locust user для тестирования GET /v1/users.

    :param wait_time: Время ожидания между запросами (в секундах).
    :type wait_time: locust.wait_time
    :param page_size: Размер страницы для пагинации.
    :type page_size: int
    """

    wait_time = between(0.01, 0.05)
    page_size = 10

    @task
    def get_users(self) -> Response:
        """
        Отправляет GET запрос к "/v1/users" с пагинацией.

        :return: Ответ сервера
        :rtype: Response
        """
        limit = random.choice([10, 50, 100])
        offset = random.randrange(0, MAX_OFFSET, limit)
        with self.client.get(
            "/v1/users", params={"limit": limit, "offset": offset}, catch_response=True
        ) as resp:
            if resp.status_code != 200:
                resp.failure(f"Expected 200, got {resp.status_code}")
            elif not isinstance(resp.json(), list):
                resp.failure("Response is not a list")
            return resp


class GetUserByIdUser(HttpUser):
    """
    Locust user для тестирования GET /v1/users/{user_id}.

    :param wait_time: Время ожидания между запросами (в секундах).
    :type wait_time: locust.wait_time
    """

    wait_time = between(0.01, 0.05)

    @task
    def get_user_by_id(self) -> Response:
        """
        Отправляет GET запрос к "/v1/users/{user_id}".

        :return: Ответ сервера
        :rtype: Response
        """
        user_id = random.randint(1, MAX_USER_ID)
        with self.client.get(f"/v1/users/{user_id}", catch_response=True) as resp:
            if resp.status_code not in (200, 404):  # 404 допустим
                resp.failure(f"Expected 200 or 404, got {resp.status_code}")
            return resp


class RandomUser(HttpUser):
    """
    Locust user для тестирования GET /v1/random.

    :param wait_time: Время ожидания между запросами (в секундах).
    :type wait_time: locust.wait_time
    """

    wait_time = between(0.01, 0.05)

    @task
    def get_random(self) -> Response:
        """
        Отправляет GET запрос к "/v1/random".

        :return: Ответ сервера
        :rtype: Response
        """
        with self.client.get("/v1/random", catch_response=True) as resp:
            if resp.status_code != 200:
                resp.failure(f"Expected 200, got {resp.status_code}")
            return resp


class PutUser(HttpUser):
    """
    Locust user для тестирования PUT /v1/users/{user_id}.

    :param wait_time: Время ожидания между запросами (в секундах).
    :type wait_time: locust.wait_time
    """

    wait_time = between(0.01, 0.05)

    @task
    def put_user(self) -> Response:
        """
        Отправляет PUT запрос к "/v1/users/{user_id}".

        :return: Ответ сервера
        :rtype: Response
        """
        user_id = random.randint(1, MAX_USER_ID)
        json_data = {
            "first_name": f"Test_{user_id}",
            "last_name": "Updated",
            "email": f"test_{user_id}@example.com"
        }
        with self.client.put(f"/v1/users/{user_id}", json=json_data, catch_response=True) as resp:
            if resp.status_code not in (200, 404):
                resp.failure(f"Expected 200 or 404, got {resp.status_code}")
            return resp
