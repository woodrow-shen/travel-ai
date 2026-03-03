from app.lib.currency import convert_price


MOCK_RATES = {
    "EUR": 1.0,
    "USD": 1.08,
    "TWD": 35.2,
    "JPY": 163.5,
}


def test_convert_price_eur_to_twd():
    amount, currency = convert_price(307.0, "EUR", "TWD", MOCK_RATES)
    assert currency == "TWD"
    assert amount == round(307.0 * 35.2, 2)


def test_convert_price_eur_to_usd():
    amount, currency = convert_price(100.0, "EUR", "USD", MOCK_RATES)
    assert currency == "USD"
    assert amount == 108.0


def test_convert_price_same_currency():
    amount, currency = convert_price(500.0, "TWD", "TWD", MOCK_RATES)
    assert currency == "TWD"
    assert amount == 500.0


def test_convert_price_missing_target_rate():
    amount, currency = convert_price(100.0, "EUR", "GBP", MOCK_RATES)
    assert currency == "EUR"
    assert amount == 100.0


def test_convert_price_empty_rates():
    amount, currency = convert_price(100.0, "EUR", "TWD", {})
    assert currency == "EUR"
    assert amount == 100.0


def test_convert_price_rounds_to_two_decimals():
    rates = {"TWD": 35.123}
    amount, currency = convert_price(100.0, "EUR", "TWD", rates)
    assert currency == "TWD"
    assert amount == 3512.3
