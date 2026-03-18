document.addEventListener('DOMContentLoaded', function () {
    const allImgBlocks = document.querySelectorAll('.hero__img');
    if (allImgBlocks.length > 0) {
        const randomIndex = Math.floor(Math.random() * allImgBlocks.length);
        allImgBlocks[randomIndex].classList.add('is-visible');
    }

    if (window.location.pathname === '/') {
        document.body.style.setProperty('background-color', '#151515');
    }

    const showcaseButton = document.querySelector('.header__button-btn');
    if (showcaseButton) {
        showcaseButton.addEventListener('click', function () {
            window.location.href = '/upload';
        });
    }
});