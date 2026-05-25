import numpy as np
from PIL import Image, ImageDraw, ImageFont


def make_text_image(text: str = "Hello World") -> Image.Image:
    """Create a small white image with black text for OCR testing."""
    img = Image.new("RGB", (400, 100), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("arial.ttf", 24)
    except OSError:
        font = ImageFont.load_default()
    draw.text((20, 30), text, fill=(0, 0, 0), font=font)
    return img


def test_ocr_recognizes_english_text():
    """Integration test: requires paddleocr installed."""
    from ocr.engine import OCREngine

    engine = OCREngine(lang="en")
    img = make_text_image("Hello World")
    results = engine.recognize(img)

    assert len(results) >= 1
    texts = " ".join(r["text"] for r in results).lower()
    assert "hello" in texts or "world" in texts


def test_ocr_empty_image_returns_empty():
    from ocr.engine import OCREngine

    engine = OCREngine(lang="en")
    img = Image.new("RGB", (100, 100), color=(255, 255, 255))
    results = engine.recognize(img)
    assert results == []
