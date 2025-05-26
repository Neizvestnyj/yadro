from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import func

from app.core.cache import cache
from app.core.logging import logger
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
    if count > 5000:
        raise ValueError("Too many users requested, max - 5000")

    users_data: dict = await fetch_random_users(count)  # Получаем данные пользователей из randomuser.me.
    users: list[UserOut] = []
    for user_data in users_data["results"]:
        try:
            user = UserCreate(
                gender=user_data["gender"],
                title=user_data["name"]["title"],
                first_name=user_data["name"]["first"],
                last_name=user_data["name"]["last"],
                street_number=user_data["location"]["street"]["number"],
                street_name=user_data["location"]["street"]["name"],
                city=user_data["location"]["city"],
                state=user_data["location"]["state"],
                country=user_data["location"]["country"],
                postcode=str(user_data["location"]["postcode"]),
                latitude=float(user_data["location"]["coordinates"]["latitude"]),
                longitude=float(user_data["location"]["coordinates"]["longitude"]),
                timezone_offset=user_data["location"]["timezone"]["offset"],
                phone=user_data["phone"],
                cell=user_data["cell"],
                email=user_data["email"],
                external_id=user_data["id"]["value"],
                username=user_data["login"]["username"],
                uuid=user_data["login"]["uuid"],
                picture=user_data["picture"]["thumbnail"],
                dob=user_data["dob"]["date"],
                registered_at=user_data["registered"]["date"],
                nat=user_data["nat"],
            )
            user_out: UserOut = await create_user(db, user)
            users.append(user_out)
        except ValidationError as e:
            await db.rollback()

            logger.warning(f"Value is not a valid email address {user_data['email']}: {e}")
            continue
        except IntegrityError as e:
            await db.rollback()

            error_msg = str(e.orig)
            if "email" in error_msg:
                logger.warning(f"Duplicate email detected: {user_data['email']}")
            elif "username" in error_msg:
                logger.warning(f"Duplicate username detected: {user_data['username']}")
            elif "uuid" in error_msg:
                logger.warning(f"Duplicate UUID detected: {user_data['uuid']}")
            else:
                logger.error(f"Database integrity error: {e}")
            continue

    # Инвалидация кэша списка пользователей
    await cache.delete("users:*")
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
    cache_key = f"users:limit={limit}:offset={offset}"
    cached_users = await cache.get(cache_key)
    if cached_users:
        return [UserOut(**user) for user in cached_users]

    users: list[UserOut] = await get_users(db, limit, offset)
    await cache.set(cache_key, [user.model_dump() for user in users], ttl=300)
    return users


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
    cache_key = f"user:{user_id}"
    cached_user = await cache.get(cache_key)
    if cached_user:
        return UserOut(**cached_user)

    user: UserOut = await get_user(db, user_id)
    if user:
        await cache.set(cache_key, user.model_dump(), ttl=300)
    return user


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
    user: UserOut = await update_user(db, user_id, user_data)
    if user:
        # Инвалидация кэша
        await cache.delete(f"user:{user_id}")
        await cache.delete("users:*")
    return user


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
    success = await delete_user(db, user_id)
    if success:
        # Инвалидация кэша
        await cache.delete(f"user:{user_id}")
        await cache.delete("users:*")
    return success


async def get_random_user_service(db: AsyncSession) -> UserOut | None:
    """
    Получает случайного пользователя из базы данных.

    :param db: Асинхронная сессия SQLAlchemy.
    :type db: AsyncSession
    :returns: Случайный пользователь или None, если база пуста.
    :rtype: Optional[UserOut]
    """
    stmt = select(User).order_by(func.random()).limit(1)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    return UserOut.model_validate(user) if user else None
