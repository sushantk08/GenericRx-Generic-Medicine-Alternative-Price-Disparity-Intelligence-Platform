import re

# Common abbreviations mapped to standardized pharmaceutical chemical names
SALT_SYNONYMS = {
    r"\bhcl\b": "Hydrochloride",
    r"\bhydrochlor\b": "Hydrochloride",
    r"\bsod\b": "Sodium",
    r"\bpot\b": "Potassium",
    r"\bphos\b": "Phosphate",
    r"\bsulph\b": "Sulphate",
    r"\bsulfate\b": "Sulphate",
    r"\bcalc\b": "Calcium",
}

# Modifiers, pharmacopeia standards, and dosage words to strip out
NOISE_PATTERNS = [
    r"\b(tab|tablets?|caps?|capsules?|inj|injections?|syp|syrup|drops?|gel|cream|ointment)\b\.?",
    r"\b(ip|bp|usp)\b\.?",  # Pharmacopeia monographs
    r"\b(sr|er|cr|pr|xr|mr|dr|xl)\b",  # Release types
    r"\b(forte|plus|ds)\b",  # Marketing brand suffixes
    r"\(.*?\)",  # Parenthetical expressions
    r"\d+(\.\d+)?\s*(mg|mcg|gm|g|ml|iu|u|%|milligram|microgram)\b",  # Dosages
    r"[\+\/\&]",  # Combination separators
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

# Regex to capture numeric strength and unit
DOSAGE_REGEX = re.compile(
    r"(\d+(?:\.\d+)?)\s*(mg|mcg|ug|gm|g|ml|iu|milligram|microgram|gram|milliliter)\b",
    re.IGNORECASE,
)


def clean_salt_name(raw_name: str) -> str:
    """Normalize and standardize a raw drug or chemical salt string."""
    if not raw_name or not isinstance(raw_name, str):
        return ""

    text = raw_name.lower().strip()

    # 1. Expand known salt abbreviations
    for pattern, replacement in SALT_SYNONYMS.items():
        text = re.sub(pattern, replacement.lower(), text)

    # 2. Strip noise terms, dosage forms, release mechanisms, and strengths
    for pattern in NOISE_PATTERNS:
        text = re.sub(pattern, " ", text)

    # 3. Clean up extra whitespace and convert to standard Title Case
    clean_tokens = [
        token.capitalize() for token in text.split() if len(token) > 1
    ]
    return " ".join(clean_tokens).strip()


def parse_dosage(raw_text: str) -> tuple[float, str, str]:
    """Extract (strength_value, strength_unit, dosage_form) from raw medicine text.

    Defaults to (0.0, 'mg', 'Tablet') if no explicit dosage is found.
    """
    if not raw_text or not isinstance(raw_text, str):
        return (0.0, "mg", "Tablet")

    # 1. Determine dosage form
    lower_text = raw_text.lower()
    if any(k in lower_text for k in ["capsule", "cap.", "cap "]):
        dosage_form = "Capsule"
    elif any(k in lower_text for k in ["syrup", "syp", "suspension", "liquid"]):
        dosage_form = "Syrup"
    elif any(k in lower_text for k in ["injection", "inj.", "inj "]):
        dosage_form = "Injection"
    else:
        dosage_form = "Tablet"

    # 2. Extract numeric strength and unit
    match = DOSAGE_REGEX.search(raw_text)
    if match:
        raw_val = float(match.group(1))
        raw_unit = match.group(2).lower()
        std_unit = UNIT_MAPPINGS.get(raw_unit, "mg")
        return (raw_val, std_unit, dosage_form)

    return (0.0, "mg", dosage_form)