from pipeline.transformers.price_calculator import (
    calculate_price_per_unit,
    parse_pack_size,
)


def test_parse_pack_size():
    assert parse_pack_size("10 tablets in 1 strip") == 10
    assert parse_pack_size("Strip of 15 tablets") == 15
    assert parse_pack_size("10's") == 10
    assert parse_pack_size("Bottle of 60 capsules") == 60
    assert parse_pack_size("100 ml in 1 bottle") == 100
    assert parse_pack_size(15) == 15
    assert parse_pack_size("") == 10
    assert parse_pack_size(None) == 10


def test_calculate_price_per_unit():
    # Branded Telmisartan: ₹140 for 10 tablets -> ₹14.00 per tablet
    assert calculate_price_per_unit(140.0, "10 tablets") == 14.0

    # Jan Aushadhi generic Telmisartan: ₹18 for 10 tablets -> ₹1.80 per tablet
    assert calculate_price_per_unit(18.0, "10's") == 1.8

    # 15 pack calculation: ₹225 for 15 tablets -> ₹15.00 per tablet
    assert calculate_price_per_unit("₹ 225.00", "Strip of 15") == 15.0

    # Edge cases
    assert calculate_price_per_unit(0, 10) == 0.0
    assert calculate_price_per_unit("invalid", 10) == 0.0