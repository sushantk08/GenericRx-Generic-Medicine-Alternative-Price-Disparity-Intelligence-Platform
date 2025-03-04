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
    r"\b(sr|er|cr|pr|xr|mr|dr|xl)\b",  # Release types (Sustained/Extended/Controlled Release)
    r"\b(forte|plus|ds)\b",  # Marketing brand suffixes
    r"\(.*?\)",  # Parenthetical expressions like (as hydrochloride)
    r"\d+(\.\d+)?\s*(mg|mcg|gm|g|ml|iu|u|%|milligram|microgram)\b",  # Dosages like 500mg, 10 ml
    r"[\+\/\&]",  # Combination separators if needed for single-salt cleaning
    r"[^a-zA-Z\s]",  # Non-alphabetical symbols
]


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
    clean_tokens = [token.capitalize() for token in text.split() if len(token) > 1]
    return " ".join(clean_tokens).strip()