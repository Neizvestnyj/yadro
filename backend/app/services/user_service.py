from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import func

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
    if count > 10000:
        raise ValueError("Too many users requested")

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
            db_user: UserOut = await create_user(db, user)
            users.append(db_user)
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
    stmt = select(User).order_by(func.random()).limit(1)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    return UserOut.model_validate(user) if user else None
