"""Tests for market data utilities."""

import pytest

from data import normalize_nse_symbol


def test_normalize_nse_symbol_adds_suffix() -> None:
    assert normalize_nse_symbol("reliance") == "RELIANCE.NS"


def test_normalize_nse_symbol_keeps_index_symbol() -> None:
    assert normalize_nse_symbol("^NSEI") == "^NSEI"


def test_normalize_nse_symbol_rejects_blank() -> None:
    with pytest.raises(ValueError):
        normalize_nse_symbol(" ")
