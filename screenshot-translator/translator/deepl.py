import requests

from .base import BaseTranslator


class DeepLTranslator(BaseTranslator):
    _API_URL = "https://api-free.deepl.com/v2/translate"

    def __init__(self, api_key: str, source: str = "EN", target: str = "ZH") -> None:
        self._api_key = api_key
        self._source = source
        self._target = target

    def translate(self, texts: list[str]) -> list[dict]:
        results: list[dict] = []
        for text in texts:
            try:
                resp = requests.post(
                    self._API_URL,
                    data={
                        "text": text,
                        "source_lang": self._source,
                        "target_lang": self._target,
                    },
                    headers={"Authorization": f"DeepL-Auth-Key {self._api_key}"},
                    timeout=10,
                )
                resp.raise_for_status()
                translated = resp.json()["translations"][0]["text"]
                results.append({"original": text, "translated": translated})
            except Exception:
                results.append({"original": text, "translated": text})
        return results
