from abc import ABC, abstractmethod


class BaseTranslator(ABC):
    @abstractmethod
    def translate(self, texts: list[str]) -> list[dict]:
        """Translate multiple text strings.

        Returns: [{"original": str, "translated": str}, ...]
        """
        ...
