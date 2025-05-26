from locust import HttpUser, between, task
from locust.clients import Response


class ApiUser(HttpUser):
    """
    Locust user class для нагрузочного тестирования API.

    :param wait_time: Время ожидания между запросами (в секундах).
    :type wait_time: locust.wait_time
    """

    wait_time = between(0.01, 0.1)

    @task(3)
    def get_users(self) -> Response:
        """
        Отправляет GET запрос к "/v1/users".

        :return: Ответ сервера
        :rtype: Response
        """
        return self.client.get("/v1/users")

    @task(3)
    def get_user_by_id(self) -> Response:
        """
        Отправляет GET запрос к "/v1/users/1".

        :return: Ответ сервера
        :rtype: Response
        """
        return self.client.get("/v1/users/1")

    @task(2)
    def get_random(self) -> Response:
        """
        Отправляет GET запрос к "/v1/random".

        :return: Ответ сервера
        :rtype: Response
        """
        return self.client.get("/v1/random")

    @task(1)
    def put_user(self) -> Response:
        """
        Отправляет PUT запрос к "/v1/users/1" с JSON телом.

        :return: Ответ сервера
        :rtype: Response
        """
        return self.client.put("/v1/users/1", json={"name": "ABTest"})
