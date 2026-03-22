import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from unittest.mock import patch, MagicMock
import pandas as pd
from pathlib import Path

# Adjust import according to your project structure
import dashboard.utils.widget_helpers as wh

@pytest.fixture
def fake_widget():
    return {
        "DATA_SOURCE": "fake_dataset.csv",
        "WIDGET_INDEX": 1,
        "WIDGET_TITLE": "Test Widget",
        "FILTERS": {},
        "START_DATE": "2023-01-01",
        "END_DATE": "2023-01-31",
        "FORECAST_LENGTH": "3M",
        "PROMOTION_WINDOWS": set(),
        "DISPLAY_TYPE": "Forecast",
    }

# -------------------------------
# Test widgetOptionFilter
# -------------------------------
@patch("dashboard.utils.widget_helpers.st.selectbox")
@patch("dashboard.utils.widget_helpers.st.pills", return_value="Concise")
@patch("dashboard.utils.widget_helpers.get_valid_options")
def test_widgetOptionFilter(mock_get_options, mock_pills, mock_selectbox, fake_widget):
    mock_get_options.return_value = {
        "product_sku_code": ["SKU1", "SKU2"],
        "customer": ["Cust1", "Cust2"]
    }
    wh.widgetOptionFilter(fake_widget)
    assert "product_sku_code" in fake_widget["FILTERS"]

def test_widgetOptionFilter_clear(fake_widget):
    wh.widgetOptionFilter(fake_widget, toClear=True)
    for key in wh.FILTER_LIST:
        assert fake_widget["FILTERS"][key] == "----- SELECT -----"

# -------------------------------
# Test widgetOptionDate
# -------------------------------
@patch("dashboard.utils.widget_helpers.load_data")
@patch("dashboard.utils.widget_helpers.st.select_slider")
@patch("dashboard.utils.widget_helpers.st.toggle", return_value=True)
def test_widgetOptionDate(mock_toggle, mock_slider, mock_load_data, fake_widget):
    df = pd.DataFrame({"date": pd.date_range("2023-01-01", periods=5)})
    mock_load_data.return_value = df
    mock_slider.return_value = ("2023-01-01", "2023-01-05")
    wh.widgetOptionDate(fake_widget)
    assert fake_widget["START_DATE"] == "2023-01-01"
    assert fake_widget["END_DATE"] == "2023-01-05"

def test_widgetOptionDate_clear(fake_widget):
    df = pd.DataFrame({"date": pd.date_range("2023-01-01", periods=5)})
    with patch("dashboard.utils.widget_helpers.load_data", return_value=df):
        wh.widgetOptionDate(fake_widget, toClear=True)
        assert fake_widget["START_DATE"] == "2023-01-01"
        assert fake_widget["END_DATE"] == "2023-01-05"

# -------------------------------
# Test createKPI
# -------------------------------
@patch("dashboard.utils.widget_helpers.st.metric")
@patch("dashboard.utils.widget_helpers.get_kpi_data", return_value=(100, 0.05))
def test_createKPI(mock_kpi, mock_metric, fake_widget):
    wh.createKPI(fake_widget)
    mock_metric.assert_called_with("Total Sales", value=100, delta="5.0%")

# -------------------------------
# Test createForecastOption
# -------------------------------
@patch("dashboard.utils.widget_helpers.st.columns")
@patch("dashboard.utils.widget_helpers.process_forecast_length", return_value=(3, "months (4 weeks)", pd.Timedelta(weeks=12)))
def test_createForecastOption(mock_process, mock_columns, fake_widget):
    mock_col_instance = [MagicMock(), MagicMock()]
    mock_columns.return_value = mock_col_instance
    mock_col_instance[0].number_input.return_value = 3
    mock_col_instance[1].selectbox.return_value = "months (4 weeks)"
    wh.createForecastOption(fake_widget)
    assert fake_widget["FORECAST_LENGTH"] == "3M"

# -------------------------------
# Test createPromotionOption
# -------------------------------
@patch("dashboard.utils.widget_helpers.st.columns")
@patch("dashboard.utils.widget_helpers.process_forecast_length", return_value=(3, "months (4 weeks)", pd.Timedelta(weeks=12)))
def test_createPromotionOption(mock_process, mock_columns, fake_widget):
    mock_col_instance = [MagicMock(), MagicMock()]
    mock_columns.return_value = mock_col_instance
    mock_col_instance[0].slider.return_value = pd.Timestamp("2023-02-01")
    mock_col_instance[1].number_input.return_value = 2
    mock_col_instance[0].button.return_value = True
    wh.createPromotionOption(fake_widget)
    assert len(fake_widget["PROMOTION_WINDOWS"]) > 0

# -------------------------------
# Test createForecast
# -------------------------------
@patch("dashboard.utils.widget_helpers.get_forecast_df", return_value=pd.DataFrame())
@patch("dashboard.utils.widget_helpers.plot_forecast_with_promos")
@patch("dashboard.utils.widget_helpers.st.pyplot")
@patch("dashboard.utils.widget_helpers.st.columns")
@patch("dashboard.utils.widget_helpers.createForecastOption")
@patch("dashboard.utils.widget_helpers.createPromotionOption")
@patch("dashboard.utils.widget_helpers.st.write")
def test_createForecast(mock_write, mock_promo, mock_forecast_option, mock_columns,
                        mock_pyplot, mock_plot_forecast, mock_get_forecast, fake_widget):
    mock_columns.return_value = [MagicMock(), MagicMock(), MagicMock()]
    wh.createForecast(fake_widget)
    mock_get_forecast.assert_called()

# -------------------------------
# Test createPredObs
# -------------------------------
@patch("dashboard.utils.widget_helpers.st.line_chart")
@patch("dashboard.utils.widget_helpers.st.write")
@patch("dashboard.utils.widget_helpers.get_pred_obs_df", return_value=pd.DataFrame({"yhat": [1,2,3], "ds": pd.date_range("2023-01-01", periods=3)}))
@patch("dashboard.utils.widget_helpers.process_data", return_value=pd.DataFrame({
    "date": pd.date_range("2023-01-01", periods=3),
    "nielsen_total_volume": [1,2,3]
}))
def test_createPredObs(mock_process, mock_pred_obs, mock_write, mock_line, fake_widget):
    wh.createPredObs(fake_widget)
    mock_line.assert_called()

# -------------------------------
# Test createBacktest
# -------------------------------
@patch("dashboard.utils.widget_helpers.st.pyplot")
@patch("dashboard.utils.widget_helpers.st.write")
@patch("dashboard.utils.widget_helpers.get_performance_metrics", return_value=pd.DataFrame())
@patch("dashboard.utils.widget_helpers.plot_cross_validation_metric")
def test_createBacktest(mock_plot_cv, mock_perf, mock_write, mock_pyplot, fake_widget):
    wh.createBacktest(fake_widget)
    mock_plot_cv.assert_called()

# -------------------------------
# Test createDecomposition
# -------------------------------
@patch("dashboard.utils.widget_helpers.st.line_chart")
@patch("dashboard.utils.widget_helpers.st.write")
@patch("dashboard.utils.widget_helpers.get_pred_obs_df", return_value=pd.DataFrame({
    "ds": pd.date_range("2023-01-01", periods=3),
    "trend": [1,2,3],
    "multiplicative_terms": [1,1,1],
    "extra_regressors_multiplicative": [0.1,0.2,0.3],
    "yhat": [1,2,3]
}))
@patch("dashboard.utils.widget_helpers.process_data", return_value=pd.DataFrame({
    "date": pd.date_range("2023-01-01", periods=3),
    "nielsen_total_volume": [1,2,3]
}))
def test_createDecomposition(mock_process, mock_pred_obs, mock_write, mock_line, fake_widget):
    wh.createDecomposition(fake_widget)
    mock_line.assert_called()