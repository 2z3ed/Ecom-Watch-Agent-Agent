from app.services import analyzer


def test_analyzer_mock_mode_output_shape() -> None:
    result = analyzer.analyze_changes(
        "Mock Product",
        [
            {"event_type": "price_changed", "old_value": "100", "new_value": "90", "change_ratio": -10},
            {"event_type": "stock_changed", "old_value": "in_stock", "new_value": "out_of_stock", "change_ratio": None},
        ],
    )
    assert set(result.keys()) == {"summary", "priority", "suggested_action"}
    assert result["priority"] in {"low", "medium", "high"}


def test_analyzer_fallback_when_real_mode_fails(monkeypatch) -> None:
    monkeypatch.setattr(analyzer.settings, "llm_enabled", True)
    monkeypatch.setattr(analyzer.settings, "llm_api_key", "dummy-key")

    def _raise(*args, **kwargs):  # noqa: ANN002, ANN003
        raise RuntimeError("llm down")

    monkeypatch.setattr(analyzer, "_real_llm_analysis", _raise)
    result = analyzer.analyze_changes("Mock Product", [{"event_type": "promotion_changed"}])
    assert set(result.keys()) == {"summary", "priority", "suggested_action"}
