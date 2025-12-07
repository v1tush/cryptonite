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
document.addEventListener('DOMContentLoaded', function() {
    const selectedRadio = document.querySelector('input[name="difficulty"]:checked');
    if (selectedRadio) {
        selectDifficulty(selectedRadio.value);
    }
});