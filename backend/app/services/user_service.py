from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import func

from app.db.crud.users import create_user, delete_user, get_user, get_users, update_user
from app.db.models.user import User
from app.schemas.user import UserCreate, UserOut, UserUpdate
from app.services.api_client import fetch_random_users


async def fetch_and_save_users(db: AsyncSession, count: int) -> list[UserOut]:
    """
    Загружает и сохраняет указанное количество пользователей из randomuser.me.

    :param db: Асинхронная сессия SQLAlchemy.
    :type db: AsyncSession
    :param count: Количество пользователей для загрузки.
    :type count: int
    :returns: Список созданных пользователей.
    :rtype: List[UserOut]
    :raises ValueError: Если count > 10000.
    """
    if count > 10000:
        raise ValueError("Too many users requested")

    users_data: dict = await fetch_random_users(count)
    users: list[UserOut] = []
    for user_data in users_data["results"]:
        user: UserCreate = UserCreate(
            gender=user_data["gender"],
            first_name=user_data["name"]["first"],
            last_name=user_data["name"]["last"],
            phone=user_data["phone"],
            email=user_data["email"],
            location=f"{user_data['location']['city']}, {user_data['location']['country']}",
            picture=user_data["picture"]["thumbnail"],
        )
        db_user: UserOut = await create_user(db, user)
        users.append(db_user)
    return users


async def get_users_service(db: AsyncSession, limit: int, offset: int) -> list[UserOut]:
    """
    Получает список пользователей с пагинацией.

    :param db: Асинхронная сессия SQLAlchemy.
    :type db: AsyncSession
    :param limit: Количество записей на страницу.
    :type limit: int
    :param offset: Смещение для пагинации.
    :type offset: int
    :returns: Список пользователей.
    :rtype: List[UserOut]
    """
    return await get_users(db, limit, offset)


async def get_user_service(db: AsyncSession, user_id: int) -> UserOut | None:
    """
    Получает пользователя по ID.

    :param db: Асинхронная сессия SQLAlchemy.
    :type db: AsyncSession
    :param user_id: ID пользователя.
    :type user_id: int
    :returns: Пользователь или None, если не найден.
    :rtype: Optional[UserOut]
    """
    return await get_user(db, user_id)


async def update_user_service(db: AsyncSession, user_id: int, user_data: UserUpdate) -> UserOut | None:
    """
    Обновляет данные пользователя.

    :param db: Асинхронная сессия SQLAlchemy.
    :type db: AsyncSession
    :param user_id: ID пользователя.
    :type user_id: int
    :param user_data: Данные для обновления.
    :type user_data: UserUpdate
    :returns: Обновленный пользователь или None, если не найден.
    :rtype: Optional[UserOut]
    """
    return await update_user(db, user_id, user_data)


async def delete_user_service(db: AsyncSession, user_id: int) -> bool:
    """
    Удаляет пользователя по ID.

    :param db: Асинхронная сессия SQLAlchemy.
    :type db: AsyncSession
    :param user_id: ID пользователя.
    :type user_id: int
    :returns: True, если пользователь удален, False, если не найден.
    :rtype: bool
    """
    return await delete_user(db, user_id)


async def get_random_user_service(db: AsyncSession) -> UserOut | None:
    """
    Получает случайного пользователя из базы данных.

    :param db: Асинхронная сессия SQLAlchemy.
    :type db: AsyncSession
    :returns: Случайный пользователь или None, если база пуста.
    :rtype: Optional[UserOut]
    """
    result = await db.execute(func.random().select().join(User).order_by(func.random()).limit(1))
    return result.scalar_one_or_none()
