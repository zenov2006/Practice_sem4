from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException, UploadFile, status

from app.core.constants import UPLOAD_DIR
from app.services.document_parser import extract_text_from_document
from app.services.elasticsearch_service import index_document_chunks
from app.services.file_validator import validate_upload_file
from app.services.text_chunker import create_document_chunks


async def process_uploaded_document(file: UploadFile) -> dict[str, str | int]:
    """
    Обрабатывает загруженный документ от момента получения файла до индексации.

    Этапы обработки:
    - чтение содержимого файла;
    - валидация имени, расширения и размера;
    - генерация UUID документа;
    - сохранение файла в локальное хранилище;
    - извлечение текста из PDF или DOCX;
    - разбиение текста на чанки;
    - индексация чанков в Elasticsearch.

    Args:
        file: Загруженный PDF или DOCX файл.

    Returns:
        dict[str, str | int]: Информация об обработанном и проиндексированном документе.

    Raises:
        HTTPException: Если файл не прошёл проверку или не был обработан.
    """
    file_content = await file.read()
    file_extension = validate_upload_file(file, file_content)

    document_id = str(uuid4())
    original_file_name = Path(file.filename or "").name
    stored_file_name = f"{document_id}{file_extension}"

    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    file_path = UPLOAD_DIR / stored_file_name
    file_path.write_bytes(file_content)

    try:
        pages_text = extract_text_from_document(file_path)
        document_chunks = create_document_chunks(
            document_id=document_id,
            file_name=original_file_name,
            pages_text=pages_text,
        )

        indexed_chunks_count = index_document_chunks(document_chunks)

    except HTTPException:
        if file_path.exists():
            file_path.unlink()

        raise

    except Exception as exc:
        if file_path.exists():
            file_path.unlink()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при обработке документа",
        ) from exc

    chunks_count = len(document_chunks)

    return {
        "document_id": document_id,
        "file_name": original_file_name,
        "stored_file_name": stored_file_name,
        "file_size": len(file_content),
        "pages_count": len(pages_text),
        "chunks_count": chunks_count,
        "chunks": chunks_count,
        "indexed_chunks_count": indexed_chunks_count,
        "status": "indexed",
    }