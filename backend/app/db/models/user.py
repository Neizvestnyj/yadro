from sqlalchemy import Column, DateTime, Float, Integer, String
from sqlalchemy.sql import func

from app.db.models.base import Base


class User(Base):
    """
    Модель пользователя для таблицы 'users'.

    :param id: Уникальный идентификатор пользователя.
    :type id: int
    :param gender: Пол пользователя (например, 'male', 'female').
    :type gender: str
    :param title: Обращение (например, 'Mr', 'Miss', 'Mrs').
    :type title: str
    :param first_name: Имя пользователя.
    :type first_name: str
    :param last_name: Фамилия пользователя.
    :type last_name: str
    :param street_number: Номер дома.
    :type street_number: int
    :param street_name: Название улицы.
    :type street_name: str
    :param city: Город.
    :type city: str
    :param state: Штат или регион.
    :type state: str
    :param country: Страна.
    :type country: str
    :param postcode: Почтовый индекс.
    :type postcode: str
    :param latitude: Широта.
    :type latitude: float
    :param longitude: Долгота.
    :type longitude: float
    :param timezone_offset: Смещение часового пояса (например, '+9:30').
    :type timezone_offset: str
    :param phone: Основной телефон.
    :type phone: str
    :param cell: Мобильный телефон.
    :type cell: str
    :param email: Email пользователя.
    :type email: str
    :param external_id: Внешний идентификатор (например, SSN).
    :type external_id: str
    :param username: Имя пользователя для входа.
    :type username: str
    :param uuid: Уникальный UUID пользователя.
    :type uuid: str
    :param picture: URL фотографии пользователя (thumbnail).
    :type picture: str
    :param dob: Дата рождения.
    :type dob: datetime.datetime
    :param registered_at: Дата регистрации.
    :type registered_at: datetime.datetime
    :param nat: Национальность (например, 'US').
    :type nat: str
    :param created_at: Время создания записи.
    :type created_at: datetime.datetime
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
