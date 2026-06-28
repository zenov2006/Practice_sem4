from fastapi import APIRouter, Query, status

from app.services.cache_service import (
    get_cached_search_results,
    set_cached_search_results,
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
) -> dict[str, str | int | bool | list[dict[str, str | int | float]]]:
    """
    Выполняет полнотекстовый поиск по чанкам документов.

    Сначала endpoint пытается получить результаты из Redis.
    Если кеша нет, выполняется поиск в Elasticsearch, после чего
    результат сохраняется в Redis на 5 минут.

    Args:
        q: Поисковый запрос.
        limit: Максимальное количество результатов.

    Returns:
        dict[str, str | int | bool | list[dict[str, str | int | float]]]: Результаты поиска.
    """
    cached_results = get_cached_search_results(query=q, limit=limit)

    if cached_results is not None:
        return {
            "query": q,
            "results_count": len(cached_results),
            "cache_hit": True,
            "results": cached_results,
        }

    results = search_document_chunks(query=q, limit=limit)
    set_cached_search_results(query=q, limit=limit, results=results)

    return {
        "query": q,
        "results_count": len(results),
        "cache_hit": False,
        "results": results,
    }