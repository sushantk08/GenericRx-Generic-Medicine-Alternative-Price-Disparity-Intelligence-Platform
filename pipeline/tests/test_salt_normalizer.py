from pipeline.transformers.salt_normalizer import clean_salt_name, parse_dosage


def test_clean_salt_name_variants():
    assert (
        clean_salt_name("Tab. Metformin HCL 500mg") == "Metformin Hydrochloride"
    )
    assert (
        clean_salt_name("Metformin Hydrochloride 500 MG Tablet IP")
        == "Metformin Hydrochloride"
    )
    assert clean_salt_name("Telmisartan 40 mg Tab IP") == "Telmisartan"
    assert (
        clean_salt_name("Atorvastatin Calcium Tablets IP 10mg")
        == "Atorvastatin Calcium"
    )
    assert clean_salt_name("Paracetamol 650 milligram") == "Paracetamol"


def test_parse_dosage_variants():
    # Standard tablets
    assert parse_dosage("Metformin 500mg Tablet") == (500.0, "mg", "Tablet")
    assert parse_dosage("Telmisartan 40 mg Tab") == (40.0, "mg", "Tablet")

    # Decimals
    assert parse_dosage("Clonazepam 0.5mg Tab") == (0.5, "mg", "Tablet")

    # Capsules & written units
    assert parse_dosage("Omeprazole 20 milligram Capsule") == (
        20.0,
        "mg",
        "Capsule",
    )

    # Liquids & syrups
    assert parse_dosage("Paracetamol 100ml Syrup") == (100.0, "ml", "Syrup")