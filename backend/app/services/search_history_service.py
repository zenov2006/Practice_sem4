from datetime import datetime

from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from app.core.constants import SEARCH_HISTORY_LIMIT
from app.models.search_history import SearchHistory


def format_search_history_item(history_item: SearchHistory) -> dict[str, int | str]:
    """
    Преобразует запись истории поиска в словарь для API-ответа.

    Args:
        history_item: Запись истории поиска из базы данных.

    Returns:
        dict[str, int | str]: Данные записи истории поиска.
    """
    created_at = history_item.created_at

    timestamp = ""
    created_at_iso = ""

    if isinstance(created_at, datetime):
        timestamp = created_at.strftime("%d.%m.%Y %H:%M")
        created_at_iso = created_at.isoformat()

    return {
        "id": history_item.id,
        "query": history_item.query,
        "timestamp": timestamp,
        "created_at": created_at_iso,
    }


def save_search_query(db: Session, query: str) -> SearchHistory:
    """
    Сохраняет поисковый запрос в историю.

    Если такой запрос уже есть, старая запись удаляется,
    а новая добавляется в начало истории.

    Args:
        db: Сессия базы данных.
        query: Поисковый запрос.

    Returns:
        SearchHistory: Созданная запись истории поиска.

    Raises:
        ValueError: Если поисковый запрос пустой.
    """
    normalized_query = query.strip()

    if not normalized_query:
        raise ValueError("Поисковый запрос не должен быть пустым")

    db.execute(
        delete(SearchHistory).where(
            func.lower(SearchHistory.query) == normalized_query.lower()
        )
    )

    history_item = SearchHistory(query=normalized_query)

    db.add(history_item)
    db.commit()
    db.refresh(history_item)

    return history_item


def get_last_search_queries(
    db: Session,
    limit: int = SEARCH_HISTORY_LIMIT,
) -> list[dict[str, int | str]]:
    """
    Возвращает последние поисковые запросы.

    Args:
        db: Сессия базы данных.
        limit: Максимальное количество записей.

    Returns:
        list[dict[str, int | str]]: Список последних поисковых запросов.
    """
    statement = (
        select(SearchHistory)
        .order_by(SearchHistory.created_at.desc(), SearchHistory.id.desc())
        .limit(limit)
    )

    history_items = db.scalars(statement).all()

    return [
        format_search_history_item(history_item)
        for history_item in history_items
    ]


def clear_search_history(db: Session) -> None:
    """
    Очищает историю поисковых запросов.

    Args:
        db: Сессия базы данных.
    """
    db.execute(delete(SearchHistory))
    db.commit()