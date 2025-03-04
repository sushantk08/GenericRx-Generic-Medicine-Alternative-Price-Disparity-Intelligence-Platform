from pipeline.transformers.salt_normalizer import clean_salt_name


def test_clean_salt_name_variants():
    # Test abbreviation expansion and noise removal
    assert (
        clean_salt_name("Tab. Metformin HCL 500mg") == "Metformin Hydrochloride"
    )
    assert (
        clean_salt_name("Metformin Hydrochloride 500 MG Tablet IP")
        == "Metformin Hydrochloride"
    )
    assert (
        clean_salt_name("Telmisartan 40 mg Tab IP")
        == "Telmisartan"
    )
    assert (
        clean_salt_name("Atorvastatin Calcium Tablets IP 10mg")
        == "Atorvastatin Calcium"
    )
    assert (
        clean_salt_name("Paracetamol 650 milligram")
        == "Paracetamol"
    )