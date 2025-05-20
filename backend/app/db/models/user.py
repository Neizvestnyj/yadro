from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.sql import func

from app.db.models import Base


class User(Base):
    """
    Модель пользователя для таблицы 'users'.

    Атрибуты:
        id (int): Уникальный идентификатор пользователя.
        gender (str): Пол пользователя.
        first_name (str): Имя пользователя.
        last_name (str): Фамилия пользователя.
        phone (str): Телефон пользователя.
        email (str): Email пользователя.
        location (str): Место проживания пользователя.
        picture (str): URL фотографии пользователя.
        created_at (datetime): Время создания записи.
    """

    __tablename__ = "users"

    id: Column = Column(Integer, primary_key=True, index=True)
    gender: Column = Column(String(50))
    first_name: Column = Column(String(100))
    last_name: Column = Column(String(100))
    phone: Column = Column(String(50))
    email: Column = Column(String(100), index=True)
    location: Column = Column(String)
    picture: Column = Column(String(255))
    created_at: Column = Column(DateTime, default=func.now())
