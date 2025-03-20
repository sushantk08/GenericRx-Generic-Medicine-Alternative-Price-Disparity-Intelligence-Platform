import re

# Common abbreviations and salt forms mapped to standardized pharmaceutical chemical names
SALT_SYNONYMS = {
    r"\b(potassium\s+|sodium\s+)?clavulan(ate|ic\s*acid)\b": "Clavulanic Acid",
    r"\bclav\b": "Clavulanic Acid",
    r"\bhcl\b": "Hydrochloride",
    r"\bhydrochlor\b": "Hydrochloride",
    r"\bsod\b": "Sodium",
    r"\bpot\b": "Potassium",
    r"\bphos\b": "Phosphate",
    r"\bsulph\b": "Sulphate",
    r"\bsulfate\b": "Sulphate",
    r"\bcalc\b": "Calcium",
}

# Modifiers, release mechanisms, salt conjugates, and noise terms to strip from salt names
NOISE_PATTERNS = [
    r"\b(tab|tablets?|caps?|capsules?|inj|injections?|syp|syrup|drops?|gel|cream|ointment)\b\.?",
    r"\b(ip|bp|usp)\b\.?",  # Pharmacopeia monographs
    r"\b(sr|er|cr|pr|xr|mr|dr|xl)\b",  # Release mechanism tags
    r"\b(besylate|mesylate|maleate|fumarate|tartrate|succinate|citrate|gluconate|trihydrate|hydrate)\b",  # Salt conjugates
    r"\b(forte|plus|ds|duo|max)\b",  # Marketing brand suffixes
    r"\(.*?\)",  # Parenthetical notes like (as hydrochloride)
    r"\d+(\.\d+)?\s*(mg|mcg|gm|g|ml|iu|u|%|milligram|microgram)\b",  # Dosages
    r"[^a-zA-Z\s]",  # Non-alphabetical symbols
]

# Standard unit mappings
UNIT_MAPPINGS = {
    "milligram": "mg",
    "milligrams": "mg",
    "mg": "mg",
    "mgs": "mg",
    "microgram": "mcg",
    "micrograms": "mcg",
    "mcg": "mcg",
    "ug": "mcg",
    "gram": "gm",
    "grams": "gm",
    "gm": "gm",
    "g": "gm",
    "milliliter": "ml",
    "milliliters": "ml",
    "ml": "ml",
    "iu": "iu",
}

# Capture numeric strength and unit
DOSAGE_REGEX = re.compile(
    r"(\d+(?:\.\d+)?)\s*(mg|mcg|ug|gm|g|ml|iu|milligram|microgram|gram|milliliter)\b",
    re.IGNORECASE,
)

# Release mechanisms for dosage form metadata
RELEASE_MECHANISMS = {
    r"\b(sr|sustained\s*release)\b": "SR",
    r"\b(pr|prolonged\s*release)\b": "PR",
    r"\b(er|extended\s*release|xr)\b": "ER",
    r"\b(cr|controlled\s*release)\b": "CR",
}


def clean_single_salt(raw_salt: str) -> str:
    """Clean and normalize a single chemical compound name."""
    if not raw_salt or not isinstance(raw_salt, str):
        return ""

    text = raw_salt.lower().strip()

    # Expand abbreviations and compound names
    for pattern, replacement in SALT_SYNONYMS.items():
        text = re.sub(pattern, replacement.lower(), text)

    # Strip noise terms, conjugates, and release types
    for pattern in NOISE_PATTERNS:
        text = re.sub(pattern, " ", text)

    tokens = [token.capitalize() for token in text.split() if len(token) > 1]
    return " ".join(tokens).strip()


def parse_combination_salt(raw_composition: str) -> dict:
    """Parse single or multi-ingredient Fixed-Dose Combination (FDC) drugs into a

    canonical, order-independent representation.
    """
    if not raw_composition or not isinstance(raw_composition, str):
        return {
            "canonical_salt_name": "",
            "strength_value": 0.0,
            "strength_unit": "mg",
            "dosage_form": "Tablet",
            "ingredients": [],
        }

    raw_text = raw_composition.strip()
    lower_text = raw_text.lower()

    # 1. Determine release mechanism modifier
    release_modifier = ""
    for pattern, tag in RELEASE_MECHANISMS.items():
        if re.search(pattern, lower_text):
            release_modifier = f" {tag}"
            break

    # 2. Determine base dosage form
    if any(k in lower_text for k in ["capsule", "cap.", "cap "]):
        base_form = "Capsule"
    elif any(k in lower_text for k in ["syrup", "syp", "suspension", "liquid"]):
        base_form = "Syrup"
    elif any(k in lower_text for k in ["injection", "inj.", "inj "]):
        base_form = "Injection"
    else:
        base_form = "Tablet"

    dosage_form = f"{base_form}{release_modifier}".strip()

    # 3. Split by combination delimiters (+, /, &, and)
    parts = re.split(r"\s*(?:\+|\band\b|\/|\&)\s*", raw_text, flags=re.IGNORECASE)

    ingredients = []
    total_strength = 0.0
    primary_unit = "mg"

    for part in parts:
        clean_name = clean_single_salt(part)
        if not clean_name:
            continue

        match = DOSAGE_REGEX.search(part)
        if match:
            val = float(match.group(1))
            unit = UNIT_MAPPINGS.get(match.group(2).lower(), "mg")
        else:
            val = 0.0
            unit = "mg"

        ingredients.append(
            {
                "salt": clean_name,
                "strength": val,
                "unit": unit,
            }
        )
        total_strength += val
        primary_unit = unit

    # 4. Sort ingredients alphabetically so order does not matter
    ingredients.sort(key=lambda x: x["salt"])

    # Build canonical combined title
    canonical_parts = [
        f"{ing['salt']} ({ing['strength']:g}{ing['unit']})"
        if ing["strength"] > 0
        else ing["salt"]
        for ing in ingredients
    ]
    canonical_salt_name = " + ".join(canonical_parts)

    return {
        "canonical_salt_name": canonical_salt_name,
        "strength_value": round(total_strength, 2),
        "strength_unit": primary_unit,
        "dosage_form": dosage_form,
        "ingredients": ingredients,
    }


def clean_salt_name(raw_name: str) -> str:
    parsed = parse_combination_salt(raw_name)
    return (
        parsed["canonical_salt_name"]
        if parsed["canonical_salt_name"]
        else clean_single_salt(raw_name)
    )


def parse_dosage(raw_text: str) -> tuple[float, str, str]:
    parsed = parse_combination_salt(raw_text)
    return (
        parsed["strength_value"],
        parsed["strength_unit"],
        parsed["dosage_form"],
    )