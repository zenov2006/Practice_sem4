from fastapi import APIRouter, Query, status

from app.services.cache_service import (
    get_cached_search_response,
    set_cached_search_response,
)
from app.services.elasticsearch_service import search_document_chunks


router = APIRouter()


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

    Endpoint поддерживает кеширование через Redis и пагинацию
    через параметры limit и offset.

    Args:
        q: Поисковый запрос.
        limit: Максимальное количество результатов.
        offset: Смещение результатов поиска.

    Returns:
        dict[str, str | int | bool | list[dict[str, str | int | float]]]: Результаты поиска.
    """
    cached_response = get_cached_search_response(
        query=q,
        limit=limit,
        offset=offset,
    )

    if cached_response is not None:
        return {
            "query": q,
            "limit": limit,
            "offset": offset,
            "results_count": int(cached_response["results_count"]),
            "total_count": int(cached_response["total_count"]),
            "cache_hit": True,
            "results": cached_response["results"],
        }

    search_response = search_document_chunks(
        query=q,
        limit=limit,
        offset=offset,
    )

    set_cached_search_response(
        query=q,
        limit=limit,
        offset=offset,
        search_response=search_response,
    )

    return {
        "query": q,
        "limit": limit,
        "offset": offset,
        "results_count": int(search_response["results_count"]),
        "total_count": int(search_response["total_count"]),
        "cache_hit": False,
        "results": search_response["results"],
    }