import re

# Regex to capture pack quantity from phrases like "10's", "15 tablets", "bottle of 60"
PACK_SIZE_REGEX = re.compile(
    r"(?:strip\s*of\s*|pack\s*of\s*|box\s*of\s*|bottle\s*of\s*)?(\d+)\s*(?:'s|s\b|tablets?|caps?|capsules?|ml|pills?|vials?|units?)?",
    re.IGNORECASE,
)


def parse_pack_size(raw_text: str | int | None) -> int:
    """Extract an integer pack size from catalog text (e.g.

    '10's', '15 Tablets in 1 Strip'). Defaults to 10 if ambiguous or zero.
    """
    if raw_text is None:
        return 10

    if isinstance(raw_text, int):
        return raw_text if raw_text > 0 else 10

    raw_str = str(raw_text).strip()
    if not raw_str:
        return 10

    # Look for integer patterns
    match = PACK_SIZE_REGEX.search(raw_str)
    if match and match.group(1):
        try:
            val = int(match.group(1))
            return val if val > 0 else 10
        except ValueError:
            pass

    return 10


def calculate_price_per_unit(
    raw_mrp: float | str | None, raw_pack_size: int | str | None
) -> float:
    """Calculates standardized price per tablet/unit rounded to 4 decimal places."""
    try:
        if raw_mrp is None:
            return 0.0

        clean_mrp_str = (
            str(raw_mrp).replace("₹", "").replace("Rs.", "").strip()
        )
        mrp = float(clean_mrp_str)
        if mrp <= 0:
            return 0.0
    except (ValueError, TypeError):
        return 0.0

    pack_size = parse_pack_size(raw_pack_size)
    return round(mrp / pack_size, 4)