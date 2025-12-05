Array.from(document.getElementsByClassName('likes')).forEach(like_btn => {
    like_btn.addEventListener('click', function() {
        let like_flag = this.getAttribute('data-like');
        if (like_flag == "0") {
            let like_cnt = this.innerHTML.split(' ')[1];
            this.innerHTML = this.innerHTML.split(' ')[0] + ' ' + (+like_cnt + 1);
            this.setAttribute('data-like', '1');
            this.classList.add('yellow-text')
        } else {
            let like_cnt = this.innerHTML.split(' ')[1];
            this.innerHTML = this.innerHTML.split(' ')[0] + ' ' + (+like_cnt - 1);
            this.setAttribute('data-like', '0');
            this.classList.remove('yellow-text')
        }
    })
});