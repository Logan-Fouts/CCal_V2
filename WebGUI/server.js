const express = require('express');
const bodyParser = require('body-parser');
const fs = require('fs');
const path = require('path');

const app = express();
const PORT = 3000;

app.use(bodyParser.urlencoded({ extended: true }));
app.use(express.static(__dirname));

app.post('/submit', (req, res) => {
    const configPath = path.join(__dirname, '../config.json');
    const newConfig = {
        GITHUB_USERNAME: req.body.GITHUB_USERNAME,
        GITHUB_TOKEN: req.body.GITHUB_TOKEN,
        STARTUP_ANIMATION: Number(req.body.STARTUP_ANIMATION),
        TAILSCALE_ENABLE: req.body.TAILSCALE_ENABLE === 'on',
        TAILSCALE_AUTHKEY: req.body.TAILSCALE_AUTHKEY || '',
        PIHOLE_ENABLE: req.body.PIHOLE_ENABLE === 'on',
        PIHOLE_WEBPASSWORD: req.body.PIHOLE_WEBPASSWORD || '',
        GITEA_ENABLE: req.body.GITEA_ENABLE === 'on',
        GITEA_ADMIN_USER: req.body.GITEA_ADMIN_USER || '',
        GITEA_ADMIN_PASS: req.body.GITEA_ADMIN_PASS || ''
    };
    fs.writeFile(configPath, JSON.stringify(newConfig, null, 2), (err) => {
        if (err) {
            console.error(err);
            return res.status(500).send('Error saving config.');
        }
        res.send('<h2>Config saved!</h2><a href="/">Back</a>');
    });
});

app.listen(PORT, () => {
    console.log(`Server running at http://localhost:${PORT}`);
});