const API_URL = 'http://127.0.0.1:8000';

document.addEventListener('DOMContentLoaded', () => {
    loadDocuments();

    const uploadForm = document.getElementById('uploadForm');
    uploadForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        const submitBtn = document.getElementById('submitBtn');
        const originalBtnText = submitBtn.innerText;
        submitBtn.innerText = 'Uploading...';
        submitBtn.disabled = true;

        const formData = new FormData();
        formData.append('sub_category', document.getElementById('sub_category').value);
        formData.append('year', document.getElementById('year').value);
        formData.append('month', document.getElementById('month').value);
        formData.append('issue_date', document.getElementById('issue_date').value);
        formData.append('title', document.getElementById('title').value);
        formData.append('file', document.getElementById('file').files[0]);

        try {
            const response = await fetch(`${API_URL}/upload/`, {
                method: 'POST',
                body: formData
            });

            if (response.ok) {
                alert('Document uploaded successfully!');
                uploadForm.reset();
                loadDocuments();
            } else {
                const errorData = await response.json();
                alert(`Upload failed: ${errorData.detail}`);
            }
        } catch (error) {
            console.error('Error uploading document:', error);
            alert('An error occurred during upload.');
        } finally {
            submitBtn.innerText = originalBtnText;
            submitBtn.disabled = false;
        }
    });

    // Auto-fill Year and Month from Issue Date
    const issueDateInput = document.getElementById('issue_date');
    const yearInput = document.getElementById('year');
    const monthSelect = document.getElementById('month');

    issueDateInput.addEventListener('change', (e) => {
        const dateVal = e.target.value;
        if (dateVal) {
            const date = new Date(dateVal);
            yearInput.value = date.getFullYear();

            const monthNames = [
                "January", "February", "March", "April", "May", "June",
                "July", "August", "September", "October", "November", "December"
            ];
            monthSelect.value = monthNames[date.getMonth()];
        }
    });
});

async function loadDocuments() {
    const documentList = document.getElementById('documentList');
    documentList.className = 'document-grid';
    documentList.innerHTML = '<p style="text-align: center; width: 100%; opacity: 0.5;">Syncing documents...</p>';

    try {
        const response = await fetch(`${API_URL}/documents/`);
        const documents = await response.json();

        if (documents.length === 0) {
            documentList.innerHTML = '<p style="text-align: center; width: 100%; opacity: 0.5;">No documents found.</p>';
            return;
        }

        documentList.innerHTML = '';
        documents.forEach(doc => {
            const card = document.createElement('div');
            card.className = 'doc-card';

            const subCategoryClass = doc.sub_category.toLowerCase().replace(/\s+/g, '-');

            card.innerHTML = `
                <span class="tag ${subCategoryClass}">${doc.sub_category}</span>
                <div class="doc-header-info">
                    <span class="vertical-tag">MCA</span>
                    <span class="date-tag">${doc.month} ${doc.year}</span>
                </div>
                <h3>${doc.title}</h3>
                <div class="doc-info">
                    <div><span>Issue Date</span> <span>${doc.issue_date}</span></div>
                    <div><span>File Name</span> <span class="file-name-truncate" title="${doc.file_name}">${doc.file_name}</span></div>
                    <div><span>Path</span> <span class="file-path-truncate" title="${doc.path}">${doc.path}</span></div>
                </div>
                <div class="card-actions">
                    <button class="btn-small btn-ghost" onclick="window.open('${doc.pdf_url}', '_blank')">View PDF</button>
                    <button class="btn-small btn-danger" onclick="deleteDocument(${doc.id})">Delete</button>
                </div>
            `;
            documentList.appendChild(card);
        });
    } catch (error) {
        console.error('Error loading documents:', error);
        documentList.innerHTML = '<p style="text-align: center; width: 100%; color: #ef4444;">Failed to load documents.</p>';
    }
}

async function deleteDocument(id) {
    if (!confirm('Are you sure you want to delete this document?')) return;

    try {
        const response = await fetch(`${API_URL}/documents/${id}`, {
            method: 'DELETE'
        });

        if (response.ok) {
            loadDocuments();
        } else {
            alert('Failed to delete document.');
        }
    } catch (error) {
        console.error('Error deleting document:', error);
    }
}
