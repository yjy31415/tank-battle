from PIL import Image, ImageDraw


def make_test_image() -> Image.Image:
    img = Image.new("RGB", (300, 100), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    draw.text((10, 20), "Hello World", fill=(0, 0, 0))
    return img


def test_render_overlay_bilingual():
    from ui.result_window import _render_overlay

    img = make_test_image()
    translations = [{
        "text": "Hello World",
        "original": "Hello World",
        "translated": "你好世界",
        "bbox": [[10, 10], [200, 10], [200, 40], [10, 40]],
    }]
    result = _render_overlay(img, translations, display_mode="bilingual")
    assert result.mode == "RGB"
    assert result.size == img.size


def test_render_overlay_translation_only():
    from ui.result_window import _render_overlay

    img = make_test_image()
    translations = [{
        "text": "Hello World",
        "original": "Hello World",
        "translated": "你好世界",
        "bbox": [[10, 10], [200, 10], [200, 40], [10, 40]],
    }]
    result = _render_overlay(img, translations, display_mode="translation_only")
    assert result.mode == "RGB"
    assert result.size == img.size


def test_render_overlay_empty_translations():
    from ui.result_window import _render_overlay

    img = make_test_image()
    result = _render_overlay(img, [], display_mode="bilingual")
    assert result.size == img.size
