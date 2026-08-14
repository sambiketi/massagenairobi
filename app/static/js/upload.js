// Upload Service JavaScript
// Handles image uploads with preview and drag & drop

document.addEventListener('DOMContentLoaded', function() {
    // Initialize all upload handlers
    initUploadHandlers();
});

function initUploadHandlers() {
    // File input change handlers
    document.querySelectorAll('input[type="file"][data-preview]').forEach(function(input) {
        input.addEventListener('change', function(e) {
            const previewId = this.dataset.preview;
            previewFile(this, previewId);
        });
    });

    // Drag and drop handlers
    document.querySelectorAll('.drop-zone').forEach(function(zone) {
        zone.addEventListener('dragover', function(e) {
            e.preventDefault();
            this.classList.add('dragover');
        });

        zone.addEventListener('dragleave', function(e) {
            e.preventDefault();
            this.classList.remove('dragover');
        });

        zone.addEventListener('drop', function(e) {
            e.preventDefault();
            this.classList.remove('dragover');
            const files = e.dataTransfer.files;
            const input = this.querySelector('input[type="file"]');
            if (input && files.length) {
                input.files = files;
                input.dispatchEvent(new Event('change'));
            }
        });
    });
}

// Preview a single image file
function previewFile(input, previewElementId) {
    if (input.files && input.files[0]) {
        const reader = new FileReader();
        reader.onload = function(e) {
            const preview = document.getElementById(previewElementId);
            if (preview) {
                preview.src = e.target.result;
                preview.classList.remove('hidden');
            }
        };
        reader.readAsDataURL(input.files[0]);
    }
}

// Preview multiple image files
function previewMultipleFiles(input, containerId) {
    const container = document.getElementById(containerId);
    if (!container) return;

    container.innerHTML = '';
    
    for (let i = 0; i < input.files.length; i++) {
        const file = input.files[i];
        const reader = new FileReader();
        
        reader.onload = function(e) {
            const div = document.createElement('div');
            div.className = 'upload-preview-item';
            
            const img = document.createElement('img');
            img.src = e.target.result;
            img.alt = file.name;
            
            const removeBtn = document.createElement('button');
            removeBtn.className = 'remove-btn';
            removeBtn.innerHTML = '<i class="fas fa-times"></i>';
            removeBtn.type = 'button';
            removeBtn.onclick = function() {
                div.remove();
            };
            
            div.appendChild(img);
            div.appendChild(removeBtn);
            container.appendChild(div);
        };
        
        reader.readAsDataURL(file);
    }
}

// Upload file to server with progress
function uploadFile(file, url, onProgress, onComplete, onError) {
    const formData = new FormData();
    formData.append('file', file);
    
    const xhr = new XMLHttpRequest();
    
    xhr.upload.addEventListener('progress', function(e) {
        if (e.lengthComputable && onProgress) {
            const percent = Math.round((e.loaded / e.total) * 100);
            onProgress(percent);
        }
    });
    
    xhr.addEventListener('load', function() {
        if (xhr.status === 200) {
            try {
                const result = JSON.parse(xhr.responseText);
                if (onComplete) onComplete(result);
            } catch (e) {
                if (onError) onError('Invalid response from server');
            }
        } else {
            if (onError) onError('Upload failed: ' + xhr.status);
        }
    });
    
    xhr.addEventListener('error', function() {
        if (onError) onError('Network error occurred');
    });
    
    xhr.open('POST', url);
    xhr.send(formData);
}

// Bulk upload multiple files
function uploadMultipleFiles(files, url, onFileComplete, onAllComplete) {
    let completed = 0;
    let total = files.length;
    
    for (let i = 0; i < files.length; i++) {
        const file = files[i];
        uploadFile(file, url, 
            function(percent) {
                // Progress callback per file
                console.log('Uploading ' + file.name + ': ' + percent + '%');
            },
            function(result) {
                completed++;
                if (onFileComplete) onFileComplete(result, file);
                if (completed === total && onAllComplete) {
                    onAllComplete();
                }
            },
            function(error) {
                console.error('Error uploading ' + file.name + ':', error);
                completed++;
                if (completed === total && onAllComplete) {
                    onAllComplete();
                }
            }
        );
    }
}

// Validate file before upload
function validateFile(file, allowedTypes, maxSize) {
    if (allowedTypes && !allowedTypes.includes(file.type)) {
        return { valid: false, error: 'File type not allowed. Allowed: ' + allowedTypes.join(', ') };
    }
    
    if (maxSize && file.size > maxSize) {
        const maxMB = Math.round(maxSize / (1024 * 1024));
        const fileMB = Math.round(file.size / (1024 * 1024));
        return { valid: false, error: 'File too large. Max: ' + maxMB + 'MB, Your file: ' + fileMB + 'MB' };
    }
    
    return { valid: true };
}

// Export functions for use in other scripts
window.uploadFile = uploadFile;
window.uploadMultipleFiles = uploadMultipleFiles;
window.validateFile = validateFile;
window.previewFile = previewFile;
window.previewMultipleFiles = previewMultipleFiles;
