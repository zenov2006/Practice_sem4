set -e

API_URL="http://localhost:8010/api/upload"
TEST_DIR="./backend/tests/fixtures"

echo "Запуск инициализации тестовых данных..."

# Создаём папку для тестовых файлов, если её нет
mkdir -p "$TEST_DIR"

# Список URL тестовых PDF-лекций (из открытых источников)
PDF_URLS=(
    "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf"
    "https://www.africau.edu/images/default/sample.pdf"
    "https://www.orimi.com/pdf-test.pdf"
)

# Скачиваем файлы
echo " Скачивание тестовых PDF-файлов..."
for url in "${PDF_URLS[@]}"; do
    filename=$(basename "$url")
    filepath="$TEST_DIR/$filename"
    
    if [ ! -f "$filepath" ]; then
        echo "  Скачивание: $filename"
        curl -s -L -o "$filepath" "$url"
    else
        echo "  Файл уже существует: $filename"
    fi
done

echo ""

# Загружаем файлы через API
echo "Загрузка PDF-файлов в систему..."

for file in "$TEST_DIR"/*.pdf; do
    if [ -f "$file" ]; then
        filename=$(basename "$file")
        echo "  Загрузка: $filename"
        
        curl -s -X POST "$API_URL" \
            -H "accept: application/json" \
            -H "Content-Type: multipart/form-data" \
            -F "file=@$file" \
            -o /dev/null \
            -w "    Статус: %{http_code}\n"
    fi
done

echo ""
echo "Инициализация завершена!"
echo "Загруженные файлы:"
ls -la "$TEST_DIR"/*.pdf 2>/dev/null || echo "  Нет файлов"

echo ""
echo "Проверьте поиск: http://localhost:3000"