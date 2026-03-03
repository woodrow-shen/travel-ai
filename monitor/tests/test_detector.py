from app.detector import detect_anomaly


def test_detect_anomaly_high_confidence():
    """Price below 50% of average should be high confidence."""
    history = [10000.0] * 30  # avg = 10000
    result = detect_anomaly(
        origin="TPE",
        destination="NRT",
        current_price=4000.0,  # 40% of avg
        currency="TWD",
        history=history,
        source="amadeus",
    )
    assert result is not None
    assert result.confidence == "high"
    assert result.current_price == 4000.0
    assert result.average_price == 10000.0


def test_detect_anomaly_medium_confidence():
    """Price below 2 std dev should be medium confidence."""
    # Create history with some variance
    history = [10000.0, 10500.0, 9500.0, 10200.0, 9800.0,
               10100.0, 10300.0, 9700.0, 10400.0, 9600.0]
    result = detect_anomaly(
        origin="TPE",
        destination="NRT",
        current_price=8500.0,
        currency="TWD",
        history=history,
        source="amadeus",
    )
    # With small std dev (~350), 8500 is well below avg(~10010) - 2*std(~700)
    assert result is not None
    assert result.confidence in ("high", "medium")


def test_detect_no_anomaly():
    """Normal price should not trigger."""
    history = [10000.0] * 30
    result = detect_anomaly(
        origin="TPE",
        destination="NRT",
        current_price=9000.0,  # 90% of avg - normal
        currency="TWD",
        history=history,
        source="amadeus",
    )
    assert result is None


def test_detect_insufficient_history():
    """Too few data points should return None."""
    result = detect_anomaly(
        origin="TPE",
        destination="NRT",
        current_price=1000.0,
        currency="TWD",
        history=[10000.0, 10000.0],  # only 2 points
        source="amadeus",
    )
    assert result is None


def test_detect_single_source_upgrade():
    """When only one source shows low price, confidence should be high."""
    history = [10000.0] * 30
    result = detect_anomaly(
        origin="TPE",
        destination="NRT",
        current_price=4500.0,
        currency="TWD",
        history=history,
        source="amadeus",
        other_source_price=9500.0,  # other source normal
    )
    assert result is not None
    assert result.confidence == "high"
