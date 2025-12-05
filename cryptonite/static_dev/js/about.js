document.addEventListener('DOMContentLoaded', function() {
    const screenshotBtns = document.querySelectorAll('.screenshot-btn');
    const screenshotFrames = document.querySelectorAll('.screenshot-frame');
    screenshotBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            screenshotBtns.forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            const screenshotType = this.dataset.screenshot;
            screenshotFrames.forEach(frame => {
                frame.classList.remove('active');
            });
            document.getElementById(`screenshot-${screenshotType}`).classList.add('active');
        });
    });
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            if (this.getAttribute('href') !== '#') {
                e.preventDefault();
                const targetId = this.getAttribute('href');
                const targetElement = document.querySelector(targetId);
                if (targetElement) {
                    window.scrollTo({
                        top: targetElement.offsetTop - 100,
                        behavior: 'smooth'
                    });
                }
            }
        });
    });
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.animation = 'fadeIn 0.8s ease forwards';
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);
    document.querySelectorAll('.section, .feature-card, .team-card, .timeline-item').forEach(el => {
        el.style.opacity = '0';
        observer.observe(el);
    });
});