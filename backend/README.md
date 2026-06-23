# Backend

Backend-часть системы полнотекстового поиска по документам.

## Стек

- Python
- FastAPI
- Uvicorn
- PostgreSQL
- Elasticsearch
- Redis
- Pytest

## Локальный запуск

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload