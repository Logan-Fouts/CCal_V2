const express = require('express');
const bodyParser = require('body-parser');
const fs = require('fs');
const path = require('path');
const { exec } = require('child_process');

const app = express();
const PORT = 8080;
USERNAME="lfouts"

app.engine('html', require('ejs').renderFile);
app.set('view engine', 'ejs');
app.set('views', __dirname);

app.use(bodyParser.urlencoded({ extended: true }));
app.use(bodyParser.json());
app.use(express.static(__dirname));

app.use((err, req, res, next) => {
    console.error(err.stack);
    res.status(500).send('Something broke!');
});

require('dotenv').config({ path: `/home/${USERNAME}/Daily-Grid/WebGUI/.env` });
// const BASIC_AUTH_USER = process.env.DAILYGRID_WEBGUI_USER || 'dailygrid';
// const BASIC_AUTH_PASS = process.env.DAILYGRID_WEBGUI_PASS || 'raspberry';
const BASIC_AUTH_USER = 'dev';
const BASIC_AUTH_PASS = 'dev';

// Basic Auth middleware
app.use((req, res, next) => {
    const auth = req.headers.authorization;
    if (!auth) {
        res.set('WWW-Authenticate', 'Basic realm="Daily Grid WebGUI"');
        return res.status(401).send('Authentication required.');
    }
    const [scheme, encoded] = auth.split(' ');
    if (scheme !== 'Basic') {
        return res.status(400).send('Bad auth scheme.');
    }
    const decoded = Buffer.from(encoded, 'base64').toString();
    const [user, pass] = decoded.split(':');
    if (user === BASIC_AUTH_USER && pass === BASIC_AUTH_PASS) {
        return next();
    }
    res.set('WWW-Authenticate', 'Basic realm="Daily Grid WebGUI"');
    return res.status(401).send('Authentication failed.');
});

app.get('/', (req, res) => {
    const configPath = path.join(__dirname, '../config.json');
    let config = {};
    try {
        config = JSON.parse(fs.readFileSync(configPath, 'utf8'));
    } catch (e) {
        config = {};
    }
    res.render('index', { config: config });
});

app.post('/submit', (req, res, next) => {
    const configPath = path.join(__dirname, '../config.json');

    let existingConfig = {};
    try {
        existingConfig = JSON.parse(fs.readFileSync(configPath, 'utf8'));
    } catch (e) {
        existingConfig = {};
    }

    const newConfig = Object.assign({}, existingConfig);

    // Github setup
    if (req.body.GITHUB_USERNAME && req.body.GITHUB_USERNAME.trim() !== '') {
        newConfig.GITHUB_USERNAME = req.body.GITHUB_USERNAME.trim();
    }

    if (req.body.GITHUB_TOKEN && req.body.GITHUB_TOKEN.trim() !== '') {
        newConfig.GITHUB_TOKEN = req.body.GITHUB_TOKEN.trim();
    }

    // Startup animation
    if (req.body.STARTUP_ANIMATION !== undefined &&
        req.body.STARTUP_ANIMATION !== null &&
        req.body.STARTUP_ANIMATION !== '' &&
        !isNaN(Number(req.body.STARTUP_ANIMATION))) {
        newConfig.STARTUP_ANIMATION = Number(req.body.STARTUP_ANIMATION);
    }

    if (req.body.BRIGHTNESS !== undefined && req.body.BRIGHTNESS !== null && req.body.BRIGHTNESS !== '' && !isNaN(Number(req.body.BRIGHTNESS))) {
        console.log(`Updating brightness to ${req.body.BRIGHTNESS}`);
        newConfig.BRIGHTNESS = Number(req.body.BRIGHTNESS);
    }

    // Weather Lat and Long
    if (req.body.WEATHER_LAT !== undefined &&
        req.body.WEATHER_LAT !== null &&
        req.body.WEATHER_LAT !== '' &&
        !isNaN(Number(req.body.WEATHER_LAT))) {
        newConfig.WEATHER_LAT = Number(req.body.WEATHER_LAT);
    }

    if (req.body.WEATHER_LON !== undefined &&
        req.body.WEATHER_LON !== null &&
        req.body.WEATHER_LON !== '' &&
        !isNaN(Number(req.body.WEATHER_LON))) {
        newConfig.WEATHER_LON = Number(req.body.WEATHER_LON);
    }
    
    // Open weather api key
    if (req.body.OPENWEATHERMAP_API_KEY && req.body.OPENWEATHERMAP_API_KEY.trim() !== '') {
        newConfig.OPENWEATHERMAP_API_KEY = req.body.OPENWEATHERMAP_API_KEY.trim();
    }

    // ON_TIME and OFF_TIME
    if (req.body.ON_TIME !== undefined &&
        req.body.ON_TIME !== null &&
        req.body.ON_TIME !== '' &&
        !isNaN(Number(req.body.ON_TIME))) {
        newConfig.ON_TIME = Number(req.body.ON_TIME);
    }

    if (req.body.OFF_TIME !== undefined &&
        req.body.OFF_TIME !== null &&
        req.body.OFF_TIME !== '' &&
        !isNaN(Number(req.body.OFF_TIME))) {
        newConfig.OFF_TIME = Number(req.body.OFF_TIME);
    }

    // Addons
    newConfig.TAILSCALE_ENABLE = req.body.TAILSCALE_ENABLE === 'on';
    newConfig.PIHOLE_ENABLE = req.body.PIHOLE_ENABLE === 'on';
    newConfig.SYNCTHING_ENABLE = req.body.SYNCTHING_ENABLE === 'on';

    fs.writeFile(configPath, JSON.stringify(newConfig, null, 2), (err) => {
        if (err) {
            console.error(err);
            return res.status(500).send('Error saving config.');
        }


        exec(`sudo bash /home/${USERNAME}/Daily-Grid/WebGUI/setup_addons.sh`,
            { timeout: 120000 },
            (error, stdout, stderr) => {
                if (error) {
                    console.error(`Setup error: ${error.message}`);
                    return res.status(500).send('Config saved, but error running setup script.');
                }
                if (stderr) {
                    console.error(`Setup stderr: ${stderr}`);
                }
                console.log(`Setup stdout: ${stdout}`);
                res.send('<h2>Config saved and add-ons setup!</h2><a href="/">Back</a>');
            });
    });
});

// Custom tracker endpoints
app.get('/api/trackers', (req, res) => {
    const trackersDir = path.join(__dirname, '../CustomTrackers');
    try {
        const files = fs.readdirSync(trackersDir).filter(file => file.endsWith('.json'));
        const trackers = files.map(file => {
            const filePath = path.join(trackersDir, file);
            try {
                const data = JSON.parse(fs.readFileSync(filePath, 'utf8'));
                return {
                    filename: file,
                    ...data
                };
            } catch (e) {
                console.error(`Error reading tracker file ${file}:`, e);
                return null;
            }
        }).filter(tracker => tracker !== null);
        res.json(trackers);
    } catch (e) {
        console.error('Error listing trackers:', e);
        res.status(500).json({ error: 'Failed to load trackers' });
    }
});

app.post('/api/trackers', (req, res) => {
    const { name, metric, color } = req.body;
    
    if (!name || !metric) {
        return res.status(400).json({ error: 'Name and metric are required' });
    }
    
    const filename = name.replace(/[^a-zA-Z0-9]/g, '') + '.json';
    const filePath = path.join(__dirname, '../CustomTrackers', filename);
    
    // Check if file already exists
    if (fs.existsSync(filePath)) {
        return res.status(400).json({ error: 'Tracker with this name already exists' });
    }
    
    // Convert hex color to RGB if provided, otherwise use default blue
    let rgbColor = [21, 32, 224]; // Default blue
    if (color) {
        const r = parseInt(color.slice(1, 3), 16);
        const g = parseInt(color.slice(3, 5), 16);
        const b = parseInt(color.slice(5, 7), 16);
        rgbColor = [r, g, b];
    }
    
    const newTracker = {
        name: name,
        data: new Array(28).fill(0), // 28 days of data, all zeros
        no_events: [30, 30, 30],
        event: rgbColor,
        metric: metric
    };
    
    try {
        fs.writeFileSync(filePath, JSON.stringify(newTracker, null, 2));
        res.json({ success: true, filename });
    } catch (e) {
        console.error('Error creating tracker:', e);
        res.status(500).json({ error: 'Failed to create tracker' });
    }
});

app.post('/api/trackers/:filename/increment', (req, res) => {
    const { filename } = req.params;
    const { amount } = req.body;
    
    if (!amount || isNaN(amount) || amount < 0) {
        return res.status(400).json({ error: 'Valid positive amount is required' });
    }
    
    const filePath = path.join(__dirname, '../CustomTrackers', filename);
    
    try {
        if (!fs.existsSync(filePath)) {
            return res.status(404).json({ error: 'Tracker not found' });
        }
        
        const tracker = JSON.parse(fs.readFileSync(filePath, 'utf8'));
        
        // Increment today's count (last element in the array)
        tracker.data[0] += parseFloat(amount);
        
        fs.writeFileSync(filePath, JSON.stringify(tracker, null, 2));
        res.json({ success: true, newValue: tracker.data[tracker.data.length - 1] });
    } catch (e) {
        console.error('Error updating tracker:', e);
        res.status(500).json({ error: 'Failed to update tracker' });
    }
});

app.delete('/api/trackers/:filename', (req, res) => {
    const { filename } = req.params;
    const filePath = path.join(__dirname, '../CustomTrackers', filename);
    
    try {
        if (!fs.existsSync(filePath)) {
            return res.status(404).json({ error: 'Tracker not found' });
        }
        
        fs.unlinkSync(filePath);
        res.json({ success: true });
    } catch (e) {
        console.error('Error deleting tracker:', e);
        res.status(500).json({ error: 'Failed to delete tracker' });
    }
});

app.put('/api/trackers/:filename/color', (req, res) => {
    const { filename } = req.params;
    const { color } = req.body;
    
    if (!color || !Array.isArray(color) || color.length !== 3) {
        return res.status(400).json({ error: 'Valid RGB color array is required' });
    }
    
    const filePath = path.join(__dirname, '../CustomTrackers', filename);
    
    try {
        if (!fs.existsSync(filePath)) {
            return res.status(404).json({ error: 'Tracker not found' });
        }
        
        const tracker = JSON.parse(fs.readFileSync(filePath, 'utf8'));
        tracker.event = color;
        
        fs.writeFileSync(filePath, JSON.stringify(tracker, null, 2));
        res.json({ success: true });
    } catch (e) {
        console.error('Error updating tracker color:', e);
        res.status(500).json({ error: 'Failed to update tracker color' });
    }
});

app.listen(PORT, '0.0.0.0', () => {
    console.log(`Server running at http://localhost:${PORT}`);
});
