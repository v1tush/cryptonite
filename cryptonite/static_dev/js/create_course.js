document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('course-form');
    const availableCiphers = document.getElementById('available-ciphers');
    const selectedCiphers = document.getElementById('selected-ciphers');
    const selectedCount = document.getElementById('selected-count');
    const clearBtn = document.getElementById('clear-selection');
    const cipherIdsInput = document.getElementById('cipher-ids');
    const emptyDropMessage = selectedCiphers.querySelector('.empty-drop-message');
    const createCourseBtn = document.getElementById('create-course-btn');

    let selectedCipherIds = [];
    let selectedCipherTitles = {};

    function loadSavedCiphers() {
        try {
            const savedData = cipherIdsInput.value || '[]';
            const savedIds = JSON.parse(savedData);
            
            if (savedIds && savedIds.length > 0) {
                savedIds.forEach(cipherId => {
                    const cipherElement = availableCiphers.querySelector(`[data-cipher-id="${cipherId}"]`);
                    if (cipherElement) {
                        addCipherToSelected(cipherElement);
                    }
                });
            }
        } catch (e) {
            console.error(e);
        }
    }

    loadSavedCiphers();
    function updateSelection() {
        selectedCount.textContent = selectedCipherIds.length;
        cipherIdsInput.value = JSON.stringify(selectedCipherIds);
        
        if (selectedCipherIds.length > 0) {
            emptyDropMessage.classList.add('hidden');
        } else {
            emptyDropMessage.classList.remove('hidden');
        }
    }

    function addCipherToSelected(cipherElement) {
        const cipherId = parseInt(cipherElement.dataset.cipherId);
        const cipherTitle = cipherElement.dataset.cipherTitle;
        const cipherDifficulty = cipherElement.dataset.cipherDifficulty;
        
        if (!selectedCipherIds.includes(cipherId)) {
            selectedCipherIds.push(cipherId);
            selectedCipherTitles[cipherId] = cipherTitle;
            const cipherItem = document.createElement('div');
            cipherItem.className = 'cipher-item selected';
            cipherItem.dataset.cipherId = cipherId;
            let difficultyClass = 'medium';
            let difficultyText = 'Средний';
            switch(parseInt(cipherDifficulty)) {
                case 1:
                    difficultyClass = 'easy';
                    difficultyText = 'Легкий';
                    break;
                case 2:
                    difficultyClass = 'medium';
                    difficultyText = 'Средний';
                    break;
                case 3:
                    difficultyClass = 'hard';
                    difficultyText = 'Сложный';
                    break;
                default:
                    difficultyClass = 'hardcore';
                    difficultyText = 'Очень сложный';
            }
            cipherItem.innerHTML = `
                <div class="cipher-item-content">
                    <span class="cipher-title">${cipherTitle}</span>
                    <span class="difficulty ${difficultyClass}">
                        ${difficultyText}
                    </span>
                </div>
                <span class="remove-btn">×</span>
            `;
            const removeBtn = cipherItem.querySelector('.remove-btn');
            removeBtn.addEventListener('click', function(e) {
                e.stopPropagation();
                removeCipherFromSelected(cipherItem, cipherId);
            });
            
            selectedCiphers.appendChild(cipherItem);
            updateSelection();
        }
    }
    function removeCipherFromSelected(element, cipherId) {
        element.remove();
        selectedCipherIds = selectedCipherIds.filter(id => id !== cipherId);
        delete selectedCipherTitles[cipherId];
        updateSelection();
    }
    clearBtn.addEventListener('click', function() {
        selectedCiphers.querySelectorAll('.cipher-item.selected').forEach(item => {
            item.remove();
        });
        selectedCipherIds = [];
        selectedCipherTitles = {};
        updateSelection();
    });

    let draggedItem = null;
    availableCiphers.querySelectorAll('.draggable').forEach(item => {
        item.addEventListener('dragstart', function(e) {
            draggedItem = this;
            this.classList.add('dragging');
            e.dataTransfer.setData('text/plain', this.dataset.cipherId);
            e.dataTransfer.effectAllowed = 'move';
        });

        item.addEventListener('dragend', function() {
            this.classList.remove('dragging');
            draggedItem = null;
        });
    });
    selectedCiphers.addEventListener('dragover', function(e) {
        e.preventDefault();
        this.classList.add('drag-over');
        e.dataTransfer.dropEffect = 'move';
    });

    selectedCiphers.addEventListener('dragleave', function() {
        this.classList.remove('drag-over');
    });

    selectedCiphers.addEventListener('drop', function(e) {
        e.preventDefault();
        this.classList.remove('drag-over');
        
        if (draggedItem) {
            addCipherToSelected(draggedItem);
        }
    });
    availableCiphers.addEventListener('click', function(e) {
        const cipherItem = e.target.closest('.draggable');
        if (cipherItem && !e.target.classList.contains('drag-handle')) {
            addCipherToSelected(cipherItem);
        }
    });
    form.addEventListener('submit', function(e) {
        clearErrors();
        
        const title = document.getElementById('title').value.trim();
        const description = document.getElementById('description').value.trim();
        let hasErrors = false;
        if (!title) {
            showError('title', 'Введите название курса');
            hasErrors = true;
        } else if (title.length < 5) {
            showError('title', 'Название должно содержать минимум 5 символов');
            hasErrors = true;
        } else if (title.length > 200) {
            showError('title', 'Название не должно превышать 200 символов');
            hasErrors = true;
        }
        if (!description) {
            showError('description', 'Введите описание курса');
            hasErrors = true;
        } else if (description.length < 100) {
            showError('description', 'Описание должно содержать минимум 100 символов');
            hasErrors = true;
        }
        if (selectedCipherIds.length < 2) {
            showError('cipher_ids', 'Выберите минимум 2 шифра для курса');
            hasErrors = true;
        }
        
        if (hasErrors) {
            e.preventDefault();
            const firstError = document.querySelector('.error-field');
            if (firstError) {
                firstError.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }
            createCourseBtn.disabled = true;
            createCourseBtn.textContent = 'Исправьте ошибки...';
            setTimeout(() => {
                createCourseBtn.disabled = false;
                createCourseBtn.textContent = 'Создать курс';
            }, 2000);
        }
    });
    function showError(fieldName, message) {
        const field = document.getElementById(fieldName);
        if (field) {
            field.classList.add('error-field');
            const errorDiv = document.createElement('div');
            errorDiv.className = 'field-error';
            errorDiv.innerHTML = `<p>${message}</p>`;
            field.parentNode.insertBefore(errorDiv, field.nextSibling);
        } else if (fieldName === 'cipher_ids') {
            const container = document.querySelector('.course-ciphers-container');
            container.classList.add('error-container');
            
            const errorDiv = document.createElement('div');
            errorDiv.className = 'field-error';
            errorDiv.innerHTML = `<p>${message}</p>`;
            container.appendChild(errorDiv);
        }
    }
    function clearErrors() {
        document.querySelectorAll('.field-error').forEach(el => el.remove());
        document.querySelectorAll('.error-field').forEach(el => {
            el.classList.remove('error-field');
        });
        
        document.querySelectorAll('.error-container').forEach(el => {
            el.classList.remove('error-container');
        });
    }

    updateSelection();
});