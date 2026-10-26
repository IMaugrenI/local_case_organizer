"""Regression coverage for the B02 UI initialization and non-destructive areas."""
from local_case_organizer.ui.local_case_organizer_ui_fixups import FIXUP_SCRIPT
from local_case_organizer.ui.local_case_organizer_ui_experience import EXPERIENCE_CSS, EXPERIENCE_SCRIPT


def test_technical_section_placeholder_precedes_node_move():
    start = FIXUP_SCRIPT.index("const placeholder = document.createComment")
    moved = FIXUP_SCRIPT.index("if (helpfulActions) body.appendChild(helpfulActions)")
    done = FIXUP_SCRIPT.index("placeholder.replaceWith(details)")
    assert start < moved < done
    assert "anchor.parentNode.appendChild(details)" not in FIXUP_SCRIPT


def test_area_navigation_preserves_dom_and_stays_top():
    assert "brand.insertAdjacentElement('afterend',nav)" in EXPERIENCE_SCRIPT
    assert "groupNode(source(ref),view)" in EXPERIENCE_SCRIPT
    assert "node.hidden=(selected!==view)" in EXPERIENCE_SCRIPT
    assert "aria-current" in EXPERIENCE_SCRIPT
    assert "target.appendChild(node)" not in EXPERIENCE_SCRIPT
    assert ".wrap" in EXPERIENCE_CSS


def test_light_palette_includes_all_cards_and_inputs():
    assert "body.lco-light .hero" in EXPERIENCE_CSS
    assert "body.lco-light .card" in EXPERIENCE_CSS
    assert "body.lco-light .editor" in EXPERIENCE_CSS
    assert "body.lco-light table th" in EXPERIENCE_CSS
    assert "--lco-control-fg:#211d18" in EXPERIENCE_CSS
