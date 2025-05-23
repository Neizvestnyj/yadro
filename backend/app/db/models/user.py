from sqlalchemy import Column, DateTime, Float, Integer, String
from sqlalchemy.sql import func

from app.db.models import Base


class User(Base):
    """
    Модель пользователя для таблицы 'users'.

    Атрибуты:
        id (int): Уникальный идентификатор пользователя.
        gender (str): Пол пользователя (например, 'male', 'female').
        title (str): Обращение (например, 'Mr', 'Miss', 'Mrs').
        first_name (str): Имя пользователя.
        last_name (str): Фамилия пользователя.
        street_number (int): Номер дома.
        street_name (str): Название улицы.
        city (str): Город.
        state (str): Штат или регион.
        country (str): Страна.
        postcode (str): Почтовый индекс.
        latitude (float): Широта.
        longitude (float): Долгота.
        timezone_offset (str): Смещение часового пояса (например, '+9:30').
        phone (str): Основной телефон.
        cell (str): Мобильный телефон.
        email (str): Email пользователя.
        external_id (str): Внешний идентификатор (например, SSN).
        username (str): Имя пользователя для входа.
        uuid (str): Уникальный UUID пользователя.
        picture (str): URL фотографии пользователя (thumbnail).
        dob (datetime): Дата рождения.
        registered_at (datetime): Дата регистрации.
        nat (str): Национальность (например, 'US').
        created_at (datetime): Время создания записи.
    """

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    gender = Column(String(50), nullable=False)
    title = Column(String(50))
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    street_number = Column(Integer)
    street_name = Column(String(100))
    city = Column(String(100), index=True)
    state = Column(String(100))
    country = Column(String(100), index=True)
    postcode = Column(String(10))
    latitude = Column(Float)
    longitude = Column(Float)
    timezone_offset = Column(String(10))
    phone = Column(String(50))
    cell = Column(String(50))
    email = Column(String(100), index=True, unique=True)
    external_id = Column(String(100))
    username = Column(String(100), index=True)
    uuid = Column(String(100), unique=True)
    picture = Column(String(255))
    dob = Column(DateTime(timezone=True))
    registered_at = Column(DateTime(timezone=True))
    nat = Column(String(10))
    created_at = Column(DateTime(timezone=True), default=func.now())
