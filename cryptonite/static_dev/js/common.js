Array.from(document.getElementsByClassName('likes')).forEach(like_btn => {
    like_btn.addEventListener('click', function(event) {
        event.preventDefault();
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        const cipherId = this.getAttribute('data-cipher-id');
        
        fetch(`/ciphers/${cipherId}/like/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrfToken,
                'Content-Type': 'application/json',
            },
            credentials: 'same-origin'
        })
        .then(response => {
            if (response.redirected) {
                alert("Чтобы поставить лайк, нужно войти в аккаунт.");
                window.location.href = response.url;
                return null;
            }
            if (response.ok) {
                return response.json();
            }
        })
        .then(data => {
            if (!data) return;
            this.classList.toggle('yellow-text', data.liked);
            this.querySelector('.likes-cnt').textContent = data.likes_count;
        })
        .catch(err => {
            console.error('Error:', err);
            alert('Произошла ошибка при обновлении лайка');
        });
    });
});