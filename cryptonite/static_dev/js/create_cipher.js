function selectDifficulty(value) {
    const radio = document.querySelector(`input[name="difficulty"][value="${value}"]`);
    if (radio) {
        radio.checked = true;
        radio.dispatchEvent(new Event('change'));
    }
    document.querySelectorAll('.difficulty-option').forEach(el => {
        el.classList.remove('selected');
    });
    const selectedOption = document.querySelector(`.difficulty-option input[value="${value}"]`).closest('.difficulty-option');
    if (selectedOption) {
        selectedOption.classList.add('selected');
    }
}

let hintCounter = document.querySelectorAll('.hint-field-group').length || 1;

document.addEventListener('DOMContentLoaded', function() {
    const selectedRadio = document.querySelector('input[name="difficulty"]:checked');
    if (selectedRadio) {
        selectDifficulty(selectedRadio.value);
    }
    const addHintBtn = document.getElementById('add-hint-btn');
    const hintsContainer = document.getElementById('hints-container');
    const cipherForm = document.getElementById('cipher-form');
    
    addHintBtn.addEventListener('click', function() {
        const newIndex = hintCounter;
        hintCounter++;
        
        const hintHtml = `
            <div class="hint-field-group" data-index="${newIndex}">
                <div class="hint-field-header">
                    <span class="hint-number">Подсказка ${newIndex + 1}</span>
                    <button type="button" class="remove-hint-btn btn btn-small btn-danger">Удалить</button>
                </div>
                <textarea 
                    class="hint-textarea" 
                    name="hints[]" 
                    placeholder="Введите текст подсказки..."></textarea>
            </div>
        `;
        
        hintsContainer.insertAdjacentHTML('beforeend', hintHtml);
        const newRemoveBtn = hintsContainer.querySelector(`.hint-field-group[data-index="${newIndex}"] .remove-hint-btn`);
        newRemoveBtn.addEventListener('click', function() {
            this.closest('.hint-field-group').remove();
            updateHintNumbers();
        });
    });
    
    document.querySelectorAll('.remove-hint-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            if (document.querySelectorAll('.hint-field-group').length > 1) {
                this.closest('.hint-field-group').remove();
                updateHintNumbers();
            } else {
                alert('Должна остаться хотя бы одна подсказка. Если не хотите использовать подсказки, оставьте поле пустым.');
            }
        });
    });
    
    function updateHintNumbers() {
        document.querySelectorAll('.hint-field-group').forEach((group, index) => {
            const numberSpan = group.querySelector('.hint-number');
            if (numberSpan) {
                numberSpan.textContent = `Подсказка ${index + 1}`;
            }
            group.dataset.index = index;
        });
        hintCounter = document.querySelectorAll('.hint-field-group').length;
    }

    function showFieldErrors(errors) {
        document.querySelectorAll('.field-error').forEach(el => el.remove());
        
        document.querySelectorAll('.form-group input, .form-group textarea, .form-group select').forEach(field => {
            field.style.borderColor = '';
            field.style.boxShadow = '';
        });

        Object.keys(errors).forEach(fieldName => {
            let field = document.getElementById(`id_${fieldName}`);
            if (!field) {
                field = document.querySelector(`[name="${fieldName}"]`);
            }
            
            if (field) {
                const formGroup = field.closest('.form-group');
                
                if (formGroup) {
                    const errorDiv = document.createElement('div');
                    errorDiv.className = 'field-error';
                    errorDiv.style.cssText = `
                        color: #fb4934;
                        font-size: 14px;
                        margin-top: 8px;
                        padding: 5px;
                        background: rgba(251, 73, 52, 0.1);
                        border-radius: 4px;
                    `;
                    errors[fieldName].forEach(error => {
                        const p = document.createElement('p');
                        p.style.margin = '3px 0';
                        p.textContent = error;
                        errorDiv.appendChild(p);
                    });
                    const afterElement = field.nextElementSibling;
                    if (afterElement && afterElement.classList.contains('form-note')) {
                        formGroup.insertBefore(errorDiv, afterElement);
                    } else {
                        formGroup.appendChild(errorDiv);
                    }
                    field.style.borderColor = '#fb4934';
                    field.style.boxShadow = '0 0 0 2px rgba(251, 73, 52, 0.2)';
                }
            }
        });
        
        if (errors.non_field_errors || errors.__all__) {
            const nonFieldErrors = errors.non_field_errors || errors.__all__;
            const formErrorDiv = document.createElement('div');
            formErrorDiv.className = 'form-error';
            formErrorDiv.style.cssText = `
                background: rgba(251, 73, 52, 0.1);
                border: 1px solid #fb4934;
                border-radius: 8px;
                padding: 15px;
                margin-bottom: 20px;
                color: #fb4934;
            `;
            
            nonFieldErrors.forEach(error => {
                const p = document.createElement('p');
                p.style.margin = '5px 0';
                p.textContent = error;
                formErrorDiv.appendChild(p);
            });
            
            const form = document.getElementById('cipher-form');
            if (form) {
                form.insertBefore(formErrorDiv, form.firstChild);
            }
        }
    }
    
    cipherForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        const formData = new FormData(this);
        const hints = [];
        document.querySelectorAll('.hint-textarea').forEach(textarea => {
            const text = textarea.value.trim();
            if (text) {
                hints.push({
                    id: textarea.dataset.hintId || null,
                    text,
                    order: hints.length + 1
                });
            }
        });
        formData.delete('hints[]');
        formData.set('hints_payload', JSON.stringify(hints));
        
        try {
            const response = await fetch(this.action, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });
            
            const data = await response.json();

            if (data.success) {
                window.location.href = data.redirect_url;
            } else {
                if (data.errors) {
                    showFieldErrors(data.errors);
                    const submitBtn = this.querySelector('button[type="submit"]');
                    submitBtn.disabled = false;
                }
            }
        } catch (error) {
            console.error('Ошибка:', error);
            alert('Произошла ошибка при отправке формы');
            this.querySelector('button[type="submit"]').disabled = false;
        }
    });
});
