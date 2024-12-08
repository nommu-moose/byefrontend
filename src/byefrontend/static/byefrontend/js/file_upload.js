document.addEventListener('DOMContentLoaded', function() {
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('file-input');
    const messages = document.getElementById('messages');
    const uploadList = document.getElementById('upload-list');

    // Get CSRF token from the rendered template (from the csrf_token tag)
    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    // Handle dragover and dragleave
    dropZone.addEventListener('dragover', handleDragOver, false);
    dropZone.addEventListener('dragleave', handleDragLeave, false);
    dropZone.addEventListener('drop', handleFileDrop, false);

    // Handle click to trigger file selection
    dropZone.addEventListener('click', () => fileInput.click(), false);

    // Handle file selection via file input
    fileInput.addEventListener('change', handleFileSelect, false);

    function handleDragOver(evt) {
        evt.preventDefault();
        evt.stopPropagation();
        dropZone.classList.add('hover');
    }

    function handleDragLeave(evt) {
        evt.preventDefault();
        evt.stopPropagation();
        dropZone.classList.remove('hover');
    }

    function handleFileDrop(evt) {
        evt.preventDefault();
        evt.stopPropagation();
        dropZone.classList.remove('hover');
        const files = evt.dataTransfer.files;
        uploadFiles(files);
    }

    function handleFileSelect(evt) {
        const files = evt.target.files;
        uploadFiles(files);
    }

    function uploadFiles(files) {
        for (const file of files) {
            const uploadElement = createUploadElement(file);
            uploadFile(file, uploadUrl, uploadElement);
        }
    }

    function createUploadElement(file) {
        const uploadItem = document.createElement('div');
        uploadItem.className = 'upload-item';

        const fileName = document.createElement('span');
        fileName.textContent = file.name;

        const progressBar = document.createElement('progress');
        progressBar.value = 0;
        progressBar.max = 100;

        const cancelButton = document.createElement('button');
        cancelButton.textContent = 'Cancel';

        uploadItem.appendChild(fileName);
        uploadItem.appendChild(progressBar);
        uploadItem.appendChild(cancelButton);

        uploadList.appendChild(uploadItem);

        return {
            uploadItem: uploadItem,
            progressBar: progressBar,
            cancelButton: cancelButton
        };
    }

    function showMessage(msg, error = false) {
        const div = document.createElement('div');
        div.className = error ? 'error' : 'message';
        div.textContent = msg;
        messages.appendChild(div);

        // Clear after a timeout if you want
        setTimeout(() => {
            messages.removeChild(div);
        }, 5000);
    }

    function uploadFile(file, url, uploadElement) {
        const xhr = new XMLHttpRequest();
        const formData = new FormData();
        formData.append('file', file);

        xhr.open('POST', url, true);

        // Set CSRF token header
        xhr.setRequestHeader('X-CSRFToken', csrftoken);

        // Set up timeout (e.g., 30 seconds)
        xhr.timeout = 30000; // in milliseconds

        xhr.upload.addEventListener('progress', function(e) {
            if (e.lengthComputable) {
                const percentComplete = (e.loaded / e.total) * 100;
                uploadElement.progressBar.value = percentComplete;
            }
        }, false);

        xhr.addEventListener('load', function(e) {
            // Log the raw response to debug
            console.log("Raw server response:", xhr.responseText);

            try {
                const response = JSON.parse(xhr.responseText);
                if (xhr.status === 200) {
                    showMessage(`File "${file.name}" uploaded successfully.`);
                } else {
                    showMessage(`Upload error: ${response.message || 'Unknown error'}`, true);
                }
            } catch (err) {
                console.error("Error parsing JSON response:", err, xhr.responseText);
                showMessage('Invalid JSON response from server.', true);
            }

            uploadElement.uploadItem.remove();
        }, false);

        xhr.addEventListener('error', function(e) {
            showMessage(`Upload error: ${xhr.status}`, true);
            uploadElement.uploadItem.remove();
        }, false);

        xhr.addEventListener('timeout', function(e) {
            showMessage('Upload timed out.', true);
            xhr.abort();
            uploadElement.uploadItem.remove();
        }, false);

        uploadElement.cancelButton.addEventListener('click', function() {
            xhr.abort();
            uploadElement.uploadItem.remove();
            showMessage(`Upload cancelled for "${file.name}"`);
        });

        xhr.send(formData);
}

});