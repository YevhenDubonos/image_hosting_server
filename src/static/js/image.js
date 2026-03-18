document.addEventListener('DOMContentLoaded', function () {
    document.addEventListener('keydown', function (event) {
        if (event.key === 'F5' || event.key === 'Escape') {
            event.preventDefault();
            window.location.href = '/upload';
        }
    });

    const fileListWrapper = document.getElementById('file-list-wrapper');
    const uploadRedirectButton = document.getElementById('upload-tab-btn');

    if (uploadRedirectButton) {
        uploadRedirectButton.addEventListener('click', () => window.location.href = '/upload');
    }

    const displayFiles = () => {
        const storedFiles = JSON.parse(localStorage.getItem('uploadedImages')) || [];
        fileListWrapper.innerHTML = '';

        if (storedFiles.length === 0) {
            fileListWrapper.innerHTML = '<p class="upload__promt" style="text-align: center; margin-top: 50px;">No images uploaded yet.</p>';
            return;
        }

        const container = document.createElement('div');
        container.className = 'file-list-container';

        const header = document.createElement('div');
        header.className = 'file-list-header';
        header.innerHTML = `
            <div class="file-col file-col-name">Name</div>
            <div class="file-col file-col-url">Url</div>
            <div class="file-col file-col-delete">Delete</div>
        `;
        container.appendChild(header);

        const list = document.createElement('div');
        list.id = 'file-list';

        storedFiles.forEach((fileData, index) => {
            const fileItem = document.createElement('div');
            fileItem.className = 'file-list-item';
            fileItem.innerHTML = `
                <div class="file-col file-col-name">
                    <span class="file-icon"><img src="/static/img/group.png" alt="file icon"></span>
                    ${fileData.url ? `<img src="${fileData.url}" alt="thumbnail">` : ''}
                    <span class="file-name" title="${fileData.originalName || fileData.displayName || fileData.name}">${fileData.displayName || fileData.name}</span>
                </div>
                <div class="file-col file-col-url">https://group6-image-hosting-server.com/${fileData.name}</div>
                <div class="file-col file-col-delete">
                    <button class="delete-btn" data-index="${index}"><img src="/static/img/delete.png" alt="delete icon"></button>
                </div>
            `;
            list.appendChild(fileItem);
        });

        container.appendChild(list);
        fileListWrapper.appendChild(container);
        addDeleteListeners();
    };

    const addDeleteListeners = () => {
        document.querySelectorAll('.delete-btn').forEach(button => {
            button.addEventListener('click', async (event) => {
                const indexToDelete = parseInt(event.currentTarget.dataset.index);
                let storedFiles = JSON.parse(localStorage.getItem('uploadedImages')) || [];
                const fileToDelete = storedFiles[indexToDelete];

                if (fileToDelete && fileToDelete.name) {
                    try {
                        const imagesResponse = await fetch('/api/images');
                        const imagesResult = await imagesResponse.json();

                        if (imagesResult.success) {
                            const imageRecord = imagesResult.images.find(img => img.filename === fileToDelete.name);

                            if (imageRecord) {
                                const deleteResponse = await fetch(`/api/images/${imageRecord.id}`, {
                                    method: 'DELETE'
                                });

                                const deleteResult = await deleteResponse.json();

                                if (deleteResult.success) {
                                    console.log('File deleted from server:', fileToDelete.name);
                                } else {
                                    console.error('Failed to delete file from server:', deleteResult.message);
                                }
                            }
                        }
                    } catch (error) {
                        console.error('Error deleting file:', error);
                    }
                }

                storedFiles.splice(indexToDelete, 1);
                localStorage.setItem('uploadedImages', JSON.stringify(storedFiles));
                displayFiles();
            });
        });
    };

    displayFiles();
});
