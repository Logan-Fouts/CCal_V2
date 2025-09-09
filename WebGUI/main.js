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

        const generalFields = ['GITHUB_USERNAME', 'GITHUB_TOKEN', 'STARTUP_ANIMATION', 'WEATHER_LAT', 'WEATHER_LON', 'OPENWEATHERMAP_API_KEY', 'BRIGHTNESS', 'ON_TIME', 'OFF_TIME'];
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

        showPopup("Updating CCal, This may take a moment...");

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

        // Create modal overlay
        const modal = document.createElement('div');
        modal.id = 'popup-modal';
        modal.style.position = 'fixed';
        modal.style.top = '0';
        modal.style.left = '0';
        modal.style.width = '100vw';
        modal.style.height = '100vh';
        modal.style.background = 'rgba(13,17,23,0.82)';
        modal.style.display = 'flex';
        modal.style.alignItems = 'center';
        modal.style.justifyContent = 'center';
        modal.style.zIndex = '9999';
        modal.style.transition = 'background 0.3s';

        // Create modal box
        const box = document.createElement('div');
        box.style.background = 'linear-gradient(120deg, #232323 80%, #21262d 100%)';
        box.style.color = '#f0f6fc';
        box.style.padding = '28px 20px 18px 20px';
        box.style.borderRadius = '18px';
        box.style.boxShadow = '0 8px 40px #000a, 0 1.5px 0 #222';
        box.style.maxWidth = '92vw';
        box.style.width = 'min(420px, 96vw)';
        box.style.maxHeight = '80vh';
        box.style.overflowY = 'auto';
        box.style.textAlign = 'center';
        box.style.position = 'relative';
        box.style.animation = 'popup-fadein 0.25s cubic-bezier(.4,2,.6,1)';
        box.innerHTML = `<div style="font-size:1.18rem;font-weight:500;margin-bottom:18px;word-break:break-word;">${message}</div>`;

        // Close button (top right X)
        const closeX = document.createElement('button');
        closeX.innerHTML = '&times;';
        closeX.setAttribute('aria-label', 'Close');
        closeX.style.position = 'absolute';
        closeX.style.top = '10px';
        closeX.style.right = '14px';
        closeX.style.background = 'none';
        closeX.style.border = 'none';
        closeX.style.color = '#fa5252';
        closeX.style.fontSize = '1.7rem';
        closeX.style.cursor = 'pointer';
        closeX.style.fontWeight = 'bold';
        closeX.style.transition = 'color 0.2s';
        closeX.addEventListener('mouseenter', () => closeX.style.color = '#ff8787');
        closeX.addEventListener('mouseleave', () => closeX.style.color = '#fa5252');
        closeX.addEventListener('click', () => modal.remove());
        box.appendChild(closeX);

        // Close button (bottom)
        const closeBtn = document.createElement('button');
        closeBtn.innerText = 'Close';
        closeBtn.style.marginTop = '18px';
        closeBtn.style.padding = '12px 0';
        closeBtn.style.width = '100%';
        closeBtn.style.background = 'linear-gradient(90deg, #fa5252 0%, #ff8787 100%)';
        closeBtn.style.color = '#fff';
        closeBtn.style.border = 'none';
        closeBtn.style.borderRadius = '8px';
        closeBtn.style.cursor = 'pointer';
        closeBtn.style.fontSize = '1.08rem';
        closeBtn.style.fontWeight = '600';
        closeBtn.style.boxShadow = '0 2px 8px #01040944';
        closeBtn.style.letterSpacing = '0.5px';
        closeBtn.style.transition = 'background 0.2s, transform 0.1s, box-shadow 0.2s';
        closeBtn.addEventListener('mouseenter', () => closeBtn.style.background = 'linear-gradient(90deg, #ff8787 0%, #fa5252 100%)');
        closeBtn.addEventListener('mouseleave', () => closeBtn.style.background = 'linear-gradient(90deg, #fa5252 0%, #ff8787 100%)');
        closeBtn.addEventListener('click', () => modal.remove());
        box.appendChild(closeBtn);

        // Responsive: shrink padding and font on small screens
        const style = document.createElement('style');
        style.innerHTML = `
        @media (max-width: 600px) {
            #popup-modal > div {
                padding: 12vw 2vw 8vw 2vw !important;
                font-size: 1rem !important;
                border-radius: 10px !important;
                width: 98vw !important;
                max-width: 99vw !important;
            }
            #popup-modal button {
                font-size: 1rem !important;
                padding: 10px 0 !important;
            }
        }
        @keyframes popup-fadein {
            from { opacity: 0; transform: scale(0.95); }
            to { opacity: 1; transform: scale(1); }
        }
        `;
        document.head.appendChild(style);

        modal.appendChild(box);
        document.body.appendChild(modal);
    }
});
