document.addEventListener('click', function(e) {
    const btn = e.target.closest('.btn-like');
    if (!btn) return;

    const cipherId = btn.dataset.cipherId;
    if (!cipherId) return;

    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    fetch(`/ciphers/${cipherId}/like/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrfToken,
        },
    })
    .then(response => {

        // Обработка неавторизованного пользователя
        if (response.redirected) {
            alert("Чтобы поставить лайк, нужно войти в аккаунт.");
            return null;
        }

        return response.json();
    })
    .then(data => {
        if (!data) return;

        btn.classList.toggle('liked', data.liked);
        btn.querySelector('.like-count').textContent = data.likes_count;
    })
    .catch(err => console.error(err));
});
