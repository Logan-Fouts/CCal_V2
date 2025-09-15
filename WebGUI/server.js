const express = require('express');
const bodyParser = require('body-parser');
const fs = require('fs');
const path = require('path');
const { exec } = require('child_process');

const app = express();
const PORT = 8080;
USERNAME="username"

app.engine('html', require('ejs').renderFile);
app.set('view engine', 'ejs');
app.set('views', __dirname);

app.use(bodyParser.urlencoded({ extended: true }));
app.use(express.static(__dirname));

app.use((err, req, res, next) => {
    console.error(err.stack);
    res.status(500).send('Something broke!');
});

require('dotenv').config({ path: `/home/${USERNAME}/CCal_V2/WebGUI/.env` });
const BASIC_AUTH_USER = process.env.CCAL_WEBGUI_USER || 'ccal';
const BASIC_AUTH_PASS = process.env.CCAL_WEBGUI_PASS || 'raspberry';

// Basic Auth middleware
app.use((req, res, next) => {
    const auth = req.headers.authorization;
    if (!auth) {
        res.set('WWW-Authenticate', 'Basic realm="CCal WebGUI"');
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
    res.set('WWW-Authenticate', 'Basic realm="CCal WebGUI"');
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


        exec(`sudo bash /home/${USERNAME}/CCal_V2/WebGUI/setup_addons.sh`,
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

app.listen(PORT, '0.0.0.0', () => {
    console.log(`Server running at http://localhost:${PORT}`);
});
