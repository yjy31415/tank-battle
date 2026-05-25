import json
import os
from dataclasses import dataclass, asdict, fields as dc_fields
from pathlib import Path

CONFIG_DIR = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming")) / "screenshot-translator"
CONFIG_FILE = CONFIG_DIR / "config.json"


@dataclass
class Config:
    hotkey: str = "Ctrl+Shift+T"
    translator: str = "google"
    display_mode: str = "bilingual"
    google_api_key: str = ""
    deepl_api_key: str = ""
    auto_start: bool = False
    ocr_lang: str = "en"

    @classmethod
    def load(cls) -> "Config":
        if CONFIG_FILE.exists():
            try:
                data = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
                known = {f.name for f in dc_fields(cls)}
                filtered = {k: v for k, v in data.items() if k in known}
                return cls(**filtered)
            except (json.JSONDecodeError, TypeError):
                pass
        return cls()

    def save(self) -> None:
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        CONFIG_FILE.write_text(
            json.dumps(asdict(self), indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
