button = document.getElementById('burger-menu');
button.onclick = function (){
    burgerNav = document.getElementById('nav-burger');
    if (burgerNav.hidden) {
        burgerNav.hidden = false;
        button.innerHTML = '&#10006;'
    } else {
        burgerNav.hidden = true;
        button.innerHTML = '&#9776;'
    }
}