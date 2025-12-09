document.addEventListener("DOMContentLoaded", () => {
    const hideButtons = document.querySelectorAll("button[data-hide-url]");
    const modal = document.getElementById("allowHideModal");
    const cancelBtn = modal.querySelector(".modal-cancel");
    const confirmBtn = modal.querySelector(".modal-confirm");
    let currentUrl = "";

    hideButtons.forEach(btn => {
        // Отвязываем старый обработчик (безопасно)
        btn.replaceWith(btn.cloneNode(true));
    });

    const newHideButtons = document.querySelectorAll("button[data-hide-url]");
    newHideButtons.forEach(btn => {
        btn.addEventListener("click", (e) => {
            e.preventDefault();
            currentUrl = btn.dataset.hideUrl;
            modal.classList.remove("hidden");
        });
    });

    cancelBtn.addEventListener("click", () => {
        modal.classList.add("hidden");
        currentUrl = "";
    });

    confirmBtn.addEventListener("click", () => {
        if (currentUrl) {
            // Деактивируем кнопку, чтобы не было двойного клика
            confirmBtn.disabled = true;
            fetch(currentUrl, {
                method: "POST",
                headers: {
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                }
            }).then(() => {
                modal.classList.add("hidden");
                confirmBtn.disabled = false;
                location.reload();
            });
        }
    });
});
