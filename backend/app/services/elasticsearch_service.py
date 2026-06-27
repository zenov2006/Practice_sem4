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


def index_document_chunks(chunks: list[dict[str, int | str | float]]) -> int:
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