document.addEventListener('DOMContentLoaded', () => {
    let numbers = document.querySelectorAll('.digit-box');
    let animation_time = 3000;

    numbers.forEach(number => {
        let start = 0;
        let end = parseInt(number.dataset.number);

        let step = Math.ceil (end / 100);
        let timing = Math.max(25, Math.floor(animation_time / end));
        
        let counter = setInterval(() => {
            start += step;
            if (start >= end) {
                number.textContent = end; 
                clearInterval(counter);
            } else {
                number.textContent = start;
            }
        }, timing);
    })
});