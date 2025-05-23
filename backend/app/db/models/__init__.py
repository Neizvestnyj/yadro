"""Модуль для SQLAlchemy моделей."""

from sqlalchemy.orm import declarative_base

Base: type[declarative_base] = declarative_base()

from .user import User  # noqa: E402, F401
