import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


import pytest
from unittest.mock import patch, MagicMock
import pandas as pd
import io
import streamlit as st

import dashboard.utils.ui_tools as ui


@pytest.fixture
def reset_session_state():
    """Reset Streamlit session state for each test."""
    st.session_state.widgets = []
    st.session_state.widget_index = 0
    yield
    st.session_state.widgets = []
    st.session_state.widget_index = 0


def test_safeParse():
    # None / empty / NaN
    assert ui.safeParse(None) is None
    assert ui.safeParse("") is None
    assert ui.safeParse(float("nan")) is None

    # literal_eval
    assert ui.safeParse("[1,2,3]") == [1, 2, 3]
    assert ui.safeParse("{'a': 1}") == {"a": 1}

    # fallback to string on error
    assert ui.safeParse("invalid") == "invalid"


def test_saveConfig(reset_session_state):
    widget_data = {"DATA_SOURCE": "ds", "DISPLAY_TYPE": "KPI", "WIDGET_TITLE": "My Widget"}
    ui.saveConfig("My Widget", "ds", "KPI", widget_data)

    # Check session state updated
    assert len(st.session_state.widgets) == 1
    w = st.session_state.widgets[0]
    assert w["DATA_SOURCE"] == "ds"
    assert w["DISPLAY_TYPE"] == "KPI"
    assert w["WIDGET_TITLE"] == "My Widget"
    assert w["WIDGET_INDEX"] == 1
    assert st.session_state.widget_index == 1


def test_exportLayout(reset_session_state):
    # Prepare session state
    ui.saveConfig("Widget1", "ds1", "KPI")
    ui.saveConfig("Widget2", "ds2", "Forecast")
    
    csv_bytes = ui.exportLayout()
    assert isinstance(csv_bytes, bytes)

    # Load CSV back and check content
    df = pd.read_csv(io.BytesIO(csv_bytes))
    assert df["WIDGET_TITLE"].tolist() == ["Widget1", "Widget2"]
    assert df["DISPLAY_TYPE"].tolist() == ["KPI", "Forecast"]


def test_importLayout(tmp_path, reset_session_state):
    # Prepare a CSV layout
    csv_path = tmp_path / "layout.csv"
    df = pd.DataFrame({
        "DATA_SOURCE": ["ds1", "ds2"],
        "DISPLAY_TYPE": ["KPI", "Forecast"],
        "WIDGET_TITLE": ["W1", "W2"],
        "WIDGET_INDEX": [1, 2],
        "FILTERS": ["{}", "{}"],
        "PROMOTION_WINDOWS": ["[]", "[]"]
    })
    df.to_csv(csv_path, index=False)

    ui.importLayout(str(csv_path))
    
    # Check widgets loaded
    assert len(st.session_state.widgets) == 2
    assert st.session_state.widgets[0]["WIDGET_TITLE"] == "W1"
    assert st.session_state.widgets[1]["WIDGET_TITLE"] == "W2"
    assert st.session_state.widget_index == 2


@patch("dashboard.utils.ui_tools.st")
def test_match_and_render(mock_st):
    # Mock all create functions
    for fn in ["createKPI","createForecast","createPredObs","createBacktest","createDecomposition"]:
        setattr(ui, fn, MagicMock())

    widgets = [
        {"DISPLAY_TYPE": "KPI"},
        {"DISPLAY_TYPE": "Forecast"},
        {"DISPLAY_TYPE": "Predicted Vs. Observed"},
        {"DISPLAY_TYPE": "Backtest Performance"},
        {"DISPLAY_TYPE": "Decomposition"},
        {"DISPLAY_TYPE": "Other"},
    ]
    
    for w in widgets:
        ui.match_and_render(w)

    ui.createKPI.assert_called_once()
    ui.createForecast.assert_called_once()
    ui.createPredObs.assert_called_once()
    ui.createBacktest.assert_called_once()
    ui.createDecomposition.assert_called_once()
    mock_st.success.assert_called_once_with("widget display for Other")