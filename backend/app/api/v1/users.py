from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.user import UserOut, UserUpdate
from app.services.user_service import (
    delete_user_service,
    fetch_and_save_users,
    get_user_service,
    get_users_service,
    update_user_service,
)

router: APIRouter = APIRouter(prefix="/v1", tags=["users"])

db_dependency = Depends(get_db)


@router.post("/users/fetch", response_model=list[UserOut])
async def fetch_users(count: int, db: AsyncSession = db_dependency) -> list[UserOut]:
    """
    Загружает указанное количество пользователей из randomuser.me.

    :param count: Количество пользователей для загрузки.
    :type count: int
    :param db: Асинхронная сессия SQLAlchemy.
    :type db: AsyncSession
    :returns: Список созданных пользователей.
    :rtype: List[UserOut]
    :raises HTTPException: Если count > 10000 или запрос к API не удался.
    """
    try:
        users: list[UserOut] = await fetch_and_save_users(db, count)
        return users
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.get("/users", response_model=list[UserOut])
async def read_users(limit: int = 10, offset: int = 0, db: AsyncSession = db_dependency) -> list[UserOut]:
    """
    Получает список пользователей с пагинацией.

    :param limit: Количество записей на страницу (по умолчанию 10).
    :type limit: int
    :param offset: Смещение для пагинации (по умолчанию 0).
    :type offset: int
    :param db: Асинхронная сессия SQLAlchemy.
    :type db: AsyncSession
    :returns: Список пользователей.
    :rtype: List[UserOut]
    """
    return await get_users_service(db, limit, offset)


@router.get("/users/{user_id}", response_model=UserOut)
async def read_user(user_id: int, db: AsyncSession = db_dependency) -> UserOut:
    """
    Получает пользователя по ID.

    :param user_id: ID пользователя.
    :type user_id: int
    :param db: Асинхронная сессия SQLAlchemy.
    :type db: AsyncSession
    :returns: Данные пользователя.
    :rtype: UserOut
    :raises HTTPException: Если пользователь не найден.
    """
    user = await get_user_service(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found") from None
    return user


@router.put("/users/{user_id}", response_model=UserOut)
async def update_user(user_id: int, user: UserUpdate, db: AsyncSession = db_dependency) -> UserOut:
    """
    Обновляет данные пользователя.

    :param user_id: ID пользователя.
    :type user_id: int
    :param user: Данные для обновления.
    :type user: UserUpdate
    :param db: Асинхронная сессия SQLAlchemy.
    :type db: AsyncSession
    :returns: Обновленные данные пользователя.
    :rtype: UserOut
    :raises HTTPException: Если пользователь не найден.
    """
    updated_user = await update_user_service(db, user_id, user)
    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found") from None
    return updated_user


@router.delete("/users/{user_id}", status_code=204)
async def delete_user(user_id: int, db: AsyncSession = db_dependency) -> None:
    """
    Удаляет пользователя по ID.

    :param user_id: ID пользователя.
    :type user_id: int
    :param db: Асинхронная сессия SQLAlchemy.
    :type db: AsyncSession
    :returns: Ничего не возвращает.
    :rtype: None
    :raises HTTPException: Если пользователь не найден.
    """
    success: bool = await delete_user_service(db, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found") from None
