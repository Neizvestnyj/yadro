"""Модуль для SQLAlchemy моделей."""

from sqlalchemy.ext.declarative import declarative_base

Base: type[declarative_base] = declarative_base()
