document.addEventListener('DOMContentLoaded', () => {
    const container = document.getElementById('toasts-container');

    Array.from(container.children).forEach(element => {
        bootstrap.Toast.getOrCreateInstance(element).show();
    })
});