document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', function () {
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(tc => tc.classList.remove('active'));
            btn.classList.add('active');
            document.getElementById('tab-' + btn.dataset.tab).classList.add('active');
            
            // Show/hide the save button and forms based on active tab
            const saveButton = document.querySelector('input[type="submit"]');
            const settingsForm = document.getElementById('settingsForm');
            const trackersContainer = document.querySelector('.settings-form-container');
            
            if (btn.dataset.tab === 'trackers') {
                saveButton.style.display = 'none';
                settingsForm.style.display = 'none';
                trackersContainer.style.display = 'block';
                loadTrackers();
            } else {
                saveButton.style.display = 'block';
                settingsForm.style.display = 'flex';
                trackersContainer.style.display = 'none';
            }
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

        showPopup("Updating Daily Grid, This may take a moment...");

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

    // Custom Trackers functionality
    async function loadTrackers() {
        const trackersList = document.getElementById('trackers-list');
        trackersList.innerHTML = '<div class="loading-message">Loading trackers...</div>';
        
        try {
            const response = await fetch('/api/trackers');
            const trackers = await response.json();
            
            if (trackers.length === 0) {
                trackersList.innerHTML = '<div class="no-trackers">No custom trackers yet. Create one above!</div>';
                return;
            }
            
            trackersList.innerHTML = trackers.map(tracker => {
                const todayValue = tracker.data[0] || 0;
                const last7Days = tracker.data.slice(0, 7);
                const last7DaysSum = last7Days.reduce((sum, val) => sum + val, 0);
                const currentColor = `rgb(${tracker.event[0]}, ${tracker.event[1]}, ${tracker.event[2]})`;
                const hexColor = `#${tracker.event[0].toString(16).padStart(2, '0')}${tracker.event[1].toString(16).padStart(2, '0')}${tracker.event[2].toString(16).padStart(2, '0')}`;
                

                
                return `
                    <div class="tracker-card compact" data-filename="${tracker.filename}">
                        <div class="tracker-header">
                            <h4>${tracker.name}</h4>
                            <button class="delete-tracker-btn" onclick="deleteTracker('${tracker.filename}')">×</button>
                        </div>
                        <div class="tracker-stats">
                            <div class="stat">
                                <span class="stat-label">Today:</span>
                                <span class="stat-value">${todayValue} ${tracker.metric}</span>
                            </div>
                            <div class="stat">
                                <span class="stat-label">Last 7 days:</span>
                                <span class="stat-value">${last7DaysSum} ${tracker.metric}</span>
                            </div>
                            <div class="stat">
                                <span class="stat-label">Color:</span>
                                <div class="color-control">
                                    <div class="color-preview" style="background-color: ${currentColor}"></div>
                                    <input type="color" value="${hexColor}" onchange="updateTrackerColor('${tracker.filename}', this.value)" class="color-input">
                                </div>
                            </div>
                        </div>
                        <div class="tracker-actions">
                            <button class="action-btn increment-btn" onclick="showIncrementPopup('${tracker.filename}', '${tracker.metric}')">Add ${tracker.metric}</button>
                        </div>
                    </div>
                `;
            }).join('');
        } catch (error) {
            console.error('Error loading trackers:', error);
            trackersList.innerHTML = '<div class="error-message">Error loading trackers. Please try again.</div>';
        }
    }
    
    async function createTracker() {
        const nameInput = document.getElementById('new-tracker-name');
        const metricInput = document.getElementById('new-tracker-metric');
        const colorInput = document.getElementById('new-tracker-color');
        
        const name = nameInput.value.trim();
        const metric = metricInput.value.trim();
        const color = colorInput.value;
        
        if (!name || !metric) {
            showPopup('Please enter both a tracker name and metric.');
            return;
        }
        
        try {
            const response = await fetch('/api/trackers', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name, metric, color })
            });
            
            const result = await response.json();
            
            if (result.error) {
                showPopup(result.error);
                return;
            }
            
            nameInput.value = '';
            metricInput.value = '';
            colorInput.value = '#1520e0'; // Reset to default
            showPopup('Tracker created successfully!');
            loadTrackers();
        } catch (error) {
            console.error('Error creating tracker:', error);
            showPopup('Error creating tracker. Please try again.');
        }
    }
    
    window.showIncrementPopup = function(filename, metric) {
        const existing = document.getElementById('increment-popup-modal');
        if (existing) existing.remove();

        const modal = document.createElement('div');
        modal.id = 'increment-popup-modal';
        modal.style.position = 'fixed';
        modal.style.top = '0';
        modal.style.left = '0';
        modal.style.width = '100vw';
        modal.style.height = '100vh';
        modal.style.background = 'rgba(13,17,23,0.85)';
        modal.style.display = 'flex';
        modal.style.alignItems = 'center';
        modal.style.justifyContent = 'center';
        modal.style.zIndex = '10000';

        const box = document.createElement('div');
        box.style.background = 'linear-gradient(135deg, #161b22 0%, #21262d 50%, #30363d 100%)';
        box.style.color = '#f0f6fc';
        box.style.padding = '32px 28px 24px 28px';
        box.style.borderRadius = '16px';
        box.style.boxShadow = '0 12px 48px rgba(0,0,0,0.6), 0 2px 0 rgba(255,255,255,0.05) inset';
        box.style.maxWidth = '400px';
        box.style.width = '90vw';
        box.style.textAlign = 'center';
        box.style.position = 'relative';
        box.style.border = '1px solid #58a6ff';
        
        const trackerName = filename.replace('.json', '').replace(/([A-Z])/g, ' $1').trim();
        
        box.innerHTML = `
            <h3 style="margin:0 0 20px 0;color:#58a6ff;font-size:1.3rem;font-weight:700;">Add ${metric}</h3>
            <p style="margin:0 0 24px 0;color:#8b949e;font-size:1rem;">How many ${metric} would you like to add to <strong style="color:#f0f6fc;">${trackerName}</strong> today?</p>
            <input type="number" id="increment-amount-input" placeholder="Enter amount" min="0" step="0.1" style="
                width: 100%;
                padding: 14px 16px;
                border: 1.5px solid #30363d;
                border-radius: 10px;
                font-size: 1.1rem;
                background: #0d1117;
                color: #f0f6fc;
                margin-bottom: 24px;
                box-sizing: border-box;
                outline: none;
                transition: all 0.3s ease;
            ">
        `;
        
        const input = box.querySelector('#increment-amount-input');
        input.addEventListener('focus', () => {
            input.style.borderColor = '#58a6ff';
            input.style.boxShadow = '0 0 0 3px rgba(88, 166, 255, 0.15)';
        });
        input.addEventListener('blur', () => {
            input.style.borderColor = '#30363d';
            input.style.boxShadow = 'none';
        });

        const closeX = document.createElement('button');
        closeX.innerHTML = '×';
        closeX.style.position = 'absolute';
        closeX.style.top = '12px';
        closeX.style.right = '16px';
        closeX.style.background = 'none';
        closeX.style.border = 'none';
        closeX.style.color = '#8b949e';
        closeX.style.fontSize = '1.8rem';
        closeX.style.cursor = 'pointer';
        closeX.addEventListener('click', () => modal.remove());
        box.appendChild(closeX);

        const buttonContainer = document.createElement('div');
        buttonContainer.style.display = 'flex';
        buttonContainer.style.gap = '12px';
        
        const cancelBtn = document.createElement('button');
        cancelBtn.type = 'button';  // Prevent form submission
        cancelBtn.innerText = 'Cancel';
        cancelBtn.style.flex = '1';
        cancelBtn.style.padding = '12px 0';
        cancelBtn.style.background = '#30363d';
        cancelBtn.style.color = '#8b949e';
        cancelBtn.style.border = 'none';
        cancelBtn.style.borderRadius = '8px';
        cancelBtn.style.cursor = 'pointer';
        cancelBtn.addEventListener('click', () => modal.remove());
        
        const addBtn = document.createElement('button');
        addBtn.type = 'button';
        addBtn.innerText = 'Add';
        addBtn.style.flex = '1';
        addBtn.style.padding = '12px 0';
        addBtn.style.background = 'linear-gradient(135deg, #1f6feb 0%, #58a6ff 100%)';
        addBtn.style.color = '#fff';
        addBtn.style.border = 'none';
        addBtn.style.borderRadius = '8px';
        addBtn.style.cursor = 'pointer';
        addBtn.style.fontWeight = '600';
        
        const handleAdd = async (e) => {
            e.preventDefault();  // Prevent any form submission
            const amount = parseFloat(input.value);
            if (!amount || amount <= 0) {
                input.style.borderColor = '#f85149';
                return;
            }
            
            modal.remove();
            
            try {
                const response = await fetch(`/api/trackers/${filename}/increment`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ amount })
                });
                
                const result = await response.json();
                
                if (result.error) {
                    showPopup(result.error);
                    return;
                }
                
                showPopup(`Successfully added ${amount} ${metric}!`);
                loadTrackers();
            } catch (error) {
                console.error('Error incrementing tracker:', error);
                showPopup('Error updating tracker. Please try again.');
            }
        };
        
        addBtn.addEventListener('click', handleAdd);
        input.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') handleAdd();
        });
        
        buttonContainer.appendChild(cancelBtn);
        buttonContainer.appendChild(addBtn);
        box.appendChild(buttonContainer);

        modal.appendChild(box);
        document.body.appendChild(modal);
        
        setTimeout(() => input.focus(), 100);
    };
    
    window.incrementTracker = async function(filename) {
        const input = document.getElementById(`increment-${filename}`);
        const amount = parseFloat(input.value);
        
        if (!amount || amount <= 0) {
            showPopup('Please enter a valid positive amount.');
            return;
        }
        
        try {
            const response = await fetch(`/api/trackers/${filename}/increment`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ amount })
            });
            
            const result = await response.json();
            
            if (result.error) {
                showPopup(result.error);
                return;
            }
            
            input.value = '';
            showPopup(`Successfully added ${amount} to today's count!`);
            loadTrackers();
        } catch (error) {
            console.error('Error incrementing tracker:', error);
            showPopup('Error updating tracker. Please try again.');
        }
    };
    
    window.deleteTracker = async function(filename) {
        if (!confirm('Are you sure you want to delete this tracker? This action cannot be undone.')) {
            return;
        }
        
        try {
            const response = await fetch(`/api/trackers/${filename}`, {
                method: 'DELETE'
            });
            
            const result = await response.json();
            
            if (result.error) {
                showPopup(result.error);
                return;
            }
            
            showPopup('Tracker deleted successfully.');
            loadTrackers();
        } catch (error) {
            console.error('Error deleting tracker:', error);
            showPopup('Error deleting tracker. Please try again.');
        }
    };
    
    window.updateTrackerColor = async function(filename, hexColor) {
        // Convert hex to RGB
        const r = parseInt(hexColor.slice(1, 3), 16);
        const g = parseInt(hexColor.slice(3, 5), 16);
        const b = parseInt(hexColor.slice(5, 7), 16);
        
        try {
            const response = await fetch(`/api/trackers/${filename}/color`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ color: [r, g, b] })
            });
            
            const result = await response.json();
            if (result.success) {
                // Update the color preview immediately
                const trackerCard = document.querySelector(`[data-filename="${filename}"]`);
                const colorPreview = trackerCard.querySelector('.color-preview');
                colorPreview.style.backgroundColor = hexColor;
            } else {
                showPopup('Error updating color. Please try again.');
            }
        } catch (error) {
            console.error('Error updating tracker color:', error);
            showPopup('Error updating color. Please try again.');
        }
    };
    
    // Set up create tracker button
    document.getElementById('create-tracker-btn').addEventListener('click', (e) => {
        e.preventDefault(); // Prevent form submission
        createTracker();
    });
    
    // Allow Enter key to create tracker
    document.getElementById('new-tracker-name').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') createTracker();
    });
    document.getElementById('new-tracker-metric').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') createTracker();
    });
});
