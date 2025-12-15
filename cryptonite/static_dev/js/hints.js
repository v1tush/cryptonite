class HintSystem {
    constructor() {
        this.csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        this.HINT_PRICE = 100;
        this.currentUrl = window.location.href;
        this.messageContainer = document.getElementById('message-container');
        
        this.init();
    }
    
    init() {
        this.bindEvents();
        this.checkSolvedCipher();
        this.updateBuyButtons();
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
            const oldBalance = parseInt(balanceElement.textContent);
            this.animateBalanceChange(balanceElement, oldBalance, newBalance);
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
    
    checkSolvedCipher() {
        const solvedMessage = document.querySelector('.solution-result.success');
        if (solvedMessage) {
            document.querySelectorAll('.buy-hint-btn').forEach(btn => {
                btn.disabled = true;
                btn.textContent = 'Шифр уже решен';
            });
        }
    }
    
    showMessage(text, type = 'success') {
        const existingMessages = this.messageContainer.querySelectorAll('.message');
        existingMessages.forEach(msg => msg.remove());
        const messageDiv = document.createElement('div');
        messageDiv.className = `message message-${type}`;
        messageDiv.innerHTML = `
            <span class="message-icon">${type === 'success' ? '✓' : '✗'}</span>
            <span class="message-text">${text}</span>
        `;
        
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
    
    animateBalanceChange(element, oldValue, newValue) {
        const duration = 500;
        const steps = 20;
        const stepDuration = duration / steps;
        const increment = (newValue - oldValue) / steps;
        let current = oldValue;
        let step = 0;
        this.balanceAnimationTimer = setInterval(() => {
            current += increment;
            step++;
            
            if (step >= steps) {
                element.textContent = newValue;
                clearInterval(this.balanceAnimationTimer);
                this.balanceAnimationTimer = null;
            } else {
                element.textContent = Math.round(current);
            }
        }, stepDuration);
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