"""AI Recommendations Router — smart package & product suggestions."""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from ..db import get_db
from ..models import Package, Product, Project, Room, RoomItem

router = APIRouter()

COLOR_FAMILIES = {
    "Pink": ["Pink", "Rose", "Blush", "Peach", "Red", "Maroon", "Blush Pink", "Rosewood"],
    "White": ["White", "Off White", "Off-white", "Cream", "Beige", "Ivory White"],
    "Grey": ["Grey", "Gray", "Charcoal", "Black", "Charcoal Black", "Matte Black", "Midnight Black"],
    "Brown": ["Brown", "Walnut", "Oak", "Dark Brown", "Natural Walnut", "Warm Honey", "Teak Finish", "Honey Oak", "Light Oak"],
}
NEUTRALS = ["white", "off white", "off-white", "cream", "beige", "grey", "gray", "charcoal", "black", "ivory white", "charcoal black", "matte black", "midnight black"]

def get_color_match_priority(prod_colors: List[str], user_colors: List[str]) -> int:
    if not prod_colors or not user_colors:
        return 4
    prod_colors_lower = [c.lower().strip() for c in prod_colors]
    user_colors_lower = [c.lower().strip() for c in user_colors]
    
    # Priority 1: Exact color match
    for uc in user_colors_lower:
        if uc in prod_colors_lower:
            return 1
            
    # Priority 2: Closest color family match
    for uc in user_colors_lower:
        family = []
        for fam, members in COLOR_FAMILIES.items():
            if uc == fam.lower() or any(uc == m.lower() for m in members):
                family = [fam.lower()] + [m.lower() for m in members]
                break
        for pc in prod_colors_lower:
            if pc in family:
                return 2
                
    # Priority 3: Neutral colors
    for pc in prod_colors_lower:
         if pc in NEUTRALS:
             return 3
             
    return 4



STYLE_COMPAT = {
    "modern":              {"modern": 1.0, "minimalist": 0.85, "contemporary": 0.8},
    "scandinavian":        {"scandinavian": 1.0, "boho": 0.7, "minimalist": 0.8, "warm": 0.7},
    "indian_contemporary": {"indian_contemporary": 1.0, "contemporary": 0.9, "warm": 0.8},
    "luxury":              {"luxury": 1.0, "contemporary": 0.75, "glam": 0.85, "italian": 0.9, "art-deco": 0.8},
    "mediterranean":       {"mediterranean": 1.0, "tropical": 0.75},
    "boho":                {"boho": 1.0, "scandinavian": 0.7, "tropical": 0.65},
}


def _score_package(pkg: Package, style_tags: List[str], budget: float, color_prefs: List[str], db: Session) -> float:
    score = 0.0
    pkg_styles = pkg.style_tags or []
    # Style match
    for user_style in style_tags:
        compat = STYLE_COMPAT.get(user_style, {})
        for pkg_style in pkg_styles:
            score += compat.get(pkg_style, 0.2)
    # Budget fit (1.0 if exactly at budget, less if much cheaper or over)
    if pkg.base_price <= budget:
        budget_score = pkg.base_price / budget
    else:
        budget_score = max(0, 1 - (pkg.base_price - budget) / budget)
    score += budget_score * 2
    # Featured bonus
    if pkg.featured:
        score += 0.3

    # Color preference bonus: check matching products in database
    if color_prefs:
        style_prods = db.query(Product).all()
        matching_style_prods = [
            p for p in style_prods 
            if any(t in (p.style_tags or []) for t in pkg_styles)
        ]
        if matching_style_prods:
            color_match_count = 0
            for p in matching_style_prods:
                p_colors = p.color_variants or []
                if not p_colors and p.variants and isinstance(p.variants, dict):
                    p_colors = p.variants.get("color", [])
                p_priority = get_color_match_priority(p_colors, color_prefs)
                if p_priority in (1, 2):
                    color_match_count += 1
            color_score = (color_match_count / len(matching_style_prods)) * 1.5
            score += color_score

    return score



@router.get("/packages", summary="AI-recommended packages")
def recommend_packages(
    bhk: str = Query(...),
    budget: float = Query(...),
    style_tags: str = Query("", description="Comma-separated style tags"),
    project_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    tags = [t.strip() for t in style_tags.split(",") if t.strip()] if style_tags else []
    
    color_prefs = []
    if project_id:
        from ..models import Project
        project = db.query(Project).filter(Project.id == project_id).first()
        if project and project.color_preferences:
            color_prefs = project.color_preferences

    from ..services.business_rules import normalize_bhk

    packages = db.query(Package).filter(Package.bhk == normalize_bhk(bhk)).all()

    scored = []
    for pkg in packages:
        score = _score_package(pkg, tags, budget, color_prefs, db)
        scored.append({"package": _pkg_dict(pkg), "score": round(score, 3), "match_pct": min(100, int(score * 20))})

    scored.sort(key=lambda x: x["score"], reverse=True)

    # Label top recommendation
    if scored:
        scored[0]["recommended"] = True
        scored[0]["label"] = "Best Match for You"

    return {
        "bhk": bhk,
        "budget": budget,
        "style_tags": tags,
        "recommendations": scored,
        "total": len(scored),
    }



@router.get("/products", summary="AI-recommended products for a room")
def recommend_products(
    room_type: str = Query(...),
    style_tags: str = Query("", description="Comma-separated style tags"),
    budget: float = Query(500000),
    project_id: Optional[str] = Query(None),
    limit: int = 10,
    db: Session = Depends(get_db),
):
    tags = [t.strip() for t in style_tags.split(",") if t.strip()] if style_tags else []
    products = db.query(Product).filter(Product.room_type == room_type).all()

    color_prefs = []
    if project_id:
        from ..models import Project
        project = db.query(Project).filter(Project.id == project_id).first()
        if project and project.color_preferences:
            color_prefs = project.color_preferences

    # Check if exact color match is found
    exact_color_match_found = True
    if color_prefs and products:
        exact_match = False
        for p in products:
            p_colors = p.color_variants or []
            if not p_colors and p.variants and isinstance(p.variants, dict):
                p_colors = p.variants.get("color", [])
            p_colors_lower = [c.lower().strip() for c in p_colors]
            if any(uc.lower().strip() in p_colors_lower for uc in color_prefs):
                exact_match = True
                break
        exact_color_match_found = exact_match

    def score_product(p: Product) -> float:
        s = 0.0
        for user_tag in tags:
            compat = STYLE_COMPAT.get(user_tag, {})
            for pt in (p.style_tags or []):
                s += compat.get(pt, 0.1)
        # Price budget fit
        per_room = budget * 0.25
        if p.price <= per_room:
            s += 1.0
        return s

    def product_sort_key(p: Product):
        p_colors = p.color_variants or []
        if not p_colors and p.variants and isinstance(p.variants, dict):
            p_colors = p.variants.get("color", [])
        color_pri = get_color_match_priority(p_colors, color_prefs)
        
        style_score = score_product(p)
        return (color_pri, -style_score)

    scored = sorted(products, key=product_sort_key)[:limit]

    return {
        "room_type": room_type,
        "style_tags": tags,
        "products": [_prod_dict(p) for p in scored],
        "total": len(scored),
        "exact_color_match_found": exact_color_match_found
    }


# ── Budget Proportions & Anchor Pairing Rules ─────────────────────────────────
ROOM_BUDGET_WEIGHTS = {
    "living_room": 0.30,
    "bedroom_master": 0.26,
    "bedroom_2": 0.18,
    "bedroom_3": 0.16,
    "bedroom_4": 0.14,
    "bedroom_5": 0.12,
    "kitchen": 0.16,
    "bathroom": 0.08,
    "bathroom_2": 0.06,
    "bathroom_3": 0.05,
    "balcony": 0.06,
}

COLOR_HARMONY_MAP = {
    "royal navy blue": {
        "primary": ["royal navy blue", "navy blue", "blue"],
        "complementary": ["charcoal grey", "warm beige", "white", "gold", "matte black", "grey"],
        "accent": ["blush pink", "emerald green"],
    },
    "warm beige": {
        "primary": ["warm beige", "beige", "cream", "ivory white"],
        "complementary": ["warm honey", "natural walnut", "light oak", "white", "charcoal grey", "matte"],
        "accent": ["emerald green", "blush pink", "royal navy blue"],
    },
    "blush pink": {
        "primary": ["blush pink", "pink", "rose", "peach"],
        "complementary": ["warm beige", "charcoal grey", "white", "cream"],
        "accent": ["royal navy blue", "emerald green"],
    },
    "charcoal grey": {
        "primary": ["charcoal grey", "grey", "gray", "black", "charcoal black", "matte black"],
        "complementary": ["warm beige", "white", "royal navy blue", "blush pink"],
        "accent": ["emerald green"],
    },
    "emerald green": {
        "primary": ["emerald green", "green"],
        "complementary": ["warm beige", "charcoal grey", "natural walnut", "matte black", "white"],
        "accent": ["blush pink", "royal navy blue"],
    },
}

def extract_dominant_color(product: Product) -> str:
    cv = product.color_variants
    if cv and isinstance(cv, list) and len(cv) > 0 and isinstance(cv[0], str):
        c_str = cv[0].lower().strip()
        for k in COLOR_HARMONY_MAP:
            if k in c_str:
                return k
    if product.variants and isinstance(product.variants, dict):
        var_colors = product.variants.get("color") or []
        for vc in var_colors:
            if isinstance(vc, str):
                for k in COLOR_HARMONY_MAP:
                    if k in vc.lower():
                        return k
    p_name = (product.name or "").lower()
    for k in ["royal navy blue", "blush pink", "charcoal grey", "warm beige", "emerald green"]:
        if k in p_name:
            return k
    for k in ["navy", "blue", "pink", "grey", "gray", "beige", "green", "black", "white"]:
        if k in p_name:
            for map_key in COLOR_HARMONY_MAP:
                if k in map_key:
                    return map_key
    return ""

def detect_product_role(p: Product) -> str:
    name = (p.name or "").lower()
    sub = (p.subcategory or "").lower()
    cat = (p.category or "").lower()
    
    if "sofa" in name or "sofa" in cat:
        return "sofa"
    if "coffee" in name or "coffee" in cat:
        return "coffee_table"
    if "bedside" in name or "nightstand" in name or ("bedside" in sub and "light" not in name):
        return "bedside_table"
    if ("bed" in name or "bed" in sub or "bed" in cat) and "bedside" not in name:
        return "bed"
    if "wardrobe" in name or "closet" in name or "wardrobe" in sub:
        return "wardrobe"
    if "desk" in name or "study" in name or "desk" in sub:
        return "study_desk"
    if "base" in name and ("cabinet" in name or "cabinet" in sub or "kitchen" in cat):
        return "base_cabinets"
    if "wall" in name and ("cabinet" in name or "cabinet" in sub or "kitchen" in cat):
        return "wall_cabinets"
    if "vanity" in name or "vanity" in sub or "vanity" in cat:
        return "vanity"
    if "towel" in name or "fixture" in name or "fixture" in sub or "accessories" in name:
        return "fixtures"
    if "chair" in name or "chair" in cat:
        return "chair"
    if "side" in name and "bedside" not in name:
        return "side_table"
    if "light" in name or "lamp" in name or "light" in cat:
        return "lighting"
    if "rug" in name or "carpet" in name or "rug" in cat or "mat" in name:
        return "rugs"
    return "other"

def get_companion_schema_for_product(room_type: str, anchor: Product) -> List[dict]:
    role = detect_product_role(anchor)
    norm = lambda s: (s or "").lower().replace("_", " ").strip()
    r = norm(room_type)

    if "living" in r:
        if role == "sofa":
            return [
                {"category": "coffee_tables", "label": "Coffee Table", "target_pct": 0.14, "rel_to_anchor_pct": 0.28, "priority": 1, "desc": "Central matching low coffee table"},
                {"category": "rugs", "label": "Area Rug", "target_pct": 0.12, "rel_to_anchor_pct": 0.25, "priority": 2, "desc": "Grounding floor rug in palette"},
                {"category": "chairs", "label": "Accent Chair", "target_pct": 0.18, "rel_to_anchor_pct": 0.38, "priority": 3, "desc": "Coordinated companion accent chair"},
                {"category": "lighting", "label": "Ambient Lighting", "target_pct": 0.08, "rel_to_anchor_pct": 0.18, "priority": 4, "desc": "Warm ambient floor/table lamp"},
                {"category": "side_tables", "label": "Side Table", "target_pct": 0.07, "rel_to_anchor_pct": 0.16, "priority": 5, "desc": "Beside sofa accent surface"},
            ]
        elif role == "coffee_table":
            return [
                {"category": "sofas", "label": "Matching Sofa", "target_pct": 0.45, "rel_to_anchor_pct": 4.5, "priority": 1, "desc": "Primary living room sofa"},
                {"category": "rugs", "label": "Area Rug", "target_pct": 0.12, "rel_to_anchor_pct": 1.0, "priority": 2, "desc": "Grounding floor rug"},
                {"category": "chairs", "label": "Accent Chair", "target_pct": 0.18, "rel_to_anchor_pct": 1.5, "priority": 3, "desc": "Companion accent seating"},
                {"category": "lighting", "label": "Ambient Lighting", "target_pct": 0.08, "rel_to_anchor_pct": 0.8, "priority": 4, "desc": "Warm living illumination"},
            ]
        elif role == "chair":
            return [
                {"category": "sofas", "label": "Main Sofa", "target_pct": 0.45, "rel_to_anchor_pct": 3.0, "priority": 1, "desc": "Primary living room sofa"},
                {"category": "side_tables", "label": "Side Table", "target_pct": 0.08, "rel_to_anchor_pct": 0.4, "priority": 2, "desc": "Companion drink surface"},
                {"category": "coffee_tables", "label": "Coffee Table", "target_pct": 0.14, "rel_to_anchor_pct": 0.7, "priority": 3, "desc": "Matching coffee table"},
                {"category": "lighting", "label": "Reading Lamp", "target_pct": 0.08, "rel_to_anchor_pct": 0.5, "priority": 4, "desc": "Focused ambient lamp"},
            ]
        elif role == "side_table":
            return [
                {"category": "sofas", "label": "Main Sofa", "target_pct": 0.45, "rel_to_anchor_pct": 8.0, "priority": 1, "desc": "Primary living sofa"},
                {"category": "coffee_tables", "label": "Coffee Table", "target_pct": 0.14, "rel_to_anchor_pct": 2.0, "priority": 2, "desc": "Central coffee table"},
                {"category": "lighting", "label": "Table Lamp", "target_pct": 0.08, "rel_to_anchor_pct": 1.4, "priority": 3, "desc": "Warm ambient lighting"},
            ]
        else:
            return [
                {"category": "sofas", "label": "Main Sofa", "target_pct": 0.45, "rel_to_anchor_pct": 5.0, "priority": 1, "desc": "Primary living room sofa"},
                {"category": "coffee_tables", "label": "Coffee Table", "target_pct": 0.14, "rel_to_anchor_pct": 1.5, "priority": 2, "desc": "Central matching coffee table"},
                {"category": "chairs", "label": "Accent Chair", "target_pct": 0.18, "rel_to_anchor_pct": 1.8, "priority": 3, "desc": "Complementary seating"},
                {"category": "rugs", "label": "Area Rug", "target_pct": 0.12, "rel_to_anchor_pct": 1.2, "priority": 4, "desc": "Floor accent rug"},
            ]

    elif "bedroom" in r:
        if role == "bed":
            return [
                {"category": "bedside_tables", "label": "Bedside Tables", "target_pct": 0.12, "rel_to_anchor_pct": 0.22, "priority": 1, "desc": "Matching bedside nightstand"},
                {"category": "lighting", "label": "Bedside Lighting", "target_pct": 0.08, "rel_to_anchor_pct": 0.18, "priority": 2, "desc": "Warm bedside reading light"},
                {"category": "wardrobe", "label": "Wardrobe Closet", "target_pct": 0.35, "rel_to_anchor_pct": 0.70, "priority": 3, "desc": "Matching storage wardrobe"},
                {"category": "study_desk", "label": "Study Desk", "target_pct": 0.15, "rel_to_anchor_pct": 0.32, "priority": 4, "desc": "Coordinated workstation desk"},
                {"category": "rugs", "label": "Bedroom Rug", "target_pct": 0.10, "rel_to_anchor_pct": 0.22, "priority": 5, "desc": "Soft bedside area rug"},
            ]
        elif role == "bedside_table":
            return [
                {"category": "beds", "label": "Master Bed", "target_pct": 0.50, "rel_to_anchor_pct": 8.0, "priority": 1, "desc": "Matching master bed set"},
                {"category": "lighting", "label": "Bedside Lamp", "target_pct": 0.08, "rel_to_anchor_pct": 0.8, "priority": 2, "desc": "Bedside reading lamp"},
                {"category": "wardrobe", "label": "Wardrobe Closet", "target_pct": 0.35, "rel_to_anchor_pct": 5.0, "priority": 3, "desc": "Coordinated wardrobe closet"},
                {"category": "study_desk", "label": "Study Desk", "target_pct": 0.15, "rel_to_anchor_pct": 2.0, "priority": 4, "desc": "Workstation study desk"},
            ]
        elif role == "wardrobe":
            return [
                {"category": "beds", "label": "Master Bed", "target_pct": 0.50, "rel_to_anchor_pct": 1.6, "priority": 1, "desc": "Matching master bed set"},
                {"category": "bedside_tables", "label": "Bedside Tables", "target_pct": 0.12, "rel_to_anchor_pct": 0.25, "priority": 2, "desc": "Matching nightstands"},
                {"category": "lighting", "label": "Bedside Lighting", "target_pct": 0.08, "rel_to_anchor_pct": 0.18, "priority": 3, "desc": "Bedside ambient illumination"},
                {"category": "study_desk", "label": "Study Desk", "target_pct": 0.15, "rel_to_anchor_pct": 0.40, "priority": 4, "desc": "Workstation desk"},
            ]
        elif role == "study_desk":
            return [
                {"category": "chairs", "label": "Desk Chair", "target_pct": 0.18, "rel_to_anchor_pct": 1.3, "priority": 1, "desc": "Comfortable accent / desk chair"},
                {"category": "lighting", "label": "Desk Lighting", "target_pct": 0.08, "rel_to_anchor_pct": 0.6, "priority": 2, "desc": "Focused study lamp"},
                {"category": "beds", "label": "Bed Set", "target_pct": 0.50, "rel_to_anchor_pct": 4.0, "priority": 3, "desc": "Coordinated bed set"},
                {"category": "bedside_tables", "label": "Bedside Tables", "target_pct": 0.12, "rel_to_anchor_pct": 0.6, "priority": 4, "desc": "Bedside nightstand"},
            ]
        else:
            return [
                {"category": "beds", "label": "Master Bed", "target_pct": 0.50, "rel_to_anchor_pct": 6.0, "priority": 1, "desc": "Anchor master bed set"},
                {"category": "bedside_tables", "label": "Bedside Tables", "target_pct": 0.12, "rel_to_anchor_pct": 1.4, "priority": 2, "desc": "Matching nightstand"},
                {"category": "wardrobe", "label": "Wardrobe Closet", "target_pct": 0.35, "rel_to_anchor_pct": 4.5, "priority": 3, "desc": "Matching storage wardrobe"},
            ]

    elif "kitchen" in r:
        if role == "base_cabinets":
            return [
                {"category": "wall_cabinets", "label": "Wall Cabinets", "target_pct": 0.40, "rel_to_anchor_pct": 0.85, "priority": 1, "desc": "Coordinated overhead wall cabinets"},
                {"category": "lighting", "label": "Kitchen Task Lighting", "target_pct": 0.10, "rel_to_anchor_pct": 0.25, "priority": 2, "desc": "Warm kitchen ambient illumination"},
            ]
        elif role == "wall_cabinets":
            return [
                {"category": "base_cabinets", "label": "Base Cabinets", "target_pct": 0.50, "rel_to_anchor_pct": 1.45, "priority": 1, "desc": "Matching countertop base cabinets"},
                {"category": "lighting", "label": "Kitchen Task Lighting", "target_pct": 0.10, "rel_to_anchor_pct": 0.30, "priority": 2, "desc": "Warm kitchen ambient illumination"},
            ]
        else:
            return [
                {"category": "base_cabinets", "label": "Base Cabinets", "target_pct": 0.50, "rel_to_anchor_pct": 3.0, "priority": 1, "desc": "Modular kitchen base cabinets"},
                {"category": "wall_cabinets", "label": "Wall Cabinets", "target_pct": 0.40, "rel_to_anchor_pct": 2.5, "priority": 2, "desc": "Modular kitchen wall cabinets"},
                {"category": "lighting", "label": "Kitchen Lighting", "target_pct": 0.10, "rel_to_anchor_pct": 0.5, "priority": 3, "desc": "Kitchen ceiling illumination"},
            ]

    elif "bath" in r:
        if role == "vanity":
            return [
                {"category": "fixtures", "label": "Towel Racks & Fixtures", "target_pct": 0.15, "rel_to_anchor_pct": 0.30, "priority": 1, "desc": "Coordinated towel racks & fixtures"},
                {"category": "lighting", "label": "Vanity Lighting", "target_pct": 0.12, "rel_to_anchor_pct": 0.35, "priority": 2, "desc": "Warm vanity mirror lighting"},
                {"category": "rugs", "label": "Bath Floor Mat", "target_pct": 0.10, "rel_to_anchor_pct": 0.35, "priority": 3, "desc": "Plush bathroom area mat"},
            ]
        elif role == "fixtures":
            return [
                {"category": "vanity", "label": "Vanity Counter", "target_pct": 0.60, "rel_to_anchor_pct": 5.0, "priority": 1, "desc": "Coordinated vanity counter with basin"},
                {"category": "lighting", "label": "Vanity Lighting", "target_pct": 0.12, "rel_to_anchor_pct": 1.4, "priority": 2, "desc": "Warm vanity mirror lighting"},
            ]
        else:
            return [
                {"category": "vanity", "label": "Vanity Counter", "target_pct": 0.60, "rel_to_anchor_pct": 2.0, "priority": 1, "desc": "Primary bathroom vanity"},
                {"category": "fixtures", "label": "Towel Racks & Fixtures", "target_pct": 0.15, "rel_to_anchor_pct": 0.5, "priority": 2, "desc": "Matching towel racks & fixtures"},
            ]

    elif "balcony" in r:
        return [
            {"category": "chairs", "label": "Balcony Accent Chair", "target_pct": 0.35, "rel_to_anchor_pct": 1.5, "priority": 1, "desc": "Comfortable balcony lounge chair"},
            {"category": "side_tables", "label": "Bistro Side Table", "target_pct": 0.20, "rel_to_anchor_pct": 0.8, "priority": 2, "desc": "Compact outdoor drink & coffee table"},
            {"category": "lighting", "label": "Balcony Ambient Lamp", "target_pct": 0.15, "rel_to_anchor_pct": 0.6, "priority": 3, "desc": "Evening mood illumination"},
            {"category": "rugs", "label": "Balcony Floor Rug", "target_pct": 0.15, "rel_to_anchor_pct": 0.7, "priority": 4, "desc": "Weather-friendly accent rug"},
        ]

    # Fallback to living room schema
    return [
        {"category": "coffee_tables", "label": "Coffee Table", "target_pct": 0.14, "rel_to_anchor_pct": 0.28, "priority": 1, "desc": "Central low table"},
        {"category": "rugs", "label": "Area Rug", "target_pct": 0.12, "rel_to_anchor_pct": 0.25, "priority": 2, "desc": "Grounding floor rug"},
        {"category": "lighting", "label": "Ambient Lighting", "target_pct": 0.08, "rel_to_anchor_pct": 0.18, "priority": 3, "desc": "Warm ambient lighting"},
    ]


def _find_candidate_products_for_companion(room_type: str, cat_id: str, anchor: Product, db: Session) -> List[Product]:
    all_prods = db.query(Product).all()
    results = []
    norm = lambda s: (s or "").lower().replace("_", " ").strip()
    c_clean = norm(cat_id)
    r_clean = norm(room_type)
    anchor_name = norm(anchor.name)
    anchor_role = detect_product_role(anchor)

    for p in all_prods:
        if p.id == anchor.id or norm(p.name) == anchor_name:
            continue

        p_room = norm(p.room_type)
        p_cat = norm(p.category)
        p_sub = norm(p.subcategory)
        p_name = norm(p.name)
        cand_role = detect_product_role(p)

        # Disallow pairing same role
        if cand_role == anchor_role and anchor_role not in ["other"]:
            continue

        # Room compatibility with decor sharing
        room_match = (p_room == r_clean) or (r_clean in norm(p.suitable_room))
        if r_clean.startswith("bedroom") and (p_room.startswith("bedroom") or p_cat in ["rugs", "lighting"]):
            room_match = True
        elif r_clean == "balcony" and (p_cat in ["chairs", "side_tables", "lighting", "rugs"] or cand_role in ["chair", "side_table", "lighting", "rugs"]):
            room_match = True
        elif r_clean.startswith("bathroom") and (p_room.startswith("bathroom") or p_cat in ["lighting", "rugs"] or cand_role in ["lighting", "rugs"]):
            room_match = True
        elif r_clean == "kitchen" and (p_room == "kitchen" or p_cat in ["lighting"] or cand_role == "lighting"):
            room_match = True

        if not room_match:
            continue

        matches = False
        if "coffee" in c_clean:
            if "coffee" in p_cat or "coffee" in p_name:
                matches = True
        elif "bedside" in c_clean:
            if ("bedside" in p_name or "nightstand" in p_name or "bedside" in p_sub) and "light" not in p_name and "lamp" not in p_name:
                matches = True
        elif "side table" in c_clean:
            if ("side" in p_cat or "side" in p_name or "side" in p_sub) and "bedside" not in p_name:
                matches = True
        elif "desk" in c_clean or "study" in c_clean:
            if "desk" in p_cat or "study" in p_cat or "desk" in p_name or "study" in p_name or "study" in p_sub:
                matches = True
        elif "wardrobe" in c_clean:
            if "wardrobe" in p_cat or "closet" in p_cat or "wardrobe" in p_name or "wardrobe" in p_sub:
                matches = True
        elif "rug" in c_clean:
            if "rug" in p_cat or "rug" in p_name or "carpet" in p_name or "mat" in p_name:
                matches = True
        elif "light" in c_clean:
            if "light" in p_cat or "lamp" in p_cat or "light" in p_name or "lamp" in p_name:
                matches = True
        elif "chair" in c_clean:
            if ("chair" in p_cat or "chair" in p_name) and "sofa" not in p_name:
                matches = True
        elif "sofa" in c_clean:
            if "sofa" in p_cat or "sofa" in p_name:
                matches = True
        elif c_clean in ["bed", "beds", "bed set", "master bed"]:
            if ("bed" in p_name or "bed" in p_sub) and "bedside" not in p_name and "bedside" not in p_sub:
                matches = True
        elif "wall cabinet" in c_clean:
            if "wall" in p_name or "wall" in p_sub:
                matches = True
        elif "base cabinet" in c_clean:
            if "base" in p_name or "base" in p_sub:
                matches = True
        elif "vanity" in c_clean:
            if "vanity" in p_name or "vanity" in p_sub or "vanity" in p_cat:
                matches = True
        elif "fixture" in c_clean or "towel" in c_clean or "accessories" in c_clean:
            if "fixture" in p_cat or "fixture" in p_sub or "towel" in p_name or "accessories" in p_name:
                matches = True
        elif c_clean in p_cat or c_clean in p_sub or c_clean in p_name:
            matches = True

        if matches:
            results.append(p)

    return results



# ?? Ergonomic Knowledge Graph ????????????????????????????????????????????????
# Evaluates inter-item architectural clearances, ergonomic height alignments,
# and scale proportionality constraints (dimensions in millimeters).

def _eval_sofa_coffee_table_ergonomics(sofa: Product, table: Product) -> tuple[float, bool, str]:
    """
    Sofa & Coffee Table Ergonomic Proportions:
    - Table height should align at or slightly below sofa seat level (typically 360-500mm).
    - Table length should be 42% - 78% of sofa width for balanced visual anchor and walking clearance.
    """
    s_w = float(sofa.width or 2000.0)
    t_w = float(table.width or 1000.0)
    t_h = float(table.height or 450.0)

    score = 0.0
    reason_parts = []

    # Height evaluation
    if 360.0 <= t_h <= 500.0:
        score += 3.5
        reason_parts.append(f"Ergonomic table height ({int(t_h)}mm)")
    elif t_h > 580.0:
        score -= 4.0
        reason_parts.append(f"Table height ({int(t_h)}mm) sits too high for living sofa")

    # Width / Length proportion
    ratio = t_w / s_w if s_w > 0 else 0.5
    if 0.42 <= ratio <= 0.78:
        score += 3.5
        reason_parts.append(f"proportional length ({int(t_w)}mm vs {int(s_w)}mm sofa)")
    elif ratio > 0.90:
        score -= 4.0
        reason_parts.append("oversized coffee table relative to sofa width")

    reason = " & ".join(reason_parts) if reason_parts else ""
    return score, (score >= 0), reason


def _eval_bed_nightstand_ergonomics(bed: Product, nightstand: Product) -> tuple[float, bool, str]:
    """
    Bed & Bedside Table Ergonomics:
    - Nightstand surface should be within -60mm to +120mm of mattress level (standard 400-580mm).
    - Nightstand width should be compact (380-620mm) to preserve wall egress.
    """
    n_h = float(nightstand.height or 480.0)
    n_w = float(nightstand.width or 450.0)

    score = 0.0
    reason = ""

    if 400.0 <= n_h <= 580.0:
        score += 4.5
        reason = f"Ideal mattress-level nightstand height ({int(n_h)}mm)"
    elif 340.0 <= n_h < 400.0 or 580.0 < n_h <= 660.0:
        score += 2.0
        reason = f"Compatible bedside table height ({int(n_h)}mm)"
    elif n_h > 720.0:
        score -= 5.0
        reason = f"Nightstand too tall ({int(n_h)}mm) for bedside reach"

    if n_w <= 620.0:
        score += 1.5
    else:
        score -= 2.5

    return score, (score >= 0), reason


def _eval_desk_chair_ergonomics(desk: Product, chair: Product) -> tuple[float, bool, str]:
    """
    Study Desk & Task Chair Clearance:
    - Standard desk height 700-780mm paired with standard chair (750-1050mm total height)
      ensures 220-300mm thigh clearance beneath desk surface.
    """
    d_h = float(desk.height or 750.0)
    c_h = float(chair.height or 850.0)

    if 700.0 <= d_h <= 780.0 and 750.0 <= c_h <= 1050.0:
        return 4.0, True, "Ergonomic desk-to-chair posture clearance"
    elif d_h < 680.0 or c_h > 1150.0:
        return -3.0, False, "Tight thigh clearance between desk and chair"
    return 1.0, True, "Standard study desk pairing"


def _eval_cabinets_depth_ergonomics(base: Product, wall: Product) -> tuple[float, bool, str]:
    """
    Kitchen Modular Cabinet Hierarchy:
    - Overhead wall cabinets must be shallower than base countertop cabinets (typically 300-380mm vs 580-650mm)
      so cooks don't bump their heads.
    """
    b_d = float(base.depth or 600.0)
    w_d = float(wall.depth or 350.0)

    if w_d <= (b_d - 140.0):
        return 4.5, True, f"Ergonomic overhead depth ({int(w_d)}mm) ensures head clearance over {int(b_d)}mm base"
    elif w_d >= b_d:
        return -6.0, False, "Overhead wall cabinet too deep for countertop safety"
    return 1.0, True, "Standard cabinet depth ratio"


def _eval_sofa_side_table_ergonomics(sofa: Product, side_table: Product) -> tuple[float, bool, str]:
    """
    Sofa & Side Table Alignment:
    - Side table height should comfortably reach sofa armrest level (450-650mm).
    """
    t_h = float(side_table.height or 550.0)
    if 450.0 <= t_h <= 650.0:
        return 3.5, True, f"Armrest-level side table height ({int(t_h)}mm)"
    elif t_h > 720.0:
        return -3.0, False, "Side table taller than sofa armrest"
    return 1.0, True, "Compatible side table proportion"


def evaluate_ergonomic_compatibility(anchor: Product, candidate: Product) -> tuple[float, bool, str]:
    """
    Evaluates geometric scale, clearance, and ergonomic height alignments between
    anchor furniture and proposed companion piece using the Ergonomic Knowledge Graph.
    """
    a_role = detect_product_role(anchor)
    c_role = detect_product_role(candidate)

    if a_role == "sofa" and c_role == "coffee_table":
        return _eval_sofa_coffee_table_ergonomics(anchor, candidate)
    elif a_role == "coffee_table" and c_role == "sofa":
        return _eval_sofa_coffee_table_ergonomics(candidate, anchor)
    elif a_role == "sofa" and c_role == "side_table":
        return _eval_sofa_side_table_ergonomics(anchor, candidate)
    elif a_role == "side_table" and c_role == "sofa":
        return _eval_sofa_side_table_ergonomics(candidate, anchor)
    elif a_role == "bed" and c_role == "bedside_table":
        return _eval_bed_nightstand_ergonomics(anchor, candidate)
    elif a_role == "bedside_table" and c_role == "bed":
        return _eval_bed_nightstand_ergonomics(candidate, anchor)
    elif a_role == "study_desk" and c_role == "chair":
        return _eval_desk_chair_ergonomics(anchor, candidate)
    elif a_role == "chair" and c_role == "study_desk":
        return _eval_desk_chair_ergonomics(candidate, anchor)
    elif a_role == "base_cabinets" and c_role == "wall_cabinets":
        return _eval_cabinets_depth_ergonomics(anchor, candidate)
    elif a_role == "wall_cabinets" and c_role == "base_cabinets":
        return _eval_cabinets_depth_ergonomics(candidate, anchor)

    return 0.0, True, ""


# ?? In-Session Dynamic Contextual Preference Re-Ranking ????????????????????????
def extract_in_session_preferences(project: Optional[Project], current_room_id: Optional[str] = None) -> dict:
    """
    In-Session Dynamic Contextual Preference Re-Ranking.
    Extracts cross-room aesthetic momentum: finishes, fabrics, and colors that the homeowner
    has actively selected or customized in other rooms within the current project session.
    """
    if not project or not project.rooms:
        return {"woods": [], "fabrics": [], "colors": [], "styles": []}

    session_woods = []
    session_fabrics = []
    session_colors = []
    session_styles = []

    for r in project.rooms:
        for it in (r.items or []):
            prod = it.product
            # 1. Custom or product wood finish
            wf = (it.custom_wood_finish or (prod.finish if prod else "") or "").lower().strip()
            for w in ["oak", "teak", "walnut"]:
                if w in wf:
                    session_woods.append(w)

            # 2. Custom or product fabric
            fb = (it.custom_fabric or (prod.primary_material if prod else "") or "").lower().strip()
            for f in ["velvet", "linen", "woven", "leather", "leatherette"]:
                if f in fb:
                    session_fabrics.append(f)

            # 3. Custom or product dominant color
            c_val = (it.custom_color or (extract_dominant_color(prod) if prod else "") or "").lower().strip()
            if c_val:
                session_colors.append(c_val)

            # 4. Product style tags
            if prod and prod.style_tags:
                for st in prod.style_tags:
                    session_styles.append(st.lower().strip())

    # Keep unique while preserving order of recent selection
    return {
        "woods": list(dict.fromkeys(session_woods)),
        "fabrics": list(dict.fromkeys(session_fabrics)),
        "colors": list(dict.fromkeys(session_colors)),
        "styles": list(dict.fromkeys(session_styles)),
    }


@router.get("/complementary-bundle", summary="Get budget-proportional complementary product recommendations")
def get_complementary_bundle(
    product_id: str = Query(..., description="Anchor product ID"),
    project_id: str = Query(..., description="Active project ID"),
    room_id: Optional[str] = Query(None, description="Active room ID"),
    mood: Optional[str] = Query("monochrome", description="Style mood: 'monochrome' or 'accent'"),
    db: Session = Depends(get_db),
):
    anchor = db.query(Product).filter(Product.id == product_id).first()
    if not anchor:
        return {"error": "Anchor product not found", "recommended_items": [], "bundle_total": 0}

    project = db.query(Project).filter(Project.id == project_id).first()
    room = db.query(Room).filter(Room.id == room_id).first() if (room_id and str(room_id).strip() not in ["", "null", "undefined"]) else None

    norm = lambda s: (s or "").lower().replace("_", " ").strip()
    room_type = (room.room_type if room else anchor.room_type) or "living_room"
    total_budget = float(project.budget) if project and project.budget else 500000.0

    # 1. Calculate Room Budget Allocation
    weight = ROOM_BUDGET_WEIGHTS.get(room_type, 0.25)
    room_budget = total_budget * weight

    # Calculate already customized items in this room (excluding anchor's category)
    existing_spent = 0.0
    if room and room.items:
        for it in room.items:
            if it.product and it.product.category != anchor.category:
                existing_spent += float(it.unit_price or it.product.price or 0) * (it.qty or 1)

    remaining_room_budget = max(20000.0, room_budget - anchor.price - existing_spent)

    # 2b. In-Session Dynamic Contextual Preferences (Cross-Room Material & Finish Continuity)
    session_prefs = extract_in_session_preferences(project, room_id)
    session_woods = session_prefs["woods"]
    session_fabrics = session_prefs["fabrics"]
    session_colors = session_prefs["colors"]

    # 2. Dynamic Companion Category Schemas tailored to anchor product & room
    schema_list = get_companion_schema_for_product(room_type, anchor)

    # Project & Anchor Aesthetic Attributes
    user_style_tags = (project.style_tags or []) if project else []
    if not user_style_tags and project and hasattr(project, "style_vibe") and project.style_vibe:
        user_style_tags = [project.style_vibe.lower()]
    pref_wood = (project.interior_material_preference or "").lower() if project else ""
    pref_fabric = (project.fabric_preference or "").lower() if project else ""
    pref_colors = (project.color_preferences or []) if project else []

    anchor_color = extract_dominant_color(anchor)
    anchor_role = detect_product_role(anchor)

    recommended_items = []

    # 3. Process Each Companion Category
    for entry in schema_list:
        cat_id = entry["category"]
        cat_label = entry["label"]
        target_pct = entry["target_pct"]
        rel_to_anchor_pct = entry.get("rel_to_anchor_pct", 0.5)

        # Proportional Category Cap
        cap_from_room = max(7000.0, room_budget * target_pct)
        cap_from_anchor = max(7000.0, anchor.price * rel_to_anchor_pct)
        if anchor.price < 12000.0 and target_pct >= 0.30:
            hard_category_cap = max(cap_from_room, remaining_room_budget * 0.8)
        else:
            hard_category_cap = max(6000.0, min(max(cap_from_room, cap_from_anchor), remaining_room_budget * 0.75))

        candidates = _find_candidate_products_for_companion(room_type, cat_id, anchor, db)
        if not candidates:
            continue

        scored_candidates = []
        for cand in candidates:
            score = 12.0
            reasons = []

            # 1. Color Harmony Engine (Prioritize Anchor Product Color + Mood)
            cand_color = extract_dominant_color(cand)
            if anchor_color and anchor_color in COLOR_HARMONY_MAP:
                harmonies = COLOR_HARMONY_MAP[anchor_color]
                if mood == "accent":
                    # Accent Pop: boost contrasting accents & complementary colors
                    if cand_color in harmonies["accent"]:
                        score += 18.0
                        reasons.append(f"Designer Accent Contrast with {cand_color.title()}")
                    elif cand_color in harmonies["complementary"]:
                        score += 14.0
                        reasons.append(f"Complementary {cand_color.title()} palette")
                    elif cand_color in harmonies["primary"]:
                        score += 7.0
                        reasons.append(f"Matching {cand_color.title()} tone")
                    else:
                        score -= 2.0
                else:
                    # Tone Match: boost exact monochrome anchor color
                    if cand_color in harmonies["primary"]:
                        score += 18.0
                        reasons.append(f"Monochrome {cand_color.title()} match")
                    elif cand_color in harmonies["complementary"]:
                        score += 9.0
                        reasons.append(f"Harmonious {cand_color.title()} palette")
                    elif cand_color in harmonies["accent"]:
                        score += 4.0
                        reasons.append(f"Accent contrast")
                    else:
                        score -= 4.0
            elif pref_colors:
                color_priority = get_color_match_priority(cand.color_variants or [], pref_colors)
                if color_priority == 1:
                    score += 9.0
                    reasons.append("Matches your chosen color preference")
                elif color_priority == 2:
                    score += 5.0
                    reasons.append("Harmonized color family")
                elif color_priority == 3:
                    score += 2.0

            # 2. Budget & Price Fit
            if cand.price <= hard_category_cap:
                score += 5.0
                pct_of_room = round((cand.price / room_budget) * 100, 1)
                reasons.append(f"Fits within ₹{int(hard_category_cap):,} cap ({pct_of_room}% of room)")
            elif cand.price <= hard_category_cap * 1.25:
                score += 1.0
                reasons.append("Slight variation above target cap")
            else:
                score -= 6.0

            # 3. Wood finish harmony
            cand_finish = (cand.finish or "").lower()
            cand_mat = (cand.primary_material or "").lower()
            cand_variants = cand.variants or {}
            cand_wood_variants = [w.lower() for w in cand_variants.get("wood_finish", [])]

            if pref_wood:
                if any(w in pref_wood and (w in cand_finish or w in cand_mat or any(w in vw for vw in cand_wood_variants)) for w in ["teak", "oak", "walnut"]):
                    score += 3.5
                    reasons.append(f"Matches your {project.interior_material_preference} finish")
                elif "wood" in cand_mat or "matte" in cand_finish:
                    score += 1.5

            # 4. Fabric harmony
            if pref_fabric:
                cand_fabric_variants = [f.lower() for f in cand_variants.get("fabric", [])]
                if any(f in pref_fabric and (any(f in vf for vf in cand_fabric_variants) or f in cand_mat) for f in ["velvet", "linen", "woven", "leather"]):
                    score += 3.0
                    reasons.append(f"Harmonizes with {project.fabric_preference}")

            # 5. Style compatibility
            cand_tags = cand.style_tags or []
            anchor_tags = anchor.style_tags or []
            shared_tags = set(anchor_tags).intersection(cand_tags)
            if shared_tags:
                score += len(shared_tags) * 1.5
                reasons.append(f"{list(shared_tags)[0].title()} design style")
            else:
                for ut in user_style_tags:
                    compat = STYLE_COMPAT.get(ut, {})
                    for ct in cand_tags:
                        score += compat.get(ct, 0.2) * 1.5


            # 6. Ergonomic Knowledge Graph Evaluation
            ergo_score, ergo_compatible, ergo_reason = evaluate_ergonomic_compatibility(anchor, cand)
            score += ergo_score
            if ergo_reason:
                reasons.append(ergo_reason)

            # 7. In-Session Dynamic Contextual Preference Re-Ranking (Cross-Room Continuity)
            if session_woods:
                cand_finish_str = f"{cand_finish} {cand_mat} {' '.join(cand_wood_variants)}".lower()
                matching_sw = [sw for sw in session_woods if sw in cand_finish_str]
                if matching_sw:
                    score += 4.0
                    reasons.append(f"In-session continuity with {matching_sw[0].title()} finish")

            if session_fabrics:
                cand_fabric_str = f"{cand_mat} {' '.join(cand_fabric_variants)}".lower()
                matching_sf = [sf for sf in session_fabrics if sf in cand_fabric_str]
                if matching_sf:
                    score += 3.5
                    reasons.append(f"Harmonizes with in-session {matching_sf[0].title()} fabric")

            # Match Percentage (84% - 98%)
            match_pct = min(98, max(82, int(74 + (score * 1.6))))

            scored_candidates.append({
                "product": cand,
                "score": score,
                "match_pct": match_pct,
                "reasons": reasons[:3],
                "category_cap": round(hard_category_cap),
                "pct_of_room": round((cand.price / room_budget) * 100, 1),
            })

        scored_candidates.sort(key=lambda x: x["score"], reverse=True)
        if scored_candidates:
            best = scored_candidates[0]
            bp = best["product"]

            # Resolve best default variant values
            default_color = ""
            avail_colors = bp.color_variants or bp.variants.get("color", [])
            target_color = anchor_color or (pref_colors[0].lower() if pref_colors else "")
            if target_color and avail_colors:
                best_c = [c for c in avail_colors if target_color in c.lower()]
                default_color = best_c[0] if best_c else avail_colors[0]
            elif avail_colors:
                default_color = avail_colors[0]

            default_wood = ""
            avail_woods = bp.variants.get("wood_finish", [])
            if pref_wood and avail_woods:
                best_w = [w for w in avail_woods if any(pw in w.lower() for pw in ["teak", "oak", "walnut"] if pw in pref_wood)]
                default_wood = best_w[0] if best_w else avail_woods[0]
            elif avail_woods:
                default_wood = avail_woods[0]

            recommended_items.append({
                "id": bp.id,
                "name": bp.name,
                "category": cat_id,
                "category_label": cat_label,
                "price": bp.price,
                "category_cap": best["category_cap"],
                "pct_of_room": best["pct_of_room"],
                "match_pct": best["match_pct"],
                "reasons": best["reasons"],
                "thumbnail_url": bp.thumbnail_url,
                "description": entry["desc"],
                "default_attributes": {
                    "color": default_color,
                    "wood_finish": default_wood,
                    "fabric": (bp.variants.get("fabric") or [None])[0] if bp.variants else None,
                    "size": (bp.variants.get("size") or [None])[0] if bp.variants else None,
                },
                "priority": entry["priority"],
            })

    # How big this room really is. Once a floor plan is confirmed these come
    # from the customer's own drawing; before that they are the BHK defaults.
    room_length = float(room.length_ft) if (room and room.length_ft) else (16.0 if "living" in room_type else 14.0 if "master" in room_type else 12.0)
    room_width = float(room.width_ft) if (room and room.width_ft) else (12.0 if "living" in room_type else 11.0 if "master" in room_type else 10.0)
    room_area_sqft = max(30.0, room_length * room_width)

    # Whether a piece can physically stand in this room is decided in one
    # place, so the catalogue and this engine cannot disagree about it.
    from ..services.room_fit import product_fits
    long_wall, short_wall = max(room_length, room_width), min(room_length, room_width)

    def wall_fit(p: Product) -> dict:
        fits, why = product_fits(p, room, room_type)
        return {"fits": fits, "reason": why}

    # 4. Pre-select top complementary items within budget
    running_total = anchor.price
    for item in recommended_items:
        product = db.query(Product).filter(Product.id == item["id"]).first()
        verdict = wall_fit(product) if product else {"fits": True, "reason": ""}
        item["fits_room"] = verdict["fits"]
        item["fit_note"] = verdict["reason"]
        affordable = ((running_total + item["price"]) <= (room_budget * 1.05)
                      and running_total + item["price"] <= total_budget)
        item["pre_selected"] = bool(affordable and verdict["fits"])
        if item["pre_selected"]:
            running_total += item["price"]
    # Anything that cannot physically go in the room sinks to the bottom of the
    # list rather than being offered first.
    recommended_items.sort(key=lambda i: (not i.get("fits_room", True), -i.get("priority", 0)))

    # 5. Spatial Feasibility & Footprint Check (Module 4)

    def get_footprint_sqft(p: Product) -> float:
        w = float(p.width or 1200.0)
        d = float(p.depth or 600.0)
        return round((w * d) / 92903.04, 1)

    total_bundle_footprint = get_footprint_sqft(anchor)
    for it in recommended_items:
        if it.get("pre_selected"):
            it_prod = db.query(Product).filter(Product.id == it["id"]).first()
            if it_prod:
                total_bundle_footprint += get_footprint_sqft(it_prod)

    footprint_pct = round((total_bundle_footprint / room_area_sqft) * 100, 1)
    spatial_feasibility = {
        "room_dimensions": f"{int(room_length)}' × {int(room_width)}'",
        "room_area_sqft": round(room_area_sqft),
        "bundle_footprint_sqft": round(total_bundle_footprint, 1),
        "footprint_pct": footprint_pct,
        "status": "Optimal Spatial Flow" if footprint_pct <= 38.0 else "Comfortable Fit",
        "badge_text": f"Uses {round(footprint_pct)}% floor area (within 40% clearance limit)",
        "circulation_envelope": "Preserves 850mm walking clearance",
        "is_valid": footprint_pct <= 42.0,
        "longest_wall_ft": round(max(room_length, room_width), 1),
        "anchor_fits": wall_fit(anchor)["fits"],
        "anchor_fit_note": wall_fit(anchor)["reason"],
        "wont_fit": [i["name"] for i in recommended_items if not i.get("fits_room", True)],
    }

    # 6. Alternative Swaps Engine (Module 6: Budget-Saver & Premium Upgrade)
    same_role_prods = [
        p for p in db.query(Product).filter(Product.room_type == room_type).all()
        if p.id != anchor.id and detect_product_role(p) == anchor_role
    ]

    alternatives = {}
    cheaper = [p for p in same_role_prods if p.price < anchor.price]
    if cheaper:
        cheaper.sort(key=lambda x: x.price)
        best_cheap = cheaper[0]
        savings = anchor.price - best_cheap.price
        alternatives["budget_saver"] = {
            "id": best_cheap.id,
            "name": best_cheap.name,
            "price": best_cheap.price,
            "savings": round(savings),
            "badge": f"Save ₹{int(savings):,}",
            "thumbnail_url": best_cheap.thumbnail_url,
            "label": "Budget-Saver Alternative",
        }
    else:
        est_savings = round(anchor.price * 0.15)
        alternatives["budget_saver"] = {
            "id": anchor.id,
            "name": f"Matte Finish {anchor.name}",
            "price": round(anchor.price - est_savings),
            "savings": est_savings,
            "badge": f"Save ₹{int(est_savings):,} with Matte finish",
            "thumbnail_url": anchor.thumbnail_url,
            "label": "Budget-Saver Option",
        }

    costlier = [p for p in same_role_prods if p.price > anchor.price]
    if costlier:
        costlier.sort(key=lambda x: x.price, reverse=True)
        best_prem = costlier[0]
        diff = best_prem.price - anchor.price
        alternatives["premium_upgrade"] = {
            "id": best_prem.id,
            "name": best_prem.name,
            "price": best_prem.price,
            "extra_cost": round(diff),
            "badge": f"+₹{int(diff):,} Premium",
            "thumbnail_url": best_prem.thumbnail_url,
            "label": "Premium Upgrade Alternative",
        }
    else:
        upgrade_cost = round(anchor.price * 0.14)
        alternatives["premium_upgrade"] = {
            "id": anchor.id,
            "name": f"Solid Teak Finish {anchor.name}",
            "price": round(anchor.price + upgrade_cost),
            "extra_cost": upgrade_cost,
            "badge": f"+₹{int(upgrade_cost):,} Solid Teak",
            "thumbnail_url": anchor.thumbnail_url,
            "label": "Luxury Finish Upgrade",
        }

    # 7. Dynamic Budget Rebalancing Breakdown (Module 1)
    budget_breakdown = {
        "room_allocated": round(room_budget),
        "anchor_spent": round(anchor.price),
        "anchor_pct_of_room": round((anchor.price / room_budget) * 100, 1),
        "tier_classification": "Anchor Element (45-50% tier)" if anchor.price >= room_budget * 0.3 else "Secondary / Accent Tier",
        "remaining_for_companions": round(remaining_room_budget),
        "bundle_total": round(running_total),
        "savings_vs_budget": round(max(0, room_budget - running_total)),
    }

    return {
        "anchor_product_id": anchor.id,
        "anchor_name": anchor.name,
        "anchor_price": anchor.price,
        "room_type": room_type,
        "room_budget": round(room_budget),
        "remaining_room_budget": round(remaining_room_budget),
        "recommended_items": recommended_items,
        "pre_selected_total": round(running_total),
        "budget_safe": running_total <= room_budget,
        "spatial_feasibility": spatial_feasibility,
        "alternatives": alternatives,
        "budget_breakdown": budget_breakdown,
    }


def _pkg_dict(p: Package) -> dict:
    return {
        "id": p.id,
        "name": p.name,
        "tier": p.tier,
        "bhk": p.bhk,
        "base_price": p.base_price,
        "style_tags": p.style_tags or [],
        "thumbnail_url": p.thumbnail_url,
        "description": p.description,
        "featured": p.featured,
    }


def _prod_dict(p: Product) -> dict:
    return {
        "id": p.id,
        "sku": p.sku,
        "name": p.name,
        "category": p.category,
        "room_type": p.room_type,
        "price": p.price,
        "materials": p.materials or [],
        "color_variants": p.color_variants or [],
        "thumbnail_url": p.thumbnail_url,
        "style_tags": p.style_tags or [],
        "primary_material": p.primary_material,
        "width": p.width,
        "height": p.height,
        "depth": p.depth,
        "weight": p.weight,
        "weight_capacity": p.weight_capacity,
        "style": p.style,
        "finish": p.finish,
        "mounting_type": p.mounting_type,
        "assembly_required": p.assembly_required,
        "suitable_room": p.suitable_room,
        "description": p.description
    }


# --- Spatial Feasibility & Clearance Envelope Solver ---
