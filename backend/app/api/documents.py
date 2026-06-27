from fastapi import APIRouter, File, UploadFile, status

from app.services.document_service import process_uploaded_document


router = APIRouter()


@router.post(
    "/upload",
    status_code=status.HTTP_200_OK,
    summary="Загрузка PDF или DOCX документа",
)
async def upload_document(file: UploadFile = File(...)) -> dict[str, str | int]:
    """
    Загружает PDF или DOCX документ и запускает его полную обработку.

    Endpoint принимает файл, передаёт его в сервис обработки документа
    и возвращает результат обработки: UUID документа, имя файла,
    количество страниц, количество чанков и количество проиндексированных чанков.

    Args:
        file: Загружаемый PDF или DOCX файл.

    Returns:
        dict[str, str | int]: Информация об обработанном и проиндексированном документе.
    """
    return await process_uploaded_document(file)