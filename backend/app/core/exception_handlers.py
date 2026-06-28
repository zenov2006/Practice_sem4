from typing import Any

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


def format_validation_errors(errors: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Приводит ошибки валидации FastAPI к безопасному JSON-формату.

    Args:
        errors: Список ошибок валидации FastAPI.

    Returns:
        list[dict[str, Any]]: Упрощённый список ошибок.
    """
    formatted_errors: list[dict[str, Any]] = []

    for error in errors:
        formatted_errors.append(
            {
                "loc": error.get("loc", []),
                "msg": error.get("msg", ""),
                "type": error.get("type", ""),
            }
        )

    return formatted_errors


def register_exception_handlers(app: FastAPI) -> None:
    """
    Регистрирует обработчики ошибок для FastAPI-приложения.

    Args:
        app: Экземпляр FastAPI-приложения.
    """

    @app.exception_handler(HTTPException)
    async def http_exception_handler(
        request: Request,
        exc: HTTPException,
    ) -> JSONResponse:
        """
        Обрабатывает HTTPException и возвращает единый JSON-ответ.

        Args:
            request: HTTP-запрос.
            exc: Исключение FastAPI.

        Returns:
            JSONResponse: Ответ с описанием ошибки.
        """
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "status": "error",
                "detail": exc.detail,
                "path": request.url.path,
            },
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request,
        exc: RequestValidationError,
    ) -> JSONResponse:
        """
        Обрабатывает ошибки валидации входных данных.

        Args:
            request: HTTP-запрос.
            exc: Ошибка валидации FastAPI.

        Returns:
            JSONResponse: Ответ с описанием ошибок валидации.
        """
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "status": "error",
                "detail": "Ошибка валидации запроса",
                "path": request.url.path,
                "errors": format_validation_errors(exc.errors()),
            },
        )

    @app.exception_handler(Exception)
    async def unexpected_exception_handler(
        request: Request,
        exc: Exception,
    ) -> JSONResponse:
        """
        Обрабатывает непредвиденные ошибки приложения.

        Args:
            request: HTTP-запрос.
            exc: Непредвиденное исключение.

        Returns:
            JSONResponse: Ответ с сообщением о внутренней ошибке сервера.
        """
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "status": "error",
                "detail": "Внутренняя ошибка сервера",
                "path": request.url.path,
            },
        )