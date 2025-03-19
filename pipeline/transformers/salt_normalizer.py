import re
from typing import TypedDict


class ParsedComponent(TypedDict):
    salt: str
    strength: float
    unit: str


class NormalizedSaltResult(TypedDict):
    canonical_salt_name: str
    strength_display: str
    dosage_form: str
    components: list[ParsedComponent]


# Noise words, pharmacopoeia tags, and release mechanisms
STRIP_TERMS = [
    r"\bIP\b",
    r"\bBP\b",
    r"\bUSP\b",
    r"\bHCL\b",
    r"\bHYDROCHLORIDE\b",
    r"\bSR\b",
    r"\bER\b",
    r"\bPR\b",
    r"\bCR\b",
    r"\bXR\b",
    r"\bFORTE\b",
    r"\bPLUS\b",
    r"\bTABLET\b",
    r"\bTABLETS\b",
    r"\bCAPSULE\b",
    r"\bCAPSULES\b",
    r"\bTAB\b",
    r"\bCAP\b",
    r"\bSYRUP\b",
    r"\bINJECTION\b",
]

# Standard dosage forms detection
DOSAGE_FORMS = [
    ("Tablet", [r"\btablet\b", r"\btablets\b", r"\btab\b"]),
    ("Capsule", [r"\bcapsule\b", r"\bcapsules\b", r"\bcap\b"]),
    ("Syrup", [r"\bsyrup\b", r"\bsuspension\b"]),
    ("Injection", [r"\binjection\b", r"\binj\b"]),
    ("Ointment", [r"\bointment\b", r"\bcream\b", r"\bgel\b"]),
]


def detect_dosage_form(raw_text: str) -> str:
    """Detect standardized dosage form from raw medicine or composition text."""
    lower_text = raw_text.lower()
    for form, patterns in DOSAGE_FORMS:
        for pat in patterns:
            if re.search(pat, lower_text):
                return form
    return "Tablet"  # Default fallback for oral solid dosage


def clean_single_salt(name: str) -> str:
    """Clean individual salt names by removing pharmacopoeia and chemical salt suffixes."""
    cleaned = name.upper()
    for term in STRIP_TERMS:
        cleaned = re.sub(term, "", cleaned, flags=re.IGNORECASE)
    # Remove extra punctuation and whitespace
    cleaned = re.sub(r"[\(\)\[\],]", " ", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned.title()


def parse_salt_composition(raw_salt_string: str) -> NormalizedSaltResult:
    """Parse single or multi-salt combination strings into canonical,

    alphabetically sorted compound representations.
    """
    dosage_form = detect_dosage_form(raw_salt_string)

    # Split combinations by '+', '/', or ' AND '
    raw_parts = re.split(r"\s*(?:\+|\/|\band\b)\s*", raw_salt_string, flags=re.IGNORECASE)

    parsed_components: list[ParsedComponent] = []

    for part in raw_parts:
        if not part.strip():
            continue

        # Extract numeric strength and unit (e.g., '500 mg', '0.5mg', '10 MCG', '1 GM')
        strength_match = re.search(
            r"(\d+(?:\.\d+)?)\s*(MG|MCG|GM|G|IU|ML|%)\b", part, flags=re.IGNORECASE
        )

        if strength_match:
            val = float(strength_match.group(1))
            unit = strength_match.group(2).lower()
            # Normalize 'g' to 'gm'
            if unit == "g":
                unit = "gm"
            # Remove the strength substring from the salt name
            salt_name_only = part[: strength_match.start()] + part[strength_match.end() :]
        else:
            val = 0.0
            unit = "mg"
            salt_name_only = part

        clean_name = clean_single_salt(salt_name_only)
        if clean_name:
            parsed_components.append(
                {"salt": clean_name, "strength": val, "unit": unit}
            )

    # Sort components alphabetically by salt name to ensure canonical matching
    parsed_components.sort(key=lambda x: x["salt"])

    if not parsed_components:
        # Fallback if no components parsed
        fallback_name = clean_single_salt(raw_salt_string)
        return {
            "canonical_salt_name": fallback_name,
            "strength_display": "N/A",
            "dosage_form": dosage_form,
            "components": [{"salt": fallback_name, "strength": 0.0, "unit": "mg"}],
        }

    # Construct canonical salt name and display strength
    canonical_salts = [comp["salt"] for comp in parsed_components]
    canonical_name = " + ".join(canonical_salts)

    strength_parts = [
        f"{comp['strength']:g} {comp['unit']}" if comp["strength"] > 0 else comp["unit"]
        for comp in parsed_components
    ]
    strength_display = " + ".join(strength_parts)

    return {
        "canonical_salt_name": canonical_name,
        "strength_display": strength_display,
        "dosage_form": dosage_form,
        "components": parsed_components,
    }