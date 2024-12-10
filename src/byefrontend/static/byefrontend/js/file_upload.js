document.addEventListener('DOMContentLoaded', function() {
    // Find the first file upload wrapper on the page
    const widget = document.querySelector('.file-upload-wrapper');
    if (!widget) return;

    const config = JSON.parse(widget.getAttribute('data-config'));
    const dropZone = widget.querySelector('#drop-zone');
    const fileInput = widget.querySelector('#file-input');
    const messages = widget.querySelector('#messages');
    const toUploadList = widget.querySelector('#to-upload-list tbody');
    const uploadedList = widget.querySelector('#uploaded-list tbody');
    const uploadAllBtn = widget.querySelector('#upload-all-btn');

    const autoUpload = config.auto_upload;
    const uploadUrl = config.upload_url;
    const allowedTypes = config.filetypes_accepted;
    const fields = config.fields; // includes file_name and possibly more
    const csrfTokenElement = document.querySelector('[name=csrfmiddlewaretoken]');
    const csrftoken = csrfTokenElement ? csrfTokenElement.value : '';

    let pendingFiles = []; // store files when auto_upload = false

    // Drag & drop events
    dropZone.addEventListener('dragover', handleDragOver, false);
    dropZone.addEventListener('dragleave', handleDragLeave, false);
    dropZone.addEventListener('drop', handleFileDrop, false);

    // Click to select files
    dropZone.addEventListener('click', () => fileInput.click(), false);
    fileInput.addEventListener('change', handleFileSelect, false);

    if (uploadAllBtn) {
        uploadAllBtn.addEventListener('click', uploadAllFiles);
    }

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
        processSelectedFiles(files);
    }

    function handleFileSelect(evt) {
        const files = evt.target.files;
        processSelectedFiles(files);
    }

    function processSelectedFiles(files) {
        for (const file of files) {
            if (allowedTypes.length > 0 && !allowedTypes.includes(file.type)) {
                showMessage(`File type not allowed: ${file.type}`, true);
                continue;
            }
            if (autoUpload) {
                // Immediately upload
                const row = createToUploadRow(file, false);
                uploadFile(file, uploadUrl, row, true);
            } else {
                // Add to pending list
                const row = createToUploadRow(file, true);
                pendingFiles.push({file: file, row: row});
            }
        }
    }

    function createToUploadRow(file, editable) {
        const tr = document.createElement('tr');

        // Build columns based on fields
        // fields always have 'thumbnail' first, 'file_name' second.
        // Additional fields follow.
        // Thumbnail:
        const thumbnailTd = document.createElement('td');
        // If image, create a thumbnail
        if (file.type.startsWith('image/')) {
            const img = document.createElement('img');
            img.src = URL.createObjectURL(file);
            img.className = 'thumbnail';
            thumbnailTd.appendChild(img);
        } else {
            // generic icon
            const icon = document.createElement('span');
            icon.textContent = '📄'; // or use a more suitable icon
            thumbnailTd.appendChild(icon);
        }
        tr.appendChild(thumbnailTd);

        // For each other field:
        for (let i = 1; i < fields.length; i++) {
            const field = fields[i];
            if (!field.visible) continue;
            const td = document.createElement('td');
            let value = '';
            if (field.field_name === 'file_name') {
                value = file.name;
            }
            if (editable && field.editable) {
                const input = document.createElement('input');
                input.type = 'text';
                input.value = value;
                input.setAttribute('data-field', field.field_name);
                td.appendChild(input);
            } else {
                td.textContent = value;
            }
            tr.appendChild(td);
        }

        // Actions column
        const actionsTd = document.createElement('td');

        if (autoUpload) {
            // Cancel button if auto uploading
            const cancelButton = document.createElement('button');
            cancelButton.textContent = 'Cancel';
            cancelButton.addEventListener('click', () => {
                // Just remove from DOM and possibly abort upload if implemented
                tr.remove();
                showMessage(`Upload cancelled for "${file.name}"`);
            });
            actionsTd.appendChild(cancelButton);
        } else {
            // Remove button for pending files
            const removeButton = document.createElement('button');
            removeButton.textContent = 'Remove';
            removeButton.addEventListener('click', () => {
                tr.remove();
                // Remove from pendingFiles as well
                pendingFiles = pendingFiles.filter(pf => pf.file !== file);
            });
            actionsTd.appendChild(removeButton);
        }

        tr.appendChild(actionsTd);

        // Append to the "To Upload" list if auto_upload is False
        // If auto_upload is True, it's a temporary row. We could append it to to-upload
        // to show progress. Once done, we move it.
        toUploadList.appendChild(tr);

        return tr;
    }

    function showMessage(msg, error = false) {
        const div = document.createElement('div');
        div.className = error ? 'error' : 'message';
        div.textContent = msg;
        messages.appendChild(div);

        setTimeout(() => {
            if (div.parentNode) {
                div.parentNode.removeChild(div);
            }
        }, 5000);
    }

    function uploadAllFiles() {
        // Upload all pending files
        for (const pf of pendingFiles) {
            uploadFile(pf.file, uploadUrl, pf.row, false);
        }
        pendingFiles = [];
    }

    function collectFormDataFromRow(tr) {
        // For each editable field in the row, gather values
        const data = {};
        const inputs = tr.querySelectorAll('input[data-field]');
        inputs.forEach(input => {
            data[input.getAttribute('data-field')] = input.value;
        });
        return data;
    }

    function uploadFile(file, url, row, removeRowOnError = false) {
        const xhr = new XMLHttpRequest();
        const formData = new FormData();
        formData.append('file', file);

        // If auto_upload=false, also append metadata fields
        if (!autoUpload) {
            const metaData = collectFormDataFromRow(row);
            // Add metadata to formData
            for (const key in metaData) {
                formData.append(key, metaData[key]);
            }
        }

        xhr.open('POST', url, true);
        if (csrftoken) {
            xhr.setRequestHeader('X-CSRFToken', csrftoken);
        }
        xhr.timeout = 30000; // 30s timeout

        // Add a progress column if desired
        let progressBar = null;
        // Insert progress bar into actions cell if needed
        if (autoUpload) {
            const actionsTd = row.querySelector('td:last-child');
            progressBar = document.createElement('progress');
            progressBar.value = 0;
            progressBar.max = 100;
            actionsTd.insertBefore(progressBar, actionsTd.firstChild);
        } else {
            // If not auto upload, we can add a progress bar too if we want
            const actionsTd = row.querySelector('td:last-child');
            progressBar = document.createElement('progress');
            progressBar.value = 0;
            progressBar.max = 100;
            actionsTd.insertBefore(progressBar, actionsTd.firstChild);
        }

        xhr.upload.addEventListener('progress', function(e) {
            if (e.lengthComputable && progressBar) {
                const percentComplete = (e.loaded / e.total) * 100;
                progressBar.value = percentComplete;
            }
        }, false);

        xhr.addEventListener('load', function(e) {
            console.log("Raw server response:", xhr.responseText);
            try {
                const response = JSON.parse(xhr.responseText);
                if (xhr.status === 200 && response.status === 'success') {
                    showMessage(`File "${file.name}" uploaded successfully.`);
                    moveRowToUploaded(row, response.filepath || '');
                } else {
                    showMessage(`Upload error: ${response.message || 'Unknown error'}`, true);
                    if (removeRowOnError) row.remove();
                }
            } catch (err) {
                console.error("Error parsing JSON response:", err, xhr.responseText);
                showMessage('Invalid JSON response from server.', true);
                if (removeRowOnError) row.remove();
            }
        }, false);

        xhr.addEventListener('error', function(e) {
            showMessage(`Upload error: ${xhr.status}`, true);
            if (removeRowOnError) row.remove();
        }, false);

        xhr.addEventListener('timeout', function(e) {
            showMessage('Upload timed out.', true);
            xhr.abort();
            if (removeRowOnError) row.remove();
        }, false);

        xhr.send(formData);
    }

    function moveRowToUploaded(row, filepath) {
        // Move row from toUploadList to uploadedList
        // Remove metadata inputs and progress bars, show final filepath
        const toUploadTbody = row.parentNode;
        if (toUploadTbody === toUploadList) {
            // Remove actions except maybe a delete button
            // Clear progress bar and editable fields
            const inputs = row.querySelectorAll('input[data-field]');
            inputs.forEach(input => {
                const td = input.parentNode;
                td.textContent = input.value;
            });

            const actionsTd = row.querySelector('td:last-child');
            // Clear old actions
            actionsTd.innerHTML = '';

            // Add a filepath column before the last (which is actions)
            // Since uploaded table has one extra column "Filepath", we must insert that
            const filepathTd = document.createElement('td');
            filepathTd.textContent = filepath;
            // We know that original structure had fields + actions
            // Insert filepath td before actionsTd
            row.insertBefore(filepathTd, actionsTd);

            // Add a delete button if you want to allow removing uploaded files from the UI
            const deleteButton = document.createElement('button');
            deleteButton.textContent = 'Delete';
            deleteButton.addEventListener('click', () => {
                row.remove();
            });
            actionsTd.appendChild(deleteButton);

            uploadedList.appendChild(row);
        }
    }

});
