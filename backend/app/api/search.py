from fastapi import APIRouter, Body, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.cache_service import (
    get_cached_search_response,
    set_cached_search_response,
)
from app.services.elasticsearch_service import search_document_chunks
from app.services.search_history_service import (
    clear_search_history,
    get_last_search_queries,
    save_search_query,
)


router = APIRouter()


class SearchHistoryCreate(BaseModel):
    """
    Схема запроса для сохранения поискового запроса в историю.
    """

    query: str = Field(..., min_length=1, description="Поисковый запрос")


@router.get(
    "/search",
    status_code=status.HTTP_200_OK,
    summary="Поиск по загруженным документам",
)
def search_documents(
    q: str = Query(..., min_length=1, description="Поисковый запрос"),
    limit: int = Query(10, ge=1, le=50, description="Максимальное количество результатов"),
    offset: int = Query(0, ge=0, description="Смещение результатов поиска"),
) -> dict[str, str | int | bool | list[dict[str, str | int | float]]]:
    """
    Выполняет полнотекстовый поиск по чанкам документов.

    Endpoint поддерживает поиск через Elasticsearch, кеширование
    через Redis и пагинацию через параметры limit и offset.

    Args:
        q: Поисковый запрос.
        limit: Максимальное количество результатов.
        offset: Смещение результатов поиска.

    Returns:
        dict[str, str | int | bool | list[dict[str, str | int | float]]]: Результаты поиска.

    Raises:
        HTTPException: Если поисковый запрос пустой.
    """
    query = q.strip()

    if not query:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Поисковый запрос не должен быть пустым",
        )

    cached_response = get_cached_search_response(
        query=query,
        limit=limit,
        offset=offset,
    )

    if cached_response is not None:
        return {
            "query": query,
            "limit": limit,
            "offset": offset,
            "results_count": int(cached_response["results_count"]),
            "total_count": int(cached_response["total_count"]),
            "cache_hit": True,
            "results": cached_response["results"],
        }

    search_response = search_document_chunks(
        query=query,
        limit=limit,
        offset=offset,
    )

    set_cached_search_response(
        query=query,
        limit=limit,
        offset=offset,
        search_response=search_response,
    )

    return {
        "query": query,
        "limit": limit,
        "offset": offset,
        "results_count": int(search_response["results_count"]),
        "total_count": int(search_response["total_count"]),
        "cache_hit": False,
        "results": search_response["results"],
    }


@router.post(
    "/search/history",
    status_code=status.HTTP_200_OK,
    summary="Сохранение поискового запроса в историю",
)
def add_search_history_item(
    history_item: SearchHistoryCreate = Body(...),
    db: Session = Depends(get_db),
) -> dict[str, str | list[dict[str, int | str]]]:
    """
    Сохраняет поисковый запрос в историю поиска.

    Args:
        history_item: Данные поискового запроса.
        db: Сессия базы данных.

    Returns:
        dict[str, str | list[dict[str, int | str]]]: Статус операции и история поиска.

    Raises:
        HTTPException: Если поисковый запрос пустой.
    """
    query = history_item.query.strip()

    if not query:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Поисковый запрос не должен быть пустым",
        )

    save_search_query(db=db, query=query)

    return {
        "status": "saved",
        "query": query,
        "history": get_last_search_queries(db=db),
    }


@router.get(
    "/search/history",
    status_code=status.HTTP_200_OK,
    summary="Получение истории поисковых запросов",
)
def read_search_history(
    db: Session = Depends(get_db),
) -> dict[str, list[dict[str, int | str]]]:
    """
    Возвращает список последних поисковых запросов.

    Args:
        db: Сессия базы данных.

    Returns:
        dict[str, list[dict[str, int | str]]]: История поисковых запросов.
    """
    return {
        "history": get_last_search_queries(db=db),
    }


@router.delete(
    "/search/history",
    status_code=status.HTTP_200_OK,
    summary="Очистка истории поисковых запросов",
)
def delete_search_history(
    db: Session = Depends(get_db),
) -> dict[str, str | list[dict[str, int | str]]]:
    """
    Очищает историю поисковых запросов.

    Args:
        db: Сессия базы данных.

    Returns:
        dict[str, str | list[dict[str, int | str]]]: Статус операции и пустая история.
    """
    clear_search_history(db=db)

    return {
        "status": "cleared",
        "history": [],
    }