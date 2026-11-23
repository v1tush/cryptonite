class HintSystem {
    constructor() {
        this.csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
        this.HINT_PRICE = Number(document.querySelector('.hints-container').dataset.price);
        this.purchasing = false;
        this.currentUrl = window.location.href;
        this.messageContainer = document.getElementById('message-container');
        
        this.init();
    }
    
    init() {
        this.bindEvents();
    }
    
    bindEvents() {
        document.querySelectorAll('.buy-hint-btn').forEach(btn => {
            btn.addEventListener('click', (e) => this.handleHintPurchase(e));
        });
        document.querySelectorAll('.hint-card.available').forEach(card => {
            card.addEventListener('click', (e) => {
                if (!e.target.closest('.buy-hint-btn')) {
                    card.classList.toggle('expanded');
                }
            });
        });
    }
    
    async handleHintPurchase(event) {
        event.preventDefault();
        event.stopPropagation();
        if (this.purchasing) return;
        
        const buyBtn = event.currentTarget;
        const hintCard = buyBtn.closest('.hint-card');
        const hintId = buyBtn.dataset.hintId;

        if (hintCard.classList.contains('purchased')) {
            this.showMessage('Вы уже купили эту подсказку', 'error');
            return;
        }

        const currentBalance = parseInt(document.getElementById('user-balance').textContent);
        if (currentBalance < this.HINT_PRICE) {
            this.showMessage(`Недостаточно монет. Нужно ${this.HINT_PRICE}`, 'error');
            return;
        }

        this.purchasing = true;
        this.setLoadingState(buyBtn, hintCard, true);
        
        try {
            const response = await fetch(this.currentUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': this.csrfToken
                },
                body: JSON.stringify({ hint_id: hintId })
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.showMessage(data.message, 'success');
                this.updateHintCard(hintCard, data.hint);
                this.updateUserBalance(data.new_balance);
                this.updateBuyButtons();
            } else {
                this.showMessage(data.error, 'error');
                this.setLoadingState(buyBtn, hintCard, false);
            }
            
        } catch (error) {
            console.error('Ошибка при покупке подсказки:', error);
            this.showMessage('Произошла ошибка при покупке', 'error');
            this.setLoadingState(buyBtn, hintCard, false);
        } finally {
            this.purchasing = false;
        }
    }
    
    setLoadingState(button, card, isLoading) {
        if (isLoading) {
            button.disabled = true;
            button.innerHTML = `
                <span class="loading-spinner"></span>
                <span class="loading-text">Покупка...</span>
            `;
            card.classList.add('purchasing');
        } else {
            button.disabled = false;
            button.innerHTML = `Купить за ${this.HINT_PRICE} монет`;
            card.classList.remove('purchasing');
        }
    }
    
    updateHintCard(card, hintData) {
        card.classList.remove('available');
        card.classList.remove('expanded');
        card.classList.add('purchased');
        const priceDiv = card.querySelector('.hint-price');
        if (priceDiv) {
            priceDiv.innerHTML = `
                <span class="purchased-icon">✓</span>
                <span class="purchased-text">Куплена</span>
            `;
            priceDiv.classList.add('purchased-badge');
        }
        const lockedContent = card.querySelector('.locked-content');
        if (lockedContent) {
            lockedContent.remove();
        }
        
        let hintContent = card.querySelector('.hint-content');
        if (!hintContent) {
            hintContent = document.createElement('div');
            hintContent.className = 'hint-content';
            card.appendChild(hintContent);
        }
        
        hintContent.innerHTML = `
            <div class="hint-text">
                ${this.escapeHtml(hintData.text).replace(/\n/g, '<br>')}
            </div>
        `;
        this.animatePurchaseSuccess(card);
    }
    
    updateUserBalance(newBalance) {
        const balanceElement = document.getElementById('user-balance');
        if (balanceElement) {
            balanceElement.textContent = newBalance;
        }
    }
    
    updateBuyButtons() {
        const currentBalance = parseInt(document.getElementById('user-balance')?.textContent || 0);
        document.querySelectorAll('.buy-hint-btn').forEach(btn => {
            const card = btn.closest('.hint-card');
            if (card.classList.contains('purchased')) {
                btn.disabled = true;
                btn.textContent = 'Уже куплено';
                return;
            }
            if (currentBalance < this.HINT_PRICE) {
                btn.disabled = true;
                const parent = btn.closest('.locked-content');
                if (parent) {
                    let insufficientMsg = parent.querySelector('.insufficient-funds');
                    if (!insufficientMsg) {
                        insufficientMsg = document.createElement('p');
                        insufficientMsg.className = 'insufficient-funds';
                        insufficientMsg.textContent = 'Недостаточно монет';
                        parent.appendChild(insufficientMsg);
                    }
                }
            } else {
                btn.disabled = false;
                const parent = btn.closest('.locked-content');
                if (parent) {
                    const insufficientMsg = parent.querySelector('.insufficient-funds');
                    if (insufficientMsg) {
                        insufficientMsg.remove();
                    }
                }
            }
        });
    }
    
    showMessage(text, type = 'success') {
        const existingMessages = this.messageContainer.querySelectorAll('.message');
        existingMessages.forEach(msg => msg.remove());
        const messageDiv = document.createElement('div');
        messageDiv.className = `message message-${type}`;
        messageDiv.innerHTML = `
            <span class="message-icon">${type === 'success' ? '✓' : '✗'}</span>
            <span class="message-text"></span>
        `;
        messageDiv.querySelector('.message-text').textContent = text;
        
        this.messageContainer.appendChild(messageDiv);
        setTimeout(() => {
            messageDiv.classList.add('fade-out');
            setTimeout(() => messageDiv.remove(), 300);
        }, 3000);
    }
    
    animatePurchaseSuccess(card) {
        card.style.transform = 'scale(1.05)';
        card.style.boxShadow = '0 0 20px rgba(106, 153, 85, 0.5)';
        
        setTimeout(() => {
            card.style.transform = 'scale(1)';
            card.style.boxShadow = '';
        }, 500);
    }
    
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

document.addEventListener('DOMContentLoaded', () => {
    if (document.querySelector('.hints-container')) {
        window.hintSystem = new HintSystem();
    }
});
