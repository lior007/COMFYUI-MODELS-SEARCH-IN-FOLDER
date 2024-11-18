let lastSearchTerm = '';
let isSearching = false;

document.getElementById('searchInput').addEventListener('input', debounce(handleSearch, 300));

document.getElementById('searchInput').addEventListener('keypress', function(e) {
    if (e.key === 'Enter') {
        handleSearch();
    }
});

document.getElementById('basePath').addEventListener('keypress', function(e) {
    if (e.key === 'Enter') {
        handleSearch();
    }
});

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

function showLoading(show) {
    const loader = document.getElementById('loadingIndicator');
    const button = document.getElementById('searchButton');
    loader.style.display = show ? 'block' : 'none';
    button.disabled = show;
    isSearching = show;
}

function showError(message) {
    const errorDiv = document.getElementById('errorMessage');
    errorDiv.textContent = message;
    errorDiv.style.display = 'block';
    setTimeout(() => {
        errorDiv.style.display = 'none';
    }, 5000);
}

function showSuccess(message) {
    const successDiv = document.getElementById('successMessage');
    successDiv.textContent = message;
    successDiv.style.display = 'block';
    setTimeout(() => {
        successDiv.style.display = 'none';
    }, 3000);
}

// handleSearch
async function handleSearch() {
    if (isSearching) return;

    const basePath = document.getElementById('basePath').value;
    const searchTerm = document.getElementById('searchInput').value;

    if (!basePath) {
        showError('Please enter a path to scan');
        return;
    }

    lastSearchTerm = searchTerm;
    showLoading(true);

    try {
        console.log('Sending scan request for path:', basePath);
        const response = await fetch('http://localhost:3000/scan', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ path: basePath })
        });

        console.log('Received response:', response);
        if (!response.ok) {
            throw new Error(`Scan error: ${response.statusText}`);
        }

        const data = await response.json();
        console.log('Parsed response data:', data);
        
        if (data.error) {
            throw new Error(data.error);
        }

        displayResults(data.files || [], searchTerm);

    } catch (error) {
        console.error('Error in handleSearch:', error);
        showError(error.message);
        document.getElementById('results').innerHTML = '';
    } finally {
        showLoading(false);
    }
}

function getFileTypeInfo(filename) {
    const ext = filename.split('.').pop().toLowerCase();
    const types = {
        'ckpt': { name: 'Checkpoint', color: '#4a90e2' },
        'safetensors': { name: 'SafeTensors', color: '#28a745' },
		'sft': { name: 'SafeTensors', color: '#28a745' },
        'pt': { name: 'LoRA/TI', color: '#dc3545' },
        'bin': { name: 'Binary', color: '#6c757d' },
        'yaml': { name: 'Config', color: '#ffc107' },
		'gguf': { name: 'Stable Diffusion Model', color: '#4169E1' },
        'vae': { name: 'VAE', color: '#17a2b8' }
    };
    return types[ext] || { name: 'other', color: '#6c757d' };
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleString('he-IL', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
    });
}

function highlightText(text, searchTerm) {
    if (!searchTerm) return text;
    const regex = new RegExp(`(${searchTerm})`, 'gi');
    return text.replace(regex, '<span class="highlight">$1</span>');
}

function toggleFolder(element) {
    const content = element.nextElementSibling;
    const isVisible = content.style.display === 'block';
    content.style.display = isVisible ? 'none' : 'block';
    
    const arrow = element.querySelector('.folder-arrow');
    arrow.textContent = isVisible ? '▼' : '▲';
}

function toggleFileDetails(element) {
    const details = element.querySelector('.file-details');
    details.style.display = details.style.display === 'block' ? 'none' : 'block';
}

function displayResults(files, searchTerm) {
    console.log('Displaying results:', files); // Log for testing
    const resultsDiv = document.getElementById('results');
    resultsDiv.innerHTML = '';

    if (!files || files.length === 0) {
        resultsDiv.innerHTML = '<div class="error-message">No files found</div>';
        return;
    }

    // Sort files by folders
    const filesByFolder = {};
    files.forEach(file => {
        console.log('Processing file:', file); // Log for testing
        if (!searchTerm || file.name.toLowerCase().includes(searchTerm.toLowerCase())) {
            const folder = file.path.substring(0, file.path.lastIndexOf('\\'));
            if (!filesByFolder[folder]) {
                filesByFolder[folder] = [];
            }
            filesByFolder[folder].push(file);
        }
    });

    console.log('Files by folder:', filesByFolder); // Log for testing

    Object.entries(filesByFolder).forEach(([folder, folderFiles]) => {
        const folderDiv = document.createElement('div');
        folderDiv.className = 'folder';

        const folderHeader = document.createElement('div');
        folderHeader.className = 'folder-header';
        folderHeader.innerHTML = `
            <span>${folder}</span>
            <span>
                <span class="file-count">${folderFiles.length} files</span>
                <span class="folder-arrow">▼</span>
            </span>
        `;
        folderHeader.onclick = () => toggleFolder(folderHeader);

        const folderContent = document.createElement('div');
        folderContent.className = 'folder-content';
        folderContent.style.display = 'block'; // Open by default

        folderFiles.forEach(file => {
            const fileDiv = document.createElement('div');
            fileDiv.className = 'file';
            const fileType = getFileTypeInfo(file.name);
            
            fileDiv.innerHTML = `
                <div>
                    <span class="file-type" style="background-color: ${fileType.color}; color: white;">
                        ${fileType.name}
                    </span>
                    ${highlightText(file.name, searchTerm)}
                </div>
                <div class="file-details">
                    <div class="path-display">נתיב: ${file.path}</div>
                    <div>גודל: ${formatFileSize(file.size)}</div>
                    <div>תאריך עדכון: ${formatDate(file.modified)}</div>
                </div>
            `;
            fileDiv.onclick = () => toggleFileDetails(fileDiv);
            folderContent.appendChild(fileDiv);
        });

        folderDiv.appendChild(folderHeader);
        folderDiv.appendChild(folderContent);
        resultsDiv.appendChild(folderDiv);
    });
}

async function clearCache() {
    try {
        const response = await fetch('http://localhost:3000/cache/clear', {
            method: 'POST'
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showSuccess(data.message || 'The cache has been cleared successfully');
        } else {
            throw new Error(data.error || 'Error clearing the cache');
        }
    } catch (error) {
        showError(error.message);
    }
}

function updateStats(data) {
    const statsInfo = document.getElementById('statsInfo');
    const fromCache = data.from_cache ? 'from the cache' : 'New scan';
    statsInfo.textContent = `Scan time: ${data.scan_time} seconds source: ${fromCache}`;
}
