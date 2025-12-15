document.addEventListener('DOMContentLoaded', function() {
    const UserName = document.getElementById('username').innerText;
    if (UserName.length > 10){
        document.querySelector('nav').style.display = 'none';
        document.getElementById('burger-menu').style.display = 'block';
    }
})