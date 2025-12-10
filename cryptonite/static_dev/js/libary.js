document.querySelectorAll('.filter-btn').forEach(btn => {
    btn.addEventListener('click', function () {
        const parent = this.parentElement;
        parent.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
        this.classList.add('active');

        let difficulty = document.querySelector('.filter-btn.active.difficulty-filter-button').innerHTML;

        let wrappers = document.querySelectorAll('.cipher-wrapper');

        wrappers.forEach(wrapper => {
            let card = wrapper.querySelector('.cipher-card');
            let difficulty_cipher = card.getAttribute('data-difficulty');

            if (difficulty_cipher !== difficulty && difficulty !== 'Все') {
                wrapper.style.display = 'none';
            } else {
                wrapper.style.display = 'block';
            }
        });
    });
});
