```bash
cp .env.example .env
```
```bash
ELASTICSEARCH_URL=http://elasticsearch:9200
ELASTICSEARCH_INDEX_NAME=documents
```

```bash
docker compose up -d --build
```

```bash
# Проверить статус контейнеров
docker compose ps
```
# Проверить Elasticsearch
curl http://localhost:9200

**Перезапуск:**
```bash
docker compose down
docker compose up -d
```
**Пересборка:**
```bash
docker compose up -d --build
```
**Логи:**
```bash
docker compose logs backend --tail=50
docker compose logs elasticsearch --tail=50
```
**Остановка:**
```bash
docker compose down
```
