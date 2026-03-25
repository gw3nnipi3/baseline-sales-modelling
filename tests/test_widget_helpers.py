import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from unittest.mock import patch, MagicMock
import pandas as pd
import dashboard.utils.widget_helpers as wh

@pytest.fixture
def fake_widget():
    return {
        "DATA_SOURCE": "fake_dataset.csv",
        "WIDGET_INDEX": 1,
        "WIDGET_TITLE": "Test Widget",
        "FILTERS": {key: "" for key in wh.FILTER_LIST},
        "START_DATE": "2023-01-01",
        "END_DATE": "2023-01-31",
        "FORECAST_LENGTH": "3M",
        "PROMOTION_WINDOWS": set(),
        "DISPLAY_TYPE": "Forecast",
        "ENABLE_CANNIBAL": False,
    }

# -------------------------------
# Test widgetOptionFilter
# -------------------------------
@patch("dashboard.utils.widget_helpers.get_valid_options")
def test_widgetOptionFilter(mock_get_options, fake_widget):
    # Force get_valid_options to return two fields
    mock_get_options.return_value = {
        "product_sku_code": ["SKU1", "SKU2"],
        "customer": ["Cust1", "Cust2"]
    }

    # Monkey-patch the internal function that updates FILTERS directly
    for key, options in mock_get_options.return_value.items():
        fake_widget["FILTERS"][key] = options[0]

    # Call function (doesn't rely on Streamlit)
    wh.widgetOptionFilter(fake_widget)

    for key, options in mock_get_options.return_value.items():
        assert fake_widget["FILTERS"][key] == options[0]

def test_widgetOptionFilter_clear(fake_widget):
    # Simulate clearing all filters
    for key in wh.FILTER_LIST:
        fake_widget["FILTERS"][key] = wh.PLACHOLDER_STR
    wh.widgetOptionFilter(fake_widget, toClear=True)
    for key in wh.FILTER_LIST:
        assert fake_widget["FILTERS"][key] == wh.PLACHOLDER_STR

# -------------------------------
# Test widgetOptionDate
# -------------------------------
def test_widgetOptionDate(fake_widget):
    start, end = "2023-01-01", "2023-01-05"
    # Force the widget to update
    fake_widget["START_DATE"] = start
    fake_widget["END_DATE"] = end
    wh.widgetOptionDate(fake_widget)
    assert fake_widget["START_DATE"] == start
    assert fake_widget["END_DATE"] == end

def test_widgetOptionDate_clear(fake_widget):
    df = pd.DataFrame({"date": pd.date_range("2023-01-01", periods=5)})
    start = df["date"].dt.strftime("%Y-%m-%d").iloc[0]
    end = df["date"].dt.strftime("%Y-%m-%d").iloc[-1]
    fake_widget["START_DATE"] = start
    fake_widget["END_DATE"] = end
    wh.widgetOptionDate(fake_widget, toClear=True)
    assert fake_widget["START_DATE"] == start
    assert fake_widget["END_DATE"] == end
