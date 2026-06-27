from pathlib import Path

from fastapi import HTTPException, UploadFile, status

from app.core.constants import ALLOWED_FILE_EXTENSIONS, MAX_FILE_SIZE_BYTES


def get_file_extension(filename: str) -> str:
    """
    Получает расширение файла из его имени.

    Args:
        filename: Исходное имя загруженного файла.

    Returns:
        str: Расширение файла в нижнем регистре.
    """
    return Path(filename).suffix.lower()


def validate_upload_file(file: UploadFile, file_content: bytes) -> str:
    """
    Проверяет загруженный файл по имени, расширению, размеру и содержимому.

    Args:
        file: Загруженный файл FastAPI.
        file_content: Содержимое файла в байтах.

    Returns:
        str: Расширение файла, если проверка прошла успешно.

    Raises:
        HTTPException: Если файл не прошёл проверку.
    """
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Не указано имя файла",
        )

    file_extension = get_file_extension(file.filename)

    if file_extension not in ALLOWED_FILE_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Разрешены только файлы PDF и DOCX",
        )

    if len(file_content) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Файл не должен быть пустым",
        )

    if len(file_content) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Размер файла не должен превышать 20 МБ",
        )

    return file_extension