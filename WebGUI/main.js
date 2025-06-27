document.addEventListener('DOMContentLoaded', function () {
    document.querySelector('form').addEventListener('submit', async function (e) {
        e.preventDefault();
        const form = e.target;
        const data = new URLSearchParams(new FormData(form));
        const response = await fetch('/submit', {
            method: 'POST',
            body: data,
        });
        const text = await response.text();
        document.body.innerHTML = text;
    });
});