import pytest
from phone_repair_quote import repair_quote, repair_days, trade_in_value


# ---------- Starter tests ----------
def test_budget_screen():
    assert repair_quote("screen", "budget", False, False) == 4600


def test_in_stock_quick():
    assert repair_days("battery", True, 2) == 1


# ======================= repair_quote =======================
def test_unknown_part_raises():
    with pytest.raises(ValueError, match="unknown part"):
        repair_quote("speaker", "budget", False, False)


def test_unknown_brand_tier_raises():
    with pytest.raises(ValueError, match="unknown brand tier"):
        repair_quote("screen", "midrange", False, False)


def test_unknown_part_checked_before_tier():
    with pytest.raises(ValueError, match="unknown part"):
        repair_quote("speaker", "midrange", False, False)


@pytest.mark.parametrize(
    "part, tier, warranty, express, expected",
    [
        # brand_tier == "flagship": True / False
        ("screen", "flagship", False, False, 8600),
        ("screen", "budget", False, False, 4600),
        # part == "screen": True / False (labour 600 vs 300)
        ("battery", "budget", False, False, 1800),
        ("charging_port", "budget", False, False, 1100),
        # warranty branch: (warranty and part != screen) True / False
        ("battery", "budget", True, False, 300),        # True  -> part cost waived
        ("screen", "budget", True, False, 4600),        # warranty but screen -> not waived
        ("battery", "budget", False, False, 1800),      # no warranty
        # express: True / False
        ("screen", "budget", False, True, 5100),
        ("camera", "flagship", False, True, 5800),
        ("charging_port", "flagship", True, True, 800),
    ],
)
def test_repair_quote_combinations(part, tier, warranty, express, expected):
    assert repair_quote(part, tier, warranty, express) == expected


# ======================= repair_days =======================
@pytest.mark.parametrize(
    "part, in_stock, techs, expected",
    [
        # technicians_free == 0: True / False
        ("battery", True, 0, 3),
        ("battery", True, 1, 1),
        # not parts_in_stock: False (skipped) vs True
        ("screen", True, 0, 3),
        # part == "screen" or "camera": each side of the OR + the else
        ("screen", False, 2, 6),
        ("camera", False, 2, 6),
        ("battery", False, 2, 3),
        ("charging_port", False, 0, 5),
        ("screen", False, 0, 8),
    ],
)
def test_repair_days_combinations(part, in_stock, techs, expected):
    assert repair_days(part, in_stock, techs) == expected


# ======================= trade_in_value =======================
@pytest.mark.parametrize(
    "price, age",
    [
        (0, 10),       # price boundary (<= 0)
        (-5, 10),      # negative price
        (10000, -1),   # negative age
        (-5, -1),      # both invalid
    ],
)
def test_trade_in_invalid_inputs(price, age):
    with pytest.raises(ValueError, match="invalid input"):
        trade_in_value(price, age, False)


@pytest.mark.parametrize(
    "price, age, cracked, expected",
    [
        (10000, 0, False, 6000),     # age 0 is valid
        (10000, 12, False, 6000),    # upper edge of first tier
        (10000, 13, False, 4000),    # just into second tier
        (10000, 24, False, 4000),    # upper edge of second tier
        (10000, 25, False, 2000),    # just into third tier
        (10000, 48, False, 2000),    # last valid age
        (10000, 49, False, 0),       # first "too old" age
        (10000, 6, True, 3000),      # cracked, tier 1
        (10000, 18, True, 2000),     # cracked, tier 2
        (10000, 30, True, 1000),     # cracked, tier 3
        (10000, 60, True, 0),        # too old wins over cracked
        (999, 6, True, 299),         # integer-division rounding
    ],
)
def test_trade_in_tiers(price, age, cracked, expected):
    assert trade_in_value(price, age, cracked) == expected
