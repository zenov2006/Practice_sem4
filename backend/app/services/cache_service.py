import json
from hashlib import sha256

from redis import Redis
from redis.exceptions import RedisError

from app.core.constants import REDIS_URL, SEARCH_CACHE_TTL_SECONDS


def get_redis_client() -> Redis:
    """
    Создаёт клиент для подключения к Redis.

    Returns:
        Redis: Клиент Redis.
    """
    return Redis.from_url(
        REDIS_URL,
        decode_responses=True,
    )


def build_search_cache_key(query: str, limit: int) -> str:
    """
    Создаёт ключ кеша для поискового запроса.

    Args:
        query: Поисковый запрос пользователя.
        limit: Максимальное количество результатов.

    Returns:
        str: Ключ кеша Redis.
    """
    normalized_query = query.strip().lower()
    raw_key = f"{normalized_query}:{limit}"
    hashed_key = sha256(raw_key.encode("utf-8")).hexdigest()

    return f"search:{hashed_key}"


def get_cached_search_results(
    query: str,
    limit: int,
) -> list[dict[str, str | int | float]] | None:
    """
    Получает результаты поиска из Redis, если они есть в кеше.

    Args:
        query: Поисковый запрос пользователя.
        limit: Максимальное количество результатов.

    Returns:
        list[dict[str, str | int | float]] | None: Результаты поиска или None.
    """
    redis_client = get_redis_client()
    cache_key = build_search_cache_key(query=query, limit=limit)

    try:
        cached_data = redis_client.get(cache_key)

        if cached_data is None:
            return None

        return json.loads(cached_data)

    except (RedisError, json.JSONDecodeError):
        return None


def set_cached_search_results(
    query: str,
    limit: int,
    results: list[dict[str, str | int | float]],
) -> None:
    """
    Сохраняет результаты поиска в Redis на ограниченное время.

    Args:
        query: Поисковый запрос пользователя.
        limit: Максимальное количество результатов.
        results: Результаты поиска.
    """
    redis_client = get_redis_client()
    cache_key = build_search_cache_key(query=query, limit=limit)

    try:
        redis_client.setex(
            name=cache_key,
            time=SEARCH_CACHE_TTL_SECONDS,
            value=json.dumps(results, ensure_ascii=False),
        )
    except RedisError:
        return