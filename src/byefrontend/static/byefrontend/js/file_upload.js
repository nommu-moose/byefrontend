document.addEventListener('DOMContentLoaded', function() {
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
    const fields = config.fields; // includes thumbnail, file_name, file_path, actions, etc.
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
                const row = createToUploadRow(file);
                uploadFile(file, uploadUrl, row, true);
            } else {
                // Add to pending list
                const row = createToUploadRow(file);
                pendingFiles.push({file: file, row: row});
            }
        }
    }

    function createToUploadRow(file) {
        const tr = document.createElement('tr');
        fields.forEach((field) => {
            if (!field.visible) return;
            const td = document.createElement('td');

            switch (field.field_type) {
                case 'img':
                    // Thumbnail
                    if (file.type.startsWith('image/')) {
                        const img = document.createElement('img');
                        img.src = URL.createObjectURL(file);
                        img.className = 'thumbnail';
                        td.appendChild(img);
                    } else {
                        // generic icon
                        const icon = document.createElement('span');
                        icon.textContent = '📄';
                        td.appendChild(icon);
                    }
                    break;

                case 'text':
                    // For text fields, decide value based on field_name
                    let value = '';
                    if (field.field_name === 'file_name') {
                        // Default to the actual file's name
                        value = file.name;
                        // Make it editable if allowed and if auto_upload is false
                        if (!autoUpload && field.editable) {
                            const input = document.createElement('input');
                            input.type = 'text';
                            input.value = value;
                            input.setAttribute('data-field', field.field_name);
                            td.appendChild(input);
                        } else {
                            td.textContent = value;
                        }
                    } else if (field.field_name === 'file_path') {
                        // Since browsers do not reveal the real full path, we show the name
                        // It's often "C:\fakepath\<filename>" in some browsers, or just the file name.
                        // file.name is what we have. We set this non-editable by `editable:false`.
                        td.textContent = file.name;
                    } else {
                        // If you had other text fields, you'd handle them similarly.
                        // Since we removed description and tags, there's nothing extra here.
                    }
                    break;

                case 'actions':
                    // Actions field (upload all button, remove button, etc.)
                    if (autoUpload) {
                        const cancelButton = document.createElement('button');
                        cancelButton.textContent = 'Cancel';
                        cancelButton.addEventListener('click', () => {
                            tr.remove();
                            showMessage(`Upload cancelled for "${file.name}"`);
                        });
                        td.appendChild(cancelButton);
                    } else {
                        const removeButton = document.createElement('button');
                        removeButton.textContent = 'Remove';
                        removeButton.addEventListener('click', () => {
                            tr.remove();
                            pendingFiles = pendingFiles.filter(pf => pf.file !== file);
                        });
                        td.appendChild(removeButton);
                    }
                    break;

                default:
                    // If a field_type isn't recognized, just leave blank or
                    // show its field_name as text.
                    // But ideally, all fields have known field_type.
                    td.textContent = '';
                    break;
            }

            tr.appendChild(td);
        });

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
            for (const key in metaData) {
                formData.append(key, metaData[key]);
            }
        }

        xhr.open('POST', url, true);
        if (csrftoken) {
            xhr.setRequestHeader('X-CSRFToken', csrftoken);
        }
        xhr.timeout = 30000; // 30s timeout

        // Insert a progress bar in the actions cell
        const actionsField = fields.find(f => f.field_type === 'actions');
        let progressBar = null;
        if (actionsField) {
            const actionsTd = getCellByField(row, 'actions');
            if (actionsTd) {
                progressBar = document.createElement('progress');
                progressBar.value = 0;
                progressBar.max = 100;
                actionsTd.insertBefore(progressBar, actionsTd.firstChild);
            }
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
                    moveRowToUploaded(row, response);
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

    function moveRowToUploaded(row, responseData) {
        // After upload, we mark the row as uploaded.
        // Update fields: remove inputs, set text to final values if provided by server
        // Remove progress bar, adjust actions

        // Convert editable fields to text:
        fields.forEach(field => {
            if (!field.visible) return;
            const td = getCellByField(row, field.field_name);
            if (!td) return;

            // If we had an input, remove it and set text:
            const input = td.querySelector('input[data-field]');
            if (input) {
                td.textContent = input.value;
            }

            // If server returned updated values for these fields (like filepath), update them
            if (responseData[field.field_name] !== undefined) {
                if (field.field_type === 'text') {
                    td.textContent = responseData[field.field_name];
                }
                // For images or other field types, you could also handle updates as needed.
                // For now, assuming server might return a final filepath or filename.
            }

            if (field.field_name === 'actions') {
                // Clear old actions (like remove button or cancel button)
                // and show a final "Delete" button or whatever is appropriate for uploaded files.
                td.innerHTML = '';
                const deleteButton = document.createElement('button');
                deleteButton.textContent = 'Delete';
                deleteButton.addEventListener('click', () => {
                    row.remove();
                });
                td.appendChild(deleteButton);
            }
        });

        // Move to the uploadedList
        uploadedList.appendChild(row);
    }

    function getCellByField(row, fieldName) {
        // Returns the cell (td) corresponding to a given field_name
        // We rely on the order fields were appended. Each visible field corresponds
        // to one cell in the same order.
        const visibleFields = fields.filter(f => f.visible);
        const index = visibleFields.findIndex(f => f.field_name === fieldName);
        if (index === -1) return null;
        return row.children[index] || null;
    }

});
