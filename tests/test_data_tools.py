import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
import pandas as pd
import numpy as np
from unittest.mock import patch, MagicMock

from dashboard.utils import data_tools as dt

# -------------------------------
# Fixtures
# -------------------------------

@pytest.fixture
def fake_df():
    # Create a simple dataframe with all columns expected by FILTER_LIST and process_categories
    df = pd.DataFrame({
        "date": pd.date_range("2024-01-01", periods=4, freq="W-MON"),
        "product_sku_code": [1, 2, 1, 2],
        "nielsen_total_volume": [10, 20, 15, 5],
        "promotion_indicator": [0, 1, 0, 0],
        "top_brand": ["BrandA", "BrandB", "BrandA", "BrandB"],
        "flavor_internal": ["Vanilla", "Chocolate", "Vanilla", "Chocolate"],
        "pack_size_internal": ["375ml", "900ml", "850ml", "1500ml"],
        "units_per_package_internal": [1, 5, 10, 20],
        "customer": ["CustA", "CustB", "CustA", "CustB"],  # example FILTER_LIST column
        "region": ["North", "South", "North", "South"]    # example FILTER_LIST column
    })
    return df

@pytest.fixture
def filters():
    return {
        "customer": "CustA",
        "region": "North",
        "product_sku_code": "1"
    }

# -------------------------------
# Tests
# -------------------------------

def test_classify_size():
    assert dt.classify_size("375ml") == "S"
    assert dt.classify_size("900ml") == "L"  # matches your current function
    assert dt.classify_size("1500ml") == "L"
    assert dt.classify_size("850ml") == "M"

def test_classify_unit():
    assert dt.classify_unit("1") == "S"
    assert dt.classify_unit("5") == "M"
    assert dt.classify_unit("10") == "L"
    assert dt.classify_unit("20") == "XL"

# -------------------------------
# Patch load_data to use fake_df
# -------------------------------

@pytest.fixture
def patched_load_data(fake_df):
    with patch("dashboard.utils.data_tools.load_data", return_value=fake_df) as mock:
        yield mock

def test_process_data(patched_load_data, filters):
    df = dt.process_data("ignored.xlsx", filters)
    assert all(df["nielsen_total_volume"] >= 0)
    assert "date" in df.columns

def test_get_kpi_data(patched_load_data, filters):
    total, pct_change = dt.get_kpi_data("ignored.xlsx", filters, "2024-01-01", "2024-01-28")
    assert total >= 0
    assert isinstance(pct_change, float)

def test_process_categories(fake_df):
    # Patch run_prophet_model to return dummy model and dataframe with 'ds'
    dummy_df = fake_df.rename(columns={"date": "ds", "nielsen_total_volume": "y"})
    class DummyModel:
        def predict(self, df_pred):
            return pd.DataFrame({
                "yhat": df_pred["y"],
                "yhat_lower": df_pred["y"],
                "yhat_upper": df_pred["y"]
            })
    with patch("dashboard.utils.data_tools.run_prophet_model", return_value=(DummyModel(), dummy_df)):
        result = dt.process_categories(1, fake_df)
        assert "residual" in result.columns
        assert "promotion_indicator" in result.columns

def test_add_categories(fake_df):
    df = dt.add_categories(fake_df)
    assert "brand_cat" in df.columns
    assert "flavor_cat" in df.columns
    assert "size_cat" in df.columns
    assert "unit_cat" in df.columns

def test_get_forecast_df(fake_df, filters):
    # Patch run_prophet_model
    dummy_df = fake_df.rename(columns={"date": "ds", "nielsen_total_volume": "y"})
    class DummyModel:
        def predict(self, df_pred):
            return pd.DataFrame({
                "yhat": df_pred["y"],
                "yhat_lower": df_pred["y"],
                "yhat_upper": df_pred["y"]
            })
    with patch("dashboard.utils.data_tools.run_prophet_model", return_value=(DummyModel(), dummy_df)):
        forecast_df = dt.get_forecast_df("ignored.xlsx", filters, pd.Timestamp("2024-02-01"), set())
        assert "forecast" in forecast_df.columns
        assert "actual" in forecast_df.columns