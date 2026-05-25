from unittest.mock import patch, MagicMock

import pytest


class TestGoogleTranslator:
    def test_translate_returns_mapping(self):
        from translator.google import GoogleTranslator

        with patch.object(
            GoogleTranslator, "translate", return_value=[
                {"original": "hello", "translated": "你好"},
                {"original": "world", "translated": "世界"},
            ]
        ):
            t = GoogleTranslator()
            results = t.translate(["hello", "world"])
            assert results[0]["original"] == "hello"
            assert results[0]["translated"] == "你好"
            assert results[1]["original"] == "world"
            assert results[1]["translated"] == "世界"


class TestDeepLTranslator:
    def test_translate_success(self):
        from translator.deepl import DeepLTranslator

        mock_response = MagicMock()
        mock_response.json.return_value = {
            "translations": [{"text": "你好"}]
        }
        mock_response.raise_for_status.return_value = None

        with patch("translator.deepl.requests.post", return_value=mock_response):
            t = DeepLTranslator(api_key="fake-key")
            results = t.translate(["hello"])
            assert results[0]["original"] == "hello"
            assert results[0]["translated"] == "你好"

    def test_translate_failure_returns_original(self):
        from translator.deepl import DeepLTranslator

        with patch("translator.deepl.requests.post", side_effect=Exception("Boom")):
            t = DeepLTranslator(api_key="fake-key")
            results = t.translate(["hello"])
            assert results[0]["translated"] == "hello"


class TestFactory:
    def test_create_google_default(self):
        from translator.factory import create_translator
        from translator.google import GoogleTranslator

        t = create_translator("google")
        assert isinstance(t, GoogleTranslator)

    def test_create_deepl_requires_key(self):
        from translator.factory import create_translator

        with pytest.raises(ValueError, match="API key"):
            create_translator("deepl")

    def test_create_deepl_with_key(self):
        from translator.factory import create_translator
        from translator.deepl import DeepLTranslator

        t = create_translator("deepl", api_key="test")
        assert isinstance(t, DeepLTranslator)
