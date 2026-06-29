from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.constants import DATABASE_URL


engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    """
    Базовый класс для всех SQLAlchemy-моделей приложения.
    """


def get_db() -> Generator[Session, None, None]:
    """
    Создаёт сессию базы данных для обработки одного HTTP-запроса.

    Yields:
        Session: Сессия SQLAlchemy.
    """
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()