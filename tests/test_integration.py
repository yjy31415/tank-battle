"""Integration tests for the core processing pipeline (no GUI required)."""
from PIL import Image, ImageDraw


def make_english_text_image() -> Image.Image:
    """Create a test image containing clear English text."""
    img = Image.new("RGB", (400, 80), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    draw.text((20, 25), "Welcome to the future", fill=(0, 0, 0))
    return img


def test_ocr_translate_render_pipeline():
    """Verify the full pipeline: OCR -> translate -> render overlay."""
    from ocr.engine import OCREngine
    from translator.google import GoogleTranslator
    from ui.result_window import _render_overlay

    img = make_english_text_image()

    # 1. OCR
    engine = OCREngine(lang="en")
    blocks = engine.recognize(img)
    assert len(blocks) >= 1, "OCR should find at least one text block"

    # 2. Prepare texts for translation
    texts = [b["text"] for b in blocks]

    # 3. Translate (with fallback if network unavailable)
    translator = GoogleTranslator(source="en", target="zh-CN")
    translations = translator.translate(texts)

    for t in translations:
        assert "original" in t
        assert "translated" in t
        assert len(t["translated"]) > 0

    # 4. Merge bbox
    for i, item in enumerate(translations):
        item["bbox"] = blocks[i]["bbox"]

    # 5. Render overlay
    result = _render_overlay(img, translations, display_mode="bilingual")
    assert result.size == img.size
