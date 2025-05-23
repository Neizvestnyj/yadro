from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    """
    Базовая схема для данных пользователя.

    :param gender: Пол пользователя (например, 'male', 'female').
    :type gender: str
    :param title: Обращение (например, 'Mr', 'Miss', 'Mrs').
    :type title: str | None
    :param first_name: Имя пользователя.
    :type first_name: str
    :param last_name: Фамилия пользователя.
    :type last_name: str
    :param street_number: Номер дома.
    :type street_number: int | None
    :param street_name: Название улицы.
    :type street_name: str | None
    :param city: Город.
    :type city: str | None
    :param state: Штат или регион.
    :type state: str | None
    :param country: Страна.
    :type country: str | None
    :param postcode: Почтовый индекс.
    :type postcode: str | None
    :param latitude: Широта.
    :type latitude: float | None
    :param longitude: Долгота.
    :type longitude: float | None
    :param timezone_offset: Смещение часового пояса (например, '+9:30').
    :type timezone_offset: str | None
    :param phone: Основной телефон.
    :type phone: str | None
    :param cell: Мобильный телефон.
    :type cell: str | None
    :param email: Email пользователя.
    :type email: str
    :param external_id: Внешний идентификатор (например, SSN).
    :type external_id: str | None
    :param username: Имя пользователя для входа.
    :type username: str | None
    :param uuid: Уникальный UUID пользователя.
    :type uuid: str | None
    :param picture: URL фотографии пользователя (thumbnail).
    :type picture: str | None
    :param dob: Дата рождения.
    :type dob: datetime | None
    :param registered_at: Дата регистрации.
    :type registered_at: datetime | None
    :param nat: Национальность (например, 'US').
    :type nat: str | None
    """

    gender: str
    title: str | None = None
    first_name: str
    last_name: str
    street_number: int | None = None
    street_name: str | None = None
    city: str | None = None
    state: str | None = None
    country: str | None = None
    postcode: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    timezone_offset: str | None = None
    phone: str | None = None
    cell: str | None = None
    email: EmailStr
    external_id: str | None = None
    username: str | None = None
    uuid: str | None = None
    picture: str | None = None
    dob: datetime | None = None
    registered_at: datetime | None = None
    nat: str | None = None


class UserCreate(UserBase):
    """
    Схема для создания пользователя.

    Обязательные поля: gender, first_name, last_name, email.
    Остальные поля опциональны, унаследованы от UserBase.
    """

    gender: str = Field(..., min_length=1)
    first_name: str = Field(..., min_length=1)
    last_name: str = Field(..., min_length=1)
    email: EmailStr = Field(..., min_length=1)


class UserUpdate(BaseModel):
    """
    Схема для обновления пользователя.

    Все поля опциональны, чтобы можно было обновлять только часть данных.

    :param gender: Пол пользователя.
    :type gender: str | None
    :param title: Обращение.
    :type title: str | None
    :param first_name: Имя пользователя.
    :type first_name: str | None
    :param last_name: Фамилия пользователя.
    :type last_name: str | None
    :param street_number: Номер дома.
    :type street_number: int | None
    :param street_name: Название улицы.
    :type street_name: str | None
    :param city: Город.
    :type city: str | None
    :param state: Штат или регион.
    :type state: str | None
    :param country: Страна.
    :type country: str | None
    :param postcode: Почтовый индекс.
    :type postcode: str | None
    :param latitude: Широта.
    :type latitude: float | None
    :param longitude: Долгота.
    :type longitude: float | None
    :param timezone_offset: Смещение часового пояса.
    :type timezone_offset: str | None
    :param phone: Основной телефон.
    :type phone: str | None
    :param cell: Мобильный телефон.
    :type cell: str | None
    :param email: Email пользователя.
    :type email: EmailStr | None
    :param external_id: Внешний идентификатор.
    :type external_id: str | None
    :param username: Имя пользователя.
    :type username: str | None
    :param uuid: Уникальный UUID.
    :type uuid: str | None
    :param picture: URL фотографии.
    :type picture: str | None
    :param dob: Дата рождения.
    :type dob: datetime | None
    :param registered_at: Дата регистрации.
    :type registered_at: datetime | None
    :param nat: Национальность.
    :type nat: str | None
    """

    gender: str | None = None
    title: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    street_number: int | None = None
    street_name: str | None = None
    city: str | None = None
    state: str | None = None
    country: str | None = None
    postcode: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    timezone_offset: str | None = None
    phone: str | None = None
    cell: str | None = None
    email: EmailStr | None = None
    external_id: str | None = None
    username: str | None = None
    uuid: str | None = None
    picture: str | None = None
    dob: datetime | None = None
    registered_at: datetime | None = None
    nat: str | None = None


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
