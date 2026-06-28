<h1 align="center">Backend для системы поиска по документам</h1>

<p align="center">
Backend-часть проекта отвечает за загрузку документов, извлечение текста, индексацию данных и полнотекстовый поиск по загруженным материалам.
</p>

---

## Описание

Backend реализован на FastAPI и предоставляет API для работы с документами форматов PDF и DOCX.
После загрузки файл проходит проверку, сохраняется локально, затем из него извлекается текст. Полученный текст разбивается на небольшие фрагменты — чанки. После этого чанки отправляются в Elasticsearch, где по ним можно выполнять полнотекстовый поиск.

Для ускорения повторных поисковых запросов используется Redis. Если пользователь повторяет один и тот же запрос, backend может вернуть результат из кеша, не обращаясь повторно к Elasticsearch.

Backend также согласован с frontend-частью проекта. Frontend отправляет запросы на адрес `http://localhost:8000/api`, поэтому основные маршруты backend имеют вид:

```text
POST /api/upload
GET  /api/search
GET  /api/health
```

---

## Используемые технологии

В backend-части используются:

```text
FastAPI          — создание REST API
Uvicorn          — запуск backend-сервера
pdfplumber       — извлечение текста из PDF
python-docx      — извлечение текста из DOCX
Elasticsearch    — полнотекстовый поиск по документам
Redis            — кеширование поисковых запросов
Docker           — запуск инфраструктурных сервисов
Swagger UI       — просмотр и проверка API
```

---

## Как работает обработка документа

При загрузке документа backend выполняет несколько шагов.

Сначала файл считывается и проходит валидацию. Проверяется имя файла, расширение и размер. Разрешены только файлы `.pdf` и `.docx`, максимальный размер файла — 20 МБ.

После проверки backend создаёт UUID для документа и сохраняет файл в локальную папку. Затем в зависимости от формата вызывается нужный парсер: для PDF используется `pdfplumber`, для DOCX используется `python-docx`.

Извлечённый текст разбивается на чанки размером 1000 символов с перекрытием 100 символов. Перекрытие нужно для того, чтобы смысловой фрагмент не терялся на границе двух соседних частей текста.

Каждый чанк получает метаданные:

```text
document_id
chunk_id
file_name
page_number
chunk_index
text
```

После этого чанки индексируются в Elasticsearch в индекс `documents`.

---

## Запуск backend

Перед запуском backend должны быть доступны Elasticsearch и Redis.

### Запуск Elasticsearch

Из корня проекта:

```powershell
docker compose up -d elasticsearch
```

Проверить Elasticsearch можно в браузере:

```text
http://localhost:9200
```

---

### Запуск Redis

Если контейнер Redis ещё не создан:

```powershell
docker run --name practice-redis -p 6379:6379 -d redis:7-alpine
```

Если контейнер уже создан:

```powershell
docker start practice-redis
```

Проверить запущенные контейнеры можно командой:

```powershell
docker ps
```

---

### Запуск backend через Uvicorn

Из папки `backend`:

```powershell
cd C:\Practice_sem4\backend
python -m uvicorn app.main:app --reload
```

После запуска Swagger UI будет доступен по адресу:

```text
http://localhost:8000/docs
```

---

## API

## Проверка работоспособности backend

```http
GET /api/health
```

Ручка нужна для быстрой проверки, что backend запущен и отвечает на запросы.

Пример ответа:

```json
{
  "status": "ok",
  "service": "backend"
}
```

---

## Загрузка документа

```http
POST /api/upload
```

Ручка принимает PDF или DOCX файл, проверяет его, сохраняет, извлекает текст, разбивает текст на чанки и отправляет данные в Elasticsearch.

Тип запроса:

```text
multipart/form-data
```

Параметр:

```text
file — загружаемый PDF или DOCX документ
```

Пример успешного ответа:

```json
{
  "document_id": "ebceecbf-73cb-4b86-aee5-fb9b3f11dc46",
  "file_name": "document.pdf",
  "stored_file_name": "ebceecbf-73cb-4b86-aee5-fb9b3f11dc46.pdf",
  "file_size": 201956,
  "pages_count": 4,
  "chunks_count": 13,
  "chunks": 13,
  "indexed_chunks_count": 13,
  "status": "indexed"
}
```

Поле `chunks` добавлено для совместимости с frontend-частью проекта. Frontend использует его для отображения количества созданных чанков после загрузки файла.

Возможные ошибки:

```json
{
  "status": "error",
  "detail": "Разрешены только файлы PDF и DOCX",
  "path": "/api/upload"
}
```

```json
{
  "status": "error",
  "detail": "Файл не должен быть пустым",
  "path": "/api/upload"
}
```

```json
{
  "status": "error",
  "detail": "Размер файла не должен превышать 20 МБ",
  "path": "/api/upload"
}
```

---

## Поиск по документам

```http
GET /api/search
```

Ручка выполняет полнотекстовый поиск по загруженным и проиндексированным документам.

Параметры запроса:

```text
q       — поисковый запрос
limit   — количество результатов, по умолчанию 10
offset  — смещение результатов, по умолчанию 0
```

Пример запроса:

```text
http://localhost:8000/api/search?q=информация&limit=3&offset=0
```

Пример ответа:

```json
{
  "query": "информация",
  "limit": 3,
  "offset": 0,
  "results_count": 3,
  "total_count": 12,
  "cache_hit": false,
  "results": [
    {
      "chunk_id": "doc-1_1_1",
      "file_name": "document.pdf",
      "page": 1,
      "page_number": 1,
      "text": "Фрагмент найденного текста...",
      "score": 1.0
    }
  ]
}
```

Поле `cache_hit` показывает, откуда был получен результат:

```text
false — результат получен из Elasticsearch
true  — результат получен из Redis cache
```

---

## Пагинация поиска

Поиск поддерживает параметры `limit` и `offset`.

Пример первой страницы:

```text
/api/search?q=информация&limit=3&offset=0
```

Пример второй страницы:

```text
/api/search?q=информация&limit=3&offset=3
```

Пример третьей страницы:

```text
/api/search?q=информация&limit=3&offset=6
```

Пагинация нужна для того, чтобы backend мог отдавать результаты поиска частями, а не возвращать слишком большой список одним ответом.

---

## Кеширование поиска

Для повторных поисковых запросов используется Redis.

Логика работы кеша:

```text
первый запрос  → Elasticsearch → сохранение результата в Redis
повторный запрос → Redis → быстрый возврат результата
```

Время жизни кеша:

```text
300 секунд
```

То есть результат хранится 5 минут.

Ключ кеша формируется с учётом:

```text
поискового запроса
limit
offset
```

Это нужно, чтобы разные страницы поиска кешировались отдельно.

Пример:

```text
/api/search?q=информация&limit=3&offset=0
```

Первый ответ:

```json
{
  "cache_hit": false
}
```

Повторный такой же запрос:

```json
{
  "cache_hit": true
}
```

---

## Формат ошибок

Backend возвращает ошибки в едином формате.

Пример:

```json
{
  "status": "error",
  "detail": "Описание ошибки",
  "path": "/api/search"
}
```

Для ошибок валидации дополнительно возвращается поле `errors`.

Пример ошибки при неправильном `limit`:

```json
{
  "status": "error",
  "detail": "Ошибка валидации запроса",
  "path": "/api/search",
  "errors": [
    {
      "loc": ["query", "limit"],
      "msg": "Input should be less than or equal to 50",
      "type": "less_than_equal"
    }
  ]
}
```

---

## Связь с frontend

Frontend обращается к backend по адресу:

```text
http://localhost:8000/api
```

Используемые frontend-запросы:

```text
POST /api/upload
GET  /api/search?q=...
```

Backend возвращает данные в формате, который frontend может сразу отобразить: имя файла, найденный текст, релевантность и количество чанков после загрузки.

---

## Быстрая проверка

Проверка backend:

```text
http://localhost:8000/api/health
```

Проверка Swagger UI:

```text
http://localhost:8000/docs
```

Проверка Elasticsearch:

```text
http://localhost:9200
```

Проверка количества документов в индексе:

```text
http://localhost:9200/documents/_count
```

Проверка поиска:

```text
http://localhost:8000/api/search?q=информация
```

