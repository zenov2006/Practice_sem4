from fastapi import APIRouter, status


router = APIRouter()


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    summary="Проверка backend health",
)
def check_health() -> dict[str, str]:
    """
    Проверка что Backend работает.
    То что получим:
        dict[str, str]: Состаяние бэкенд сервиса.
    """
    return {
        "Статус": "ok",
        "Сервис": "backend",
    }