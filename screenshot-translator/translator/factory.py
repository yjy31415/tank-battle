from .base import BaseTranslator
from .google import GoogleTranslator
from .deepl import DeepLTranslator


def create_translator(name: str, **kwargs) -> BaseTranslator:
    if name == "deepl":
        api_key = kwargs.get("api_key", "")
        if not api_key:
            raise ValueError("DeepL requires an API key")
        return DeepLTranslator(api_key=api_key, source="EN", target="ZH")
    return GoogleTranslator(source="en", target="zh-CN")
