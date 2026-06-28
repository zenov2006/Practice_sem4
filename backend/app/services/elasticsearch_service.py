from elasticsearch import Elasticsearch
from fastapi import HTTPException, status

from app.core.constants import ELASTICSEARCH_INDEX_NAME, ELASTICSEARCH_URL


def get_elasticsearch_client() -> Elasticsearch:
    """
    Создаёт клиент для подключения к Elasticsearch.

    Returns:
        Elasticsearch: Клиент Elasticsearch.
    """
    return Elasticsearch(
        ELASTICSEARCH_URL,
        request_timeout=30,
    )


def create_documents_index_if_not_exists() -> None:
    """
    Создаёт индекс documents в Elasticsearch, если он ещё не существует.

    Индекс использует русскоязычный анализатор для полнотекстового поиска.
    """
    client = get_elasticsearch_client()

    try:
        if client.indices.exists(index=ELASTICSEARCH_INDEX_NAME):
            return

        index_body = {
            "settings": {
                "analysis": {
                    "analyzer": {
                        "analysis-ru": {
                            "type": "russian",
                        }
                    }
                }
            },
            "mappings": {
                "properties": {
                    "document_id": {"type": "keyword"},
                    "chunk_id": {"type": "keyword"},
                    "file_name": {"type": "keyword"},
                    "page_number": {"type": "integer"},
                    "chunk_index": {"type": "integer"},
                    "text": {
                        "type": "text",
                        "analyzer": "analysis-ru",
                    },
                }
            },
        }

        client.indices.create(
            index=ELASTICSEARCH_INDEX_NAME,
            body=index_body,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при создании индекса Elasticsearch",
        ) from exc


def index_document_chunks(chunks: list[dict[str, int | str]]) -> int:
    """
    Индексирует чанки документа в Elasticsearch.

    Args:
        chunks: Список чанков документа с метаданными.

    Returns:
        int: Количество успешно проиндексированных чанков.

    Raises:
        HTTPException: Если Elasticsearch недоступен или произошла ошибка индексации.
    """
    if not chunks:
        return 0

    create_documents_index_if_not_exists()
    client = get_elasticsearch_client()

    indexed_chunks_count = 0

    try:
        for chunk in chunks:
            client.index(
                index=ELASTICSEARCH_INDEX_NAME,
                id=str(chunk["chunk_id"]),
                document=chunk,
            )
            indexed_chunks_count += 1

        client.indices.refresh(index=ELASTICSEARCH_INDEX_NAME)

        return indexed_chunks_count
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при индексации документа в Elasticsearch",
        ) from exc


def search_document_chunks(
    query: str,
    limit: int = 10,
    offset: int = 0,
) -> dict[str, int | list[dict[str, str | int | float]]]:
    """
    Выполняет полнотекстовый поиск по чанкам документов в Elasticsearch.

    Поиск поддерживает параметры limit и offset для пагинации.

    Args:
        query: Поисковый запрос пользователя.
        limit: Максимальное количество результатов.
        offset: Смещение результатов поиска.

    Returns:
        dict[str, int | list[dict[str, str | int | float]]]: Ответ с результатами и общим количеством найденных документов.
    """
    client = get_elasticsearch_client()

    try:
        if not client.indices.exists(index=ELASTICSEARCH_INDEX_NAME):
            return {
                "results_count": 0,
                "total_count": 0,
                "results": [],
            }

        response = client.search(
            index=ELASTICSEARCH_INDEX_NAME,
            query={
                "bool": {
                    "should": [
                        {
                            "multi_match": {
                                "query": query,
                                "fields": ["text"],
                                "fuzziness": "AUTO",
                            }
                        },
                        {
                            "match_phrase_prefix": {
                                "text": {
                                    "query": query,
                                    "max_expansions": 50,
                                }
                            }
                        },
                    ],
                    "minimum_should_match": 1,
                }
            },
            size=limit,
            from_=offset,
        )

        hits = response["hits"]["hits"]
        total_data = response["hits"]["total"]

        if isinstance(total_data, dict):
            total_count = int(total_data.get("value", 0))
        else:
            total_count = int(total_data)

        max_score = response["hits"].get("max_score") or 1

        results: list[dict[str, str | int | float]] = []

        for hit in hits:
            source = hit["_source"]
            raw_score = hit.get("_score") or 0
            normalized_score = raw_score / max_score if max_score else 0

            results.append(
                {
                    "chunk_id": str(source.get("chunk_id", "")),
                    "file_name": str(source.get("file_name", "")),
                    "page": int(source.get("page_number", 0)),
                    "page_number": int(source.get("page_number", 0)),
                    "text": str(source.get("text", "")),
                    "score": round(normalized_score, 2),
                }
            )

        return {
            "results_count": len(results),
            "total_count": total_count,
            "results": results,
        }

    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при поиске в Elasticsearch",
        ) from exc