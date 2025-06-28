from sqlalchemy import delete, insert, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.db.models.user import User
from app.schemas.user import UserCreate, UserOut, UserUpdate


async def create_user(db: AsyncSession, user: UserCreate) -> UserOut:
    """
    Создает нового пользователя в базе данных.

    :param db: Асинхронная сессия SQLAlchemy.
    :type db: AsyncSession
    :param user: Данные для создания пользователя.
    :type user: UserCreate
    :returns: Созданный пользователь.
    :rtype: UserOut
    """
    stmt = insert(User).values(**user.model_dump()).returning(User)
    result = await db.execute(stmt)
    await db.commit()
    created_user = result.scalar_one()
    user_out = UserOut.model_validate(created_user)

    return user_out


async def get_users(db: AsyncSession, limit: int, offset: int) -> list[UserOut]:
    """
    Получает список пользователей с пагинацией.

    :param db: Асинхронная сессия SQLAlchemy.
    :type db: AsyncSession
    :param limit: Количество записей на страницу.
    :type limit: int
    :param offset: Смещение для пагинации.
    :type offset: int
    :returns: Список пользователей.
    :rtype: list[UserOut]
    """
    result = await db.execute(select(User).offset(offset).limit(limit))
    users = result.scalars().all()

    return [UserOut.model_validate(user) for user in users]


async def get_user(db: AsyncSession, user_id: int) -> UserOut | None:
    """
    Получает пользователя по ID.

    :param db: Асинхронная сессия SQLAlchemy.
    :type db: AsyncSession
    :param user_id: ID пользователя.
    :type user_id: int
    :returns: Пользователь или None, если не найден.
    :rtype: UserOut | None
    """
    result = await db.execute(select(User).filter_by(id=user_id))
    user = result.scalar_one_or_none()

    return UserOut.model_validate(user) if user else None


async def update_user(db: AsyncSession, user_id: int, user_data: UserUpdate) -> UserOut | None:
    """
    Обновляет данные пользователя.

    :param db: Асинхронная сессия SQLAlchemy.
    :type db: AsyncSession
    :param user_id: ID пользователя.
    :type user_id: int
    :param user_data: Данные для обновления.
    :type user_data: UserUpdate
    :returns: Обновленный пользователь или None, если не найден.
    :rtype: UserOut | None
    """
    values = user_data.model_dump(exclude_unset=True)
    if not values:
        return None

    stmt = update(User).where(User.id == user_id).values(**values).returning(User)
    result = await db.execute(stmt)
    await db.commit()
    updated_user = result.scalar_one_or_none()

    if updated_user is None:
        return None

    return UserOut.model_validate(updated_user)


async def delete_user(db: AsyncSession, user_id: int) -> bool:
    """
    Удаляет пользователя по ID.

    :param db: Асинхронная сессия SQLAlchemy.
    :type db: AsyncSession
    :param user_id: ID пользователя.
    :type user_id: int
    :returns: True, если пользователь удален, False, если не найден.
    :rtype: bool
    """
    stmt = delete(User).where(User.id == user_id).returning(User.id)
    result = await db.execute(stmt)
    await db.commit()
    deleted_id = result.scalar_one_or_none()

    return True if deleted_id else False
