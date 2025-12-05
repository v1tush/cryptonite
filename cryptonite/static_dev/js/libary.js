document.querySelectorAll('.filter-btn').forEach(btn => {
    btn.addEventListener('click', function() {
        const parent = this.parentElement;
        parent.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
        this.classList.add('active');
        let difficulty = document.querySelector('.filter-btn.active.difficulty-filter-button').innerHTML;
        let category = document.querySelector('.filter-btn.active.category-filter-button').innerHTML;
        let ciphers = document.getElementsByClassName('cipher-card');
        for (let i = 0; i < ciphers.length; i++) {
            let category_cipher = ciphers[i].getAttribute('data-category');
            let difficulty_cipher = ciphers[i].getAttribute('data-difficulty');
            if ((category_cipher != category & category != 'Все') | (difficulty_cipher != difficulty & difficulty != 'Все')) {
                ciphers[i].style.display = 'none';
            } else {
                ciphers[i].style.display = 'block';
            }
        }
    });
});