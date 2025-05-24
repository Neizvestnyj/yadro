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
    :rtype: User
    """
    db_user = User(**user.model_dump())
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    user_out = UserOut.model_validate(db_user)
    return user_out


async def get_users(db: AsyncSession, limit: int, offset: int) -> list[User]:
    """
    Получает список пользователей с пагинацией.

    :param db: Асинхронная сессия SQLAlchemy.
    :type db: AsyncSession
    :param limit: Количество записей на страницу.
    :type limit: int
    :param offset: Смещение для пагинации.
    :type offset: int
    :returns: Список пользователей.
    :rtype: List[User]
    """
    result = await db.execute(select(User).offset(offset).limit(limit))
    return result.scalars().all()


async def get_user(db: AsyncSession, user_id: int) -> User | None:
    """
    Получает пользователя по ID.

    :param db: Асинхронная сессия SQLAlchemy.
    :type db: AsyncSession
    :param user_id: ID пользователя.
    :type user_id: int
    :returns: Пользователь или None, если не найден.
    :rtype: Optional[User]
    """
    result = await db.execute(select(User).filter_by(id=user_id))
    return result.scalar_one_or_none()


async def update_user(db: AsyncSession, user_id: int, user_data: UserUpdate) -> User | None:
    """
    Обновляет данные пользователя.

    :param db: Асинхронная сессия SQLAlchemy.
    :type db: AsyncSession
    :param user_id: ID пользователя.
    :type user_id: int
    :param user_data: Данные для обновления.
    :type user_data: UserUpdate
    :returns: Обновленный пользователь или None, если не найден.
    :rtype: Optional[User]
    """
    result = await db.execute(select(User).filter_by(id=user_id))
    user = result.scalar_one_or_none()
    if not user:
        return None
    for key, value in user_data.model_dump(exclude_unset=True).items():
        setattr(user, key, value)
    await db.commit()
    await db.refresh(user)
    return user


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
    result = await db.execute(select(User).filter_by(id=user_id))
    user = result.scalar_one_or_none()
    if not user:
        return False
    await db.delete(user)
    await db.commit()
    return True
