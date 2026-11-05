import pytest
from phone_repair_quote import repair_quote, repair_days, trade_in_value


# ---------- Starter tests ----------
def test_budget_screen():
    assert repair_quote("screen", "budget", False, False) == 4600


def test_in_stock_quick():
    assert repair_days("battery", True, 2) == 1


# ---------- repair_quote ----------
def test_unknown_part_raises():
    with pytest.raises(ValueError, match="unknown part"):
        repair_quote("speaker", "budget", False, False)


def test_unknown_brand_tier_raises():
    with pytest.raises(ValueError, match="unknown brand tier"):
        repair_quote("screen", "midrange", False, False)


def test_flagship_battery_warranty_express():
    # flagship doubles cost, warranty zeroes the part cost, labour 300, express +500
    assert repair_quote("battery", "flagship", True, True) == 800


def test_budget_camera_no_warranty():
    # non-screen labour (300) with the part cost charged
    assert repair_quote("camera", "budget", False, False) == 2800


# ---------- repair_days ----------
def test_no_technicians_free():
    assert repair_days("battery", True, 0) == 3


def test_screen_out_of_stock():
    assert repair_days("screen", False, 1) == 6


def test_other_part_out_of_stock():
    assert repair_days("battery", False, 1) == 3


# ---------- trade_in_value ----------
def test_trade_in_invalid_input():
    with pytest.raises(ValueError, match="invalid input"):
        trade_in_value(0, 10, False)


def test_trade_in_too_old():
    assert trade_in_value(10000, 60, False) == 0


def test_trade_in_up_to_12_months():
    assert trade_in_value(10000, 6, False) == 6000


def test_trade_in_13_to_24_months():
    assert trade_in_value(10000, 18, False) == 4000


def test_trade_in_over_24_months():
    assert trade_in_value(10000, 30, False) == 2000


def test_trade_in_cracked_screen():
    assert trade_in_value(10000, 6, True) == 3000
