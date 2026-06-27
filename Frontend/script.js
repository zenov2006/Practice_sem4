/* ========== Конфигурация API ========== */
const API_URL = 'http://localhost:8000/api';

/* ========== DOM-элементы ========== */
const dropZone = document.getElementById('dropZone');
const fileInput = document.getElementById('fileInput');
const fileList = document.getElementById('fileList');
const searchInput = document.getElementById('searchInput');
const searchBtn = document.getElementById('searchBtn');
const resultsDiv = document.getElementById('results');

/* ========== Загрузка файлов ========== */

dropZone.addEventListener('click', () => fileInput.click());

dropZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropZone.classList.add('dragover');
});

dropZone.addEventListener('dragleave', () => {
    dropZone.classList.remove('dragover');
});

dropZone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropZone.classList.remove('dragover');
    const files = e.dataTransfer.files;
    if (files.length) uploadFiles(files);
});

fileInput.addEventListener('change', () => {
    if (fileInput.files.length) {
        uploadFiles(fileInput.files);
        fileInput.value = '';
    }
});

async function uploadFiles(files) {
    for (const file of files) {
        const ext = file.name.split('.').pop().toLowerCase();
        
        if (!['pdf', 'docx'].includes(ext)) {
            addFileToList(file.name, 'Неподдерживаемый формат', 'error');
            continue;
        }

        if (file.size > 20 * 1024 * 1024) {
            addFileToList(file.name, 'Превышен размер (20 МБ)', 'error');
            continue;
        }

        addFileToList(file.name, 'Загрузка...', 'loading');

        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await fetch(`${API_URL}/upload`, {
                method: 'POST',
                body: formData,
            });

            if (response.ok) {
                const data = await response.json();
                updateFileStatus(file.name, `Готово (${data.chunks} чанков)`, 'done');
            } else {
                const err = await response.json();
                updateFileStatus(file.name, `Ошибка: ${err.detail || 'неизвестная'}`, 'error');
            }
        } catch {
            updateFileStatus(file.name, 'Ошибка соединения', 'error');
        }
    }
}

function addFileToList(name, statusText, statusClass) {
    const item = document.createElement('div');
    item.className = 'file-item';
    item.dataset.filename = name;
    item.innerHTML = `
        <span class="filename">${name}</span>
        <span class="status ${statusClass}">${statusText}</span>
    `;
    fileList.appendChild(item);
}

function updateFileStatus(name, statusText, statusClass) {
    const items = fileList.querySelectorAll('.file-item');
    for (const item of items) {
        if (item.dataset.filename === name) {
            const statusSpan = item.querySelector('.status');
            statusSpan.textContent = statusText;
            statusSpan.className = `status ${statusClass}`;
            break;
        }
    }
}

/* ========== Поиск ========== */

searchBtn.addEventListener('click', performSearch);
searchInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') performSearch();
});

async function performSearch() {
    const query = searchInput.value.trim();
    
    if (!query) {
        resultsDiv.innerHTML = `<div class="empty-message">Введите поисковый запрос</div>`;
        return;
    }

    resultsDiv.innerHTML = `<div class="loading-spinner">Поиск...</div>`;

    try {
        const response = await fetch(`${API_URL}/search?q=${encodeURIComponent(query)}`);
        const data = await response.json();

        if (!response.ok) {
            resultsDiv.innerHTML = `<div class="empty-message">Ошибка: ${data.detail || 'неизвестная'}</div>`;
            return;
        }

        displayResults(data.results, query);
    } catch {
        resultsDiv.innerHTML = `<div class="empty-message">Ошибка соединения с сервером</div>`;
    }
}

function displayResults(results, query) {
    if (!results || results.length === 0) {
        resultsDiv.innerHTML = `
            <div class="empty-message">
                По запросу <strong>«${query}»</strong> ничего не найдено
            </div>
        `;
        return;
    }

    let html = '';
    const words = query.split(/\s+/).filter(w => w.length > 1);

    for (const result of results) {
        let text = result.text || '';
        
        for (const word of words) {
            const regex = new RegExp(`(${word})`, 'gi');
            text = text.replace(regex, '<span class="highlight">$1</span>');
        }

        const scorePercent = Math.round((result.score || 0) * 100);

        html += `
            <div class="result-card">
                <div class="file-name">${result.file_name || 'Файл'}</div>
                <div class="text">${text.substring(0, 500)}${text.length > 500 ? '...' : ''}</div>
                <div class="score">Релевантность: ${scorePercent}%</div>
            </div>
        `;
    }

    resultsDiv.innerHTML = html;
}

/* ========== Начальное состояние ========== */
resultsDiv.innerHTML = `
    <div class="empty-message">
        Загрузите документы для начала работы
    </div>
`;