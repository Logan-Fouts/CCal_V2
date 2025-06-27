const express = require('express');
const bodyParser = require('body-parser');
const fs = require('fs');
const path = require('path');
const { exec } = require('child_process');

const app = express();
const PORT = 3000;

app.use(bodyParser.urlencoded({ extended: true }));
app.use(express.static(__dirname));

app.post('/submit', (req, res) => {
    const configPath = path.join(__dirname, '../config.json');
    // Read the existing config first
    let existingConfig = {};
    try {
        existingConfig = JSON.parse(fs.readFileSync(configPath, 'utf8'));
    } catch (e) {
        // If file doesn't exist or is invalid, start with empty config
        existingConfig = {};
    }

    // Only update general settings if they are not empty/null
    const newConfig = { ...existingConfig };
    if (req.body.GITHUB_USERNAME && req.body.GITHUB_USERNAME.trim() !== '') {
        newConfig.GITHUB_USERNAME = req.body.GITHUB_USERNAME;
    }
    if (req.body.GITHUB_TOKEN && req.body.GITHUB_TOKEN.trim() !== '') {
        newConfig.GITHUB_TOKEN = req.body.GITHUB_TOKEN;
    }
    if (
        req.body.STARTUP_ANIMATION !== undefined &&
        req.body.STARTUP_ANIMATION !== null &&
        req.body.STARTUP_ANIMATION !== '' &&
        !isNaN(Number(req.body.STARTUP_ANIMATION))
    ) {
        newConfig.STARTUP_ANIMATION = Number(req.body.STARTUP_ANIMATION);
    }

    // Always update add-on settings
    newConfig.TAILSCALE_ENABLE = req.body.TAILSCALE_ENABLE === 'on';
    newConfig.TAILSCALE_AUTHKEY = req.body.TAILSCALE_AUTHKEY || '';
    newConfig.PIHOLE_ENABLE = req.body.PIHOLE_ENABLE === 'on';

    fs.writeFile(configPath, JSON.stringify(newConfig, null, 2), (err) => {
        if (err) {
            console.error(err);
            return res.status(500).send('Error saving config.');
        }
        // Call the shell script to setup addons
        exec('sudo bash setup_addons.sh', (error, stdout, stderr) => {
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

app.listen(PORT, () => {
    console.log(`Server running at http://localhost:${PORT}`);
});