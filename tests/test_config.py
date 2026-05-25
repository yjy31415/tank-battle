import json
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest


def test_config_defaults():
    from config import Config
    cfg = Config()
    assert cfg.hotkey == "Ctrl+Shift+T"
    assert cfg.translator == "google"
    assert cfg.display_mode == "bilingual"
    assert cfg.auto_start is False
    assert cfg.ocr_lang == "en"


def test_config_load_existing_file(tmp_path):
    from config import Config
    data = {
        "hotkey": "Ctrl+Shift+A",
        "translator": "deepl",
        "display_mode": "translation_only",
        "google_api_key": "test-key",
    }
    cfg_file = tmp_path / "config.json"
    cfg_file.write_text(json.dumps(data), encoding="utf-8")

    with patch("config.CONFIG_FILE", cfg_file):
        cfg = Config.load()
        assert cfg.hotkey == "Ctrl+Shift+A"
        assert cfg.translator == "deepl"
        assert cfg.display_mode == "translation_only"


def test_config_save_and_reload(tmp_path):
    from config import Config
    cfg_file = tmp_path / "config.json"

    with patch("config.CONFIG_FILE", cfg_file), patch("config.CONFIG_DIR", tmp_path):
        cfg = Config()
        cfg.hotkey = "Ctrl+Alt+X"
        cfg.save()

        loaded = Config.load()
        assert loaded.hotkey == "Ctrl+Alt+X"


def test_config_ignores_unknown_fields(tmp_path):
    from config import Config
    cfg_file = tmp_path / "config.json"
    cfg_file.write_text('{"hotkey": "A", "bogus_field": 123}', encoding="utf-8")

    with patch("config.CONFIG_FILE", cfg_file):
        cfg = Config.load()
        assert cfg.hotkey == "A"
        assert not hasattr(cfg, "bogus_field")
