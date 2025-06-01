from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.user import UserOut
from app.services.user_service import get_random_user_service

router: APIRouter = APIRouter(prefix="/api/v1", tags=["random"])
db_dependency = Depends(get_db)


@router.get("/random", response_model=UserOut)
async def get_random_user(db: AsyncSession = db_dependency) -> UserOut:
    """
    Получает случайного пользователя из базы данных.

    :param db: Асинхронная сессия SQLAlchemy.
    :type db: AsyncSession
    :returns: Данные случайного пользователя.
    :rtype: UserOut
    :raises HTTPException: Если в базе нет пользователей.
    """
    db = db or Depends(get_db)
    user = await get_random_user_service(db)
    if not user:
        raise HTTPException(status_code=404, detail="User not found") from None
    return user
