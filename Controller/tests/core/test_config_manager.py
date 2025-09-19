import os
import builtins
import logging
import threading
import tempfile
import shutil
import json
from led_control.core.config_manager import ConfigManager

CONFIG_FILE = "config/config.json"
CONFIG = {
    "GITHUB_USERNAME": "Logan-Fouts",
    "GITHUB_TOKEN": "blahblahblah",
    "STARTUP_ANIMATION": 3,
    "BRIGHTNESS": 0.6,
    "WEATHER_LAT": 0.0,
    "WEATHER_LON": 0.0,
    "OPENWEATHERMAP_API_KEY": "blebleble",
    "ON_TIME": 10,
    "OFF_TIME": 22,
    "TAILSCALE_ENABLE": True,
    "PIHOLE_ENABLE": False,
    "SYNCTHING_ENABLE": False,
}


def test_config_manager_init():
    cnf_man = ConfigManager(CONFIG_FILE)

    assert cnf_man is not None
    assert cnf_man.conf == CONFIG


def test_config_handles_missing_file():
    try:
        cnf_man = ConfigManager("config/missing.json")
    except FileNotFoundError as exc:
        assert str(exc) == "Config file 'config/missing.json' not found."


def test_config_handles_malformed_json(tmp_path):
    malformed_file = tmp_path / "malformed.json"
    malformed_file.write_text('{"GITHUB_USERNAME": "Logan-Fouts",')
    try:
        cnf_man = ConfigManager(malformed_file)
    except ValueError as exc:
        assert str(exc) == "Config file is not a valid JSON object."


def test_config_saves_and_updates(tmp_path):
    config_file = tmp_path / "config.json"
    config_file.write_text(json.dumps(CONFIG))
    cnf_man = ConfigManager(str(config_file))
    assert cnf_man.conf == CONFIG
    updated_conf = {
        "GITHUB_USERNAME": "Logan-Fouts",
        "GITHUB_TOKEN": "blahblahblah",
        "STARTUP_ANIMATION": 3,
        "BRIGHTNESS": 0.8,
        "WEATHER_LAT": 0.0,
        "WEATHER_LON": 0.0,
        "OPENWEATHERMAP_API_KEY": "blebleble",
        "ON_TIME": 10,
        "OFF_TIME": 22,
        "TAILSCALE_ENABLE": True,
        "PIHOLE_ENABLE": False,
        "SYNCTHING_ENABLE": False,
    }
    cnf_man.update_config(updated_conf)
    assert cnf_man.conf == updated_conf


def test_update_config_invalid_type(tmp_path, caplog):
    config_file = tmp_path / "config.json"
    config_file.write_text(json.dumps(CONFIG))
    cnf_man = ConfigManager(str(config_file))
    with caplog.at_level(logging.ERROR):
        result = cnf_man.update_config([1, 2, 3])
        assert not result
        assert "not a dictionary" in caplog.text


def test_update_config_atomic_write(tmp_path):
    config_file = tmp_path / "config.json"
    config_file.write_text(json.dumps(CONFIG))
    cnf_man = ConfigManager(str(config_file))
    updated_conf = dict(CONFIG)
    updated_conf["BRIGHTNESS"] = 0.9
    orig_move = shutil.move
    def fail_move(src, dst):
        raise OSError("Simulated move failure")
    shutil.move = fail_move
    try:
        result = cnf_man.update_config(updated_conf)
        assert not result
        with open(config_file) as f:
            data = json.load(f)
        assert data == CONFIG
    finally:
        shutil.move = orig_move


def test_logging_on_json_error(tmp_path, caplog):
    malformed_file = tmp_path / "malformed.json"
    malformed_file.write_text('{"GITHUB_USERNAME": "Logan-Fouts",')
    with caplog.at_level(logging.ERROR):
        try:
            ConfigManager(str(malformed_file))
        except ValueError:
            pass
        assert "Failed to parse config file" in caplog.text


def test_thread_safety(tmp_path):
    config_file = tmp_path / "config.json"
    config_file.write_text(json.dumps(CONFIG))
    cnf_man = ConfigManager(str(config_file))
    updated_conf1 = dict(CONFIG)
    updated_conf1["BRIGHTNESS"] = 0.1
    updated_conf2 = dict(CONFIG)
    updated_conf2["BRIGHTNESS"] = 0.2
    def update1():
        for _ in range(10):
            cnf_man.update_config(updated_conf1)
    def update2():
        for _ in range(10):
            cnf_man.update_config(updated_conf2)
    t1 = threading.Thread(target=update1)
    t2 = threading.Thread(target=update2)
    t1.start()
    t2.start()
    t1.join()
    t2.join()
    assert cnf_man.conf["BRIGHTNESS"] in (0.1, 0.2)
