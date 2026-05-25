from deep_translator import GoogleTranslator as _GoogleTranslator

from .base import BaseTranslator


class GoogleTranslator(BaseTranslator):
    def __init__(self, source: str = "en", target: str = "zh-CN") -> None:
        self._source = source
        self._target = target
        self._translator = _GoogleTranslator(source=source, target=target)

    def translate(self, texts: list[str]) -> list[dict]:
        results: list[dict] = []
        for text in texts:
            try:
                translated = self._translator.translate(text)
                results.append({"original": text, "translated": translated})
            except Exception:
                results.append({"original": text, "translated": text})
        return results
