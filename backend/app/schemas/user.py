from datetime import datetime

from pydantic import BaseModel


class UserBase(BaseModel):
    """
    Базовая схема для данных пользователя.

    :param gender: Пол пользователя.
    :type gender: str
    :param first_name: Имя пользователя.
    :type first_name: str
    :param last_name: Фамилия пользователя.
    :type last_name: str
    :param phone: Телефон пользователя.
    :type phone: str
    :param email: Email пользователя.
    :type email: str
    :param location: Место проживания пользователя.
    :type location: str
    :param picture: URL фотографии пользователя.
    :type picture: str
    """

    gender: str
    first_name: str
    last_name: str
    phone: str
    email: str
    location: str
    picture: str


class UserCreate(UserBase):
    """Схема для создания пользователя."""

    pass


class UserUpdate(BaseModel):
    """
    Схема для обновления пользователя.

    :param gender: Пол пользователя (опционально).
    :type gender: Optional[str]
    :param first_name: Имя пользователя (опционально).
    :type first_name: Optional[str]
    :param last_name: Фамилия пользователя (опционально).
    :type last_name: Optional[str]
    :param phone: Телефон пользователя (опционально).
    :type phone: Optional[str]
    :param email: Email пользователя (опционально).
    :type email: Optional[str]
    :param location: Место проживания пользователя (опционально).
    :type location: Optional[str]
    :param picture: URL фотографии пользователя (опционально).
    :type picture: Optional[str]
    """

    gender: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    phone: str | None = None
    email: str | None = None
    location: str | None = None
    picture: str | None = None


class UserOut(UserBase):
    """
    Схема для вывода данных пользователя.

    :param id: Уникальный идентификатор пользователя.
    :type id: int
    :param created_at: Время создания записи.
    :type created_at: datetime
    """

    id: int
    created_at: datetime

    class Config:
        """Конфигурация Pydantic для включения режима работы с ORM."""

        from_attributes = True
