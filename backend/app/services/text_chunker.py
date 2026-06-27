from app.core.constants import TEXT_CHUNK_OVERLAP, TEXT_CHUNK_SIZE


def split_text_into_chunks(
    text: str,
    chunk_size: int = TEXT_CHUNK_SIZE,
    overlap: int = TEXT_CHUNK_OVERLAP,
) -> list[str]:
    """
    Разбивает текст на чанки фиксированного размера с перекрытием.

    Args:
        text: Исходный текст документа или страницы.
        chunk_size: Максимальный размер одного чанка в символах.
        overlap: Количество символов, которые повторяются между соседними чанками.

    Returns:
        list[str]: Список текстовых чанков.

    Raises:
        ValueError: Если размер чанка или перекрытие заданы некорректно.
    """
    cleaned_text = " ".join(text.split())

    if not cleaned_text:
        return []

    if chunk_size <= 0:
        raise ValueError("Размер чанка должен быть больше нуля")

    if overlap < 0:
        raise ValueError("Перекрытие не может быть отрицательным")

    if overlap >= chunk_size:
        raise ValueError("Перекрытие должно быть меньше размера чанка")

    chunks: list[str] = []
    start = 0

    while start < len(cleaned_text):
        end = start + chunk_size
        chunk = cleaned_text[start:end]

        if chunk:
            chunks.append(chunk)

        start += chunk_size - overlap

    return chunks


def create_document_chunks(
    document_id: str,
    file_name: str,
    pages_text: list[dict[str, int | str]],
) -> list[dict[str, int | str]]:
    """
    Создаёт список чанков документа с метаданными.

    Args:
        document_id: UUID загруженного документа.
        file_name: Исходное имя файла.
        pages_text: Список страниц с текстом.

    Returns:
        list[dict[str, int | str]]: Список чанков с метаданными.
    """
    document_chunks: list[dict[str, int | str]] = []

    for page_data in pages_text:
        page_number = int(page_data["page_number"])
        page_text = str(page_data["text"])

        text_chunks = split_text_into_chunks(page_text)

        for chunk_index, chunk_text in enumerate(text_chunks, start=1):
            chunk_id = f"{document_id}_{page_number}_{chunk_index}"

            document_chunks.append(
                {
                    "document_id": document_id,
                    "chunk_id": chunk_id,
                    "file_name": file_name,
                    "page_number": page_number,
                    "chunk_index": chunk_index,
                    "text": chunk_text,
                }
            )

    return document_chunks