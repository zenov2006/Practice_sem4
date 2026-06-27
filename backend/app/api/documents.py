from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, File, UploadFile, status

from app.core.constants import UPLOAD_DIR
from app.services.document_parser import extract_text_from_document
from app.services.elasticsearch_service import index_document_chunks
from app.services.file_validator import validate_upload_file
from app.services.text_chunker import create_document_chunks


router = APIRouter()


@router.post(
    "/upload",
    status_code=status.HTTP_200_OK,
    summary="Загрузка PDF или DOCX документа",
)
async def upload_document(file: UploadFile = File(...)) -> dict[str, str | int]:
    """
    Загружает документ, проверяет его, сохраняет, извлекает текст,
    разбивает текст на чанки и индексирует чанки в Elasticsearch.

    На текущем этапе endpoint выполняет:
    - проверку имени файла;
    - проверку расширения PDF/DOCX;
    - проверку размера файла до 20 МБ;
    - проверку, что файл не пустой;
    - генерацию UUID документа;
    - сохранение файла в папку storage/uploads;
    - извлечение текста из PDF или DOCX;
    - разбиение текста на чанки по 1000 символов с перекрытием 100 символов;
    - индексацию чанков в Elasticsearch.

    Args:
        file: Загружаемый PDF или DOCX файл.

    Returns:
        dict[str, str | int]: Информация об обработанном и проиндексированном документе.
    """
    file_content = await file.read()
    file_extension = validate_upload_file(file, file_content)

    document_id = str(uuid4())
    original_file_name = Path(file.filename).name
    stored_file_name = f"{document_id}{file_extension}"

    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    file_path = UPLOAD_DIR / stored_file_name
    file_path.write_bytes(file_content)

    pages_text = extract_text_from_document(file_path)
    document_chunks = create_document_chunks(
        document_id=document_id,
        file_name=original_file_name,
        pages_text=pages_text,
    )

    indexed_chunks_count = index_document_chunks(document_chunks)

    return {
        "document_id": document_id,
        "file_name": original_file_name,
        "stored_file_name": stored_file_name,
        "file_size": len(file_content),
        "pages_count": len(pages_text),
        "chunks_count": len(document_chunks),
        "indexed_chunks_count": indexed_chunks_count,
        "status": "indexed",
    }