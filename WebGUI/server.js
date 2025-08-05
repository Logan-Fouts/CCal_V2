const express = require('express');
const bodyParser = require('body-parser');
const fs = require('fs');
const path = require('path');
const { exec } = require('child_process');

const app = express();
const PORT = 3000;

app.engine('html', require('ejs').renderFile);
app.set('view engine', 'ejs');
app.set('views', __dirname);

app.use(bodyParser.urlencoded({ extended: true }));
app.use(express.static(__dirname));

app.use((err, req, res, next) => {
    console.error(err.stack);
    res.status(500).send('Something broke!');
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
    
    if (req.body.GITHUB_USERNAME && req.body.GITHUB_USERNAME.trim() !== '') {
        newConfig.GITHUB_USERNAME = req.body.GITHUB_USERNAME.trim();
    }
    
    if (req.body.GITHUB_TOKEN && req.body.GITHUB_TOKEN.trim() !== '') {
        newConfig.GITHUB_TOKEN = req.body.GITHUB_TOKEN.trim();
    }
    
    if (req.body.STARTUP_ANIMATION !== undefined && 
        req.body.STARTUP_ANIMATION !== null && 
        req.body.STARTUP_ANIMATION !== '' && 
        !isNaN(Number(req.body.STARTUP_ANIMATION))) {
        newConfig.STARTUP_ANIMATION = Number(req.body.STARTUP_ANIMATION);
    }

    newConfig.TAILSCALE_ENABLE = req.body.TAILSCALE_ENABLE === 'on';
    newConfig.TAILSCALE_AUTHKEY = req.body.TAILSCALE_AUTHKEY || '';
    newConfig.PIHOLE_ENABLE = req.body.PIHOLE_ENABLE === 'on';
    newConfig.SYNCTHING_ENABLE = req.body.SYNCTHING_ENABLE === 'on';

    fs.writeFile(configPath, JSON.stringify(newConfig, null, 2), (err) => {
        if (err) {
            console.error(err);
            return res.status(500).send('Error saving config.');
        }
        
        exec('sudo bash /home/ccalv2/CCal_V2/WebGUI/setup_addons.sh', 
            { timeout: 30000 },
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
