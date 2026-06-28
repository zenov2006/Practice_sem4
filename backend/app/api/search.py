from fastapi import APIRouter, Query, status

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
) -> dict[str, str | int | list[dict[str, str | int | float]]]:
    """
    Выполняет полнотекстовый поиск по чанкам документов в Elasticsearch.

    Args:
        q: Поисковый запрос.
        limit: Максимальное количество результатов.

    Returns:
        dict[str, str | int | list[dict[str, str | int | float]]]: Результаты поиска.
    """
    results = search_document_chunks(query=q, limit=limit)

    return {
        "query": q,
        "results_count": len(results),
        "results": results,
    }