"""Focused WCAG 2.x AA contrast tests for both built-in UI themes.

The computed palette pairs are intentionally opaque to avoid reliance on
variable browser-native input/control colors and screenshot-only checks.
"""
import re

from local_case_organizer.ui.local_case_organizer_ui_experience import EXPERIENCE_CSS


def luminance(hex_color: str) -> float:
    rgb = [int(hex_color[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    channels = [c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in rgb]
    return sum(c * w for c, w in zip(channels, (0.2126, 0.7152, 0.0722)))


def contrast(foreground: str, background: str) -> float:
    lighter, darker = sorted((luminance(foreground), luminance(background)), reverse=True)
    return (lighter + 0.05) / (darker + 0.05)


def palette(selector: str) -> dict[str, str]:
    matches = re.finditer(re.escape(selector) + r"\s*\{([^{}]+)\}", EXPERIENCE_CSS)
    blocks = [m.group(1) for m in matches if "--lco-control-bg" in m.group(1)]
    assert len(blocks) == 1, f"Missing or duplicate CSS theme palette: {selector}"
    return dict(re.findall(r"(--lco-[a-z-]+):\s*(#[0-9a-fA-F]{6})", blocks[0]))


def test_both_themes_text_and_primary_buttons_meet_aa():
    for theme in ("body", "body.lco-light"):
        color = palette(theme)
        assert contrast(color["--lco-control-fg"], color["--lco-control-bg"]) >= 4.5
        assert contrast(color["--lco-control-placeholder"], color["--lco-control-bg"]) >= 4.5
        assert contrast(color["--lco-contrast-primary-fg"], color["--lco-contrast-primary-bg"]) >= 4.5
        assert contrast(color["--lco-control-border"], color["--lco-control-bg"]) >= 3.0


def test_contrast_applies_to_real_widget_types_and_navigation():
    for selector in ("input[type=date]", "input[type=number]", "select option", "textarea",
                     "input::placeholder", "textarea::placeholder",
                     "input[type=file]::file-selector-button"):
        assert selector in EXPERIENCE_CSS
    assert "body.lco-light .next-step" in EXPERIENCE_CSS
    assert "body.lco-light .lco-feedback.ok" in EXPERIENCE_CSS
    assert "body.lco-light .lco-feedback.attention" in EXPERIENCE_CSS
    assert "button[aria-selected=true]:not(.ghost)" in EXPERIENCE_CSS
    assert "color-scheme:dark" in EXPERIENCE_CSS
    assert "color-scheme:light" in EXPERIENCE_CSS


def test_light_mode_status_colors_are_readable():
    background = "#fbf8f2"
    assert contrast("#544d44", background) >= 4.5
    assert contrast("#80571b", background) >= 4.5
    assert contrast("#256145", "#eef7f0") >= 4.5
    assert contrast("#81530d", "#fff4df") >= 4.5
