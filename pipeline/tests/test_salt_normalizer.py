from pipeline.transformers.salt_normalizer import (
    clean_salt_name,
    parse_combination_salt,
    parse_dosage,
)


def test_combination_order_independence():
    # Verify that order of listing does not affect the canonical salt name
    fdc_variant_a = (
        "Telmisartan 40mg + Amlodipine 5mg"  # Telmisartan first
    )
    fdc_variant_b = "Amlodipine 5mg + Telmisartan 40mg"  # Amlodipine first
    fdc_variant_c = "Tab. Amlodipine Besylate 5 mg and Telmisartan 40 MG"

    parsed_a = parse_combination_salt(fdc_variant_a)
    parsed_b = parse_combination_salt(fdc_variant_b)
    parsed_c = parse_combination_salt(fdc_variant_c)

    assert parsed_a["canonical_salt_name"] == parsed_b["canonical_salt_name"]
    assert parsed_a["canonical_salt_name"] == parsed_c["canonical_salt_name"]
    assert (
        parsed_a["canonical_salt_name"]
        == "Amlodipine (5mg) + Telmisartan (40mg)"
    )


def test_triple_combination_and_release_mechanism():
    # Common diabetic triple FDC with Sustained Release (SR)
    raw_fdc = "Glimepiride 2mg + Metformin HCL 500mg SR + Voglibose 0.2mg"
    parsed = parse_combination_salt(raw_fdc)

    assert parsed["dosage_form"] == "Tablet SR"
    # Ingredients sorted alphabetically: Glimepiride, Metformin, Voglibose
    assert (
        parsed["canonical_salt_name"]
        == "Glimepiride (2mg) + Metformin Hydrochloride (500mg) + Voglibose (0.2mg)"
    )


def test_antibiotic_combination():
    # Augmentin composition
    raw = "Amoxycillin 500mg + Potassium Clavulanate 125mg Tablet"
    parsed = parse_combination_salt(raw)

    assert (
        parsed["canonical_salt_name"]
        == "Amoxycillin (500mg) + Clavulanic Acid (125mg)"
    )