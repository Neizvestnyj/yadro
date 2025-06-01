import asyncio

from faker import Faker

fake = Faker()


async def fake_fetch_random_users(count: int) -> dict:
    """
    Асинхронно получает указанное количество фейковых случайных пользователей.

    :param count: Количество случайных пользователей для получения.
    :type count: int
    :return: Словарь с данными полученных случайных пользователей.
    :rtype: dict
    :raises ValueError: Если count меньше или равен нулю.
    :raises Exception: При общих ошибках получения данных.
    """
    results = []
    for _ in range(count):
        user = {
            "gender": fake.random_element(elements=("male", "female")),
            "name": {
                "title": fake.prefix(),
                "first": fake.first_name(),
                "last": fake.last_name(),
            },
            "location": {
                "street": {"number": fake.building_number(), "name": fake.street_name()},
                "city": fake.city(),
                "state": fake.state(),
                "country": fake.country(),
                "postcode": fake.postcode(),
                "coordinates": {
                    "latitude": fake.latitude(),
                    "longitude": fake.longitude(),
                },
                "timezone": {"offset": fake.timezone()[:10]},
            },
            "phone": fake.phone_number(),
            "cell": fake.phone_number(),
            "email": fake.email(),
            "id": {"value": fake.uuid4()},
            "login": {"username": fake.user_name(), "uuid": fake.uuid4()},
            "picture": {"thumbnail": fake.image_url()},
            "dob": {"date": fake.iso8601()},
            "registered": {"date": fake.iso8601()},
            "nat": fake.country_code(),
        }
        results.append(user)
    await asyncio.sleep(0)
    return {"results": results}
