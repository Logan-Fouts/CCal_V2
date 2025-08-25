document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', function () {
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(tc => tc.classList.remove('active'));
            btn.classList.add('active');
            document.getElementById('tab-' + btn.dataset.tab).classList.add('active');
        });
    });

    document.querySelectorAll('.subtab-btn').forEach(btn => {
        btn.addEventListener('click', function () {
            document.querySelectorAll('.subtab-btn').forEach(b => b.classList.remove('active'));
            document.querySelectorAll('.subtab-content').forEach(tc => tc.classList.remove('active'));
            btn.classList.add('active');
            document.getElementById('subtab-' + btn.dataset.subtab).classList.add('active');
        });
    });

    document.querySelector('form').addEventListener('submit', async function (e) {
        e.preventDefault();
        const form = e.target;
        const formData = new FormData(form);

        form.querySelectorAll('input[type="checkbox"]').forEach(cb => {
            if (!formData.has(cb.name)) {
                formData.append(cb.name, 'off');
            }
        });

        const generalFields = ['GITHUB_USERNAME', 'GITHUB_TOKEN', 'STARTUP_ANIMATION', 'WEATHER_LAT', 'WEATHER_LON'];
        let generalHasValue = false;
        for (const field of generalFields) {
            if (formData.get(field) && formData.get(field).trim() !== '') {
                generalHasValue = true;
                break;
            }
        }
        if (!generalHasValue) {
            generalFields.forEach(field => formData.delete(field));
        }

        showPopup("Updating CCal settings...");

        const data = new URLSearchParams(formData);
        const response = await fetch('/submit', {
            method: 'POST',
            body: data,
        });
        const text = await response.text();

        showPopup(text);
    });

    function showPopup(message) {
        const existing = document.getElementById('popup-modal');
        if (existing) existing.remove();

        const modal = document.createElement('div');
        modal.id = 'popup-modal';
        modal.style.position = 'fixed';
        modal.style.top = '0';
        modal.style.left = '0';
        modal.style.width = '100vw';
        modal.style.height = '100vh';
        modal.style.background = 'rgba(0,0,0,0.6)';
        modal.style.display = 'flex';
        modal.style.alignItems = 'center';
        modal.style.justifyContent = 'center';
        modal.style.zIndex = '9999';

        const box = document.createElement('div');
        box.style.background = '#232323';
        box.style.color = '#fafafa';
        box.style.padding = '32px 28px';
        box.style.borderRadius = '12px';
        box.style.boxShadow = '0 4px 32px #000a';
        box.style.maxWidth = '90vw';
        box.style.maxHeight = '80vh';
        box.style.overflowY = 'auto';
        box.innerHTML = message;

        const closeBtn = document.createElement('button');
        closeBtn.innerText = 'Close';
        closeBtn.style.marginTop = '16px';
        closeBtn.style.padding = '10px 20px';
        closeBtn.style.background = '#fa5252';
        closeBtn.style.color = '#fff';
        closeBtn.style.border = 'none';
        closeBtn.style.borderRadius = '8px';
        closeBtn.style.cursor = 'pointer';
        closeBtn.addEventListener('click', () => modal.remove());

        box.appendChild(closeBtn);
        modal.appendChild(box);
        document.body.appendChild(modal);
    }
});
