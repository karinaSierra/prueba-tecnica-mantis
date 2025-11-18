const uploadArea = document.getElementById('uploadArea');
const fileInput = document.getElementById('fileInput');
const fileInfo = document.getElementById('fileInfo');
const fileName = document.getElementById('fileName');
const removeFile = document.getElementById('removeFile');
const processBtn = document.getElementById('processBtn');
const loading = document.getElementById('loading');
const summarySection = document.getElementById('summarySection');
const summaryList = document.getElementById('summaryList');
const error = document.getElementById('error');
const errorMessage = document.getElementById('errorMessage');

let selectedFile = null;

// Click en el área de carga
uploadArea.addEventListener('click', () => {
    fileInput.click();
});

// Drag and drop
uploadArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadArea.style.borderColor = '#764ba2';
});

uploadArea.addEventListener('dragleave', () => {
    uploadArea.style.borderColor = '#667eea';
});

uploadArea.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadArea.style.borderColor = '#667eea';
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        handleFile(files[0]);
    }
});

// Selección de archivo
fileInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
        handleFile(e.target.files[0]);
    }
});

// Manejar archivo seleccionado
function handleFile(file) {
    const validTypes = ['application/pdf', 'text/plain'];
    const validExtensions = ['.pdf', '.txt'];
    const fileExtension = '.' + file.name.split('.').pop().toLowerCase();

    if (!validTypes.includes(file.type) && !validExtensions.includes(fileExtension)) {
        showError('Por favor, selecciona un archivo PDF o TXT válido.');
        return;
    }

    selectedFile = file;
    fileName.textContent = file.name;
    fileInfo.style.display = 'flex';
    processBtn.disabled = false;
    hideError();
    hideSummary();
}

// Remover archivo
removeFile.addEventListener('click', () => {
    selectedFile = null;
    fileInput.value = '';
    fileInfo.style.display = 'none';
    processBtn.disabled = true;
    hideError();
    hideSummary();
});

// Procesar archivo
processBtn.addEventListener('click', async () => {
    if (!selectedFile) return;

    hideError();
    hideSummary();
    showLoading();
    processBtn.disabled = true;

    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
        const response = await fetch('/process', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || 'Error al procesar el archivo');
        }

        displaySummary(data.summary);
    } catch (err) {
        showError(err.message || 'Ocurrió un error al procesar el documento. Por favor, intenta de nuevo.');
    } finally {
        hideLoading();
        processBtn.disabled = false;
    }
});

function showLoading() {
    loading.style.display = 'block';
}

function hideLoading() {
    loading.style.display = 'none';
}

function displaySummary(bullets) {
    summaryList.innerHTML = '';
    bullets.forEach(bullet => {
        const li = document.createElement('li');
        li.textContent = bullet;
        summaryList.appendChild(li);
    });
    summarySection.style.display = 'block';
}

function showError(message) {
    errorMessage.textContent = message;
    error.style.display = 'block';
}

function hideError() {
    error.style.display = 'none';
}

function hideSummary() {
    summarySection.style.display = 'none';
}


