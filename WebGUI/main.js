document.addEventListener('DOMContentLoaded', function () {
    // Main tab switching
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', function () {
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(tc => tc.classList.remove('active'));
            btn.classList.add('active');
            document.getElementById('tab-' + btn.dataset.tab).classList.add('active');
        });
    });

    // Subtab switching (only when Add-ons tab is active)
    document.querySelectorAll('.subtab-btn').forEach(btn => {
        btn.addEventListener('click', function () {
            document.querySelectorAll('.subtab-btn').forEach(b => b.classList.remove('active'));
            document.querySelectorAll('.subtab-content').forEach(tc => tc.classList.remove('active'));
            btn.classList.add('active');
            document.getElementById('subtab-' + btn.dataset.subtab).classList.add('active');
        });
    });

    // Enhanced AJAX form submit to handle unchecked checkboxes and skip empty general settings
    document.querySelector('form').addEventListener('submit', async function (e) {
        e.preventDefault();
        const form = e.target;
        const formData = new FormData(form);

        // Ensure unchecked checkboxes are sent as 'off'
        form.querySelectorAll('input[type="checkbox"]').forEach(cb => {
            if (!formData.has(cb.name)) {
                formData.append(cb.name, 'off');
            }
        });

        // Remove general settings if all are empty
        const generalFields = ['GITHUB_USERNAME', 'GITHUB_TOKEN', 'STARTUP_ANIMATION'];
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

        const data = new URLSearchParams(formData);
        const response = await fetch('/submit', {
            method: 'POST',
            body: data,
        });
        const text = await response.text();
        document.body.innerHTML = text;
    });
});
