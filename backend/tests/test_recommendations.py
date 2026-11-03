import pytest
from types import SimpleNamespace
from app.routers.recommendations import (
    COLOR_HARMONY_MAP,
    ROOM_BUDGET_WEIGHTS,
    get_color_match_priority,
    evaluate_ergonomic_compatibility,
    extract_in_session_preferences
)

def test_color_harmony_mappings():
    """Verify that every color family has defined primary, complementary, and accent palettes."""
    assert "royal navy blue" in COLOR_HARMONY_MAP
    assert "warm beige" in COLOR_HARMONY_MAP
    assert "charcoal grey" in COLOR_HARMONY_MAP
    assert "emerald green" in COLOR_HARMONY_MAP

    navy_harmony = COLOR_HARMONY_MAP["royal navy blue"]
    assert "royal navy blue" in navy_harmony["primary"]
    assert "warm beige" in navy_harmony["complementary"]
    assert len(navy_harmony["accent"]) > 0

def test_room_budget_weights():
    """Verify that room budget weights cover all standard room types."""
    assert "living_room" in ROOM_BUDGET_WEIGHTS
    assert "bedroom_master" in ROOM_BUDGET_WEIGHTS
    assert "kitchen" in ROOM_BUDGET_WEIGHTS
    assert "bathroom" in ROOM_BUDGET_WEIGHTS
    assert "balcony" in ROOM_BUDGET_WEIGHTS
    assert ROOM_BUDGET_WEIGHTS["living_room"] >= 0.25

def test_color_match_priority():
    """Verify color matching priority scoring logic."""
    assert get_color_match_priority(["Navy Blue"], ["navy blue"]) == 1
    assert get_color_match_priority(["White"], ["UnrelatedColor"]) == 3

def test_ergonomic_bed_nightstand_proportions():
    bed = SimpleNamespace(id="b1", name="Master King Bed", category="beds", subcategory=None, height=1000.0, width=1900.0, depth=2100.0)
    nightstand_good = SimpleNamespace(id="n1", name="Bedside Table", category="bedside_tables", subcategory="nightstand", height=480.0, width=450.0, depth=400.0)
    nightstand_tall = SimpleNamespace(id="n2", name="Bedside Chest", category="bedside_tables", subcategory="nightstand", height=800.0, width=500.0, depth=450.0)

    score_good, compat_good, reason_good = evaluate_ergonomic_compatibility(bed, nightstand_good)
    assert score_good > 0
    assert compat_good is True
    assert "mattress-level" in reason_good

    score_tall, compat_tall, reason_tall = evaluate_ergonomic_compatibility(bed, nightstand_tall)
    assert score_tall < 0
    assert "too tall" in reason_tall

def test_ergonomic_sofa_coffee_table_proportions():
    sofa = SimpleNamespace(id="s1", name="Living Sofa", category="sofas", subcategory=None, height=850.0, width=2100.0, depth=900.0)
    table_good = SimpleNamespace(id="t1", name="Coffee Table", category="coffee_tables", subcategory=None, height=440.0, width=1200.0, depth=600.0)
    table_oversized = SimpleNamespace(id="t2", name="Large Coffee Table", category="coffee_tables", subcategory=None, height=650.0, width=2200.0, depth=1000.0)

    score_good, compat_good, reason_good = evaluate_ergonomic_compatibility(sofa, table_good)
    assert score_good > 0
    assert compat_good is True
    assert "Ergonomic table height" in reason_good

    score_bad, compat_bad, reason_bad = evaluate_ergonomic_compatibility(sofa, table_oversized)
    assert score_bad < 0

def test_ergonomic_cabinets_depth():
    base = SimpleNamespace(id="c1", name="Base Cabinet", category="base_cabinets", subcategory=None, height=850.0, width=900.0, depth=600.0)
    wall_good = SimpleNamespace(id="w1", name="Wall Cabinet", category="wall_cabinets", subcategory=None, height=700.0, width=900.0, depth=350.0)
    wall_deep = SimpleNamespace(id="w2", name="Deep Wall Cabinet", category="wall_cabinets", subcategory=None, height=700.0, width=900.0, depth=650.0)

    score_good, compat_good, reason_good = evaluate_ergonomic_compatibility(base, wall_good)
    assert score_good > 0
    assert compat_good is True
    assert "head clearance" in reason_good

    score_bad, compat_bad, reason_bad = evaluate_ergonomic_compatibility(base, wall_deep)
    assert score_bad < 0
    assert compat_bad is False

def test_in_session_preference_extraction():
    prod = SimpleNamespace(finish="Oak Finish", primary_material="Velvet", style_tags=["Modern"])
    item1 = SimpleNamespace(custom_wood_finish="Oak", custom_fabric="Velvet", custom_color="Emerald Green", product=prod)
    room1 = SimpleNamespace(items=[item1])
    project = SimpleNamespace(rooms=[room1])

    prefs = extract_in_session_preferences(project)
    assert "oak" in prefs["woods"]
    assert "velvet" in prefs["fabrics"]
    assert "emerald green" in prefs["colors"]
    assert "modern" in prefs["styles"]
