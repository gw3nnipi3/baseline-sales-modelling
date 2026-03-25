import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pandas as pd
import numpy as np
import pytest
import contextlib
from unittest.mock import patch
import dashboard.utils.data_tools as dt

# -----------------------------
# Sample DataFrame
# -----------------------------
@pytest.fixture
def fake_df():
    data = {
        "product_sku_code": ["SKU208289", "SKU210553", "SKU281868", "SKU282520"],
        "customer": ["L2_ALBERT HEIJN"] * 4,
        "year": [2022] * 4,
        "yearweek": ["202244"] * 4,
        "date": pd.to_datetime(["2023-11-28"]*4),
        "nielsen_total_volume": [927, 2726, 20410, 5571],
        "promotion_indicator": [0, 0, 0, 0],
        "top_brand": ["FUZE TEA", "FUZE TEA", "COCA-COLA", "FANTA ZERO / NO SUGAR / DIET / LIGHT"],
        "flavor_internal": ["HIBISCUS & PEACH", "LEMON", "COLA", "ORANGE"],
        "pack_type_internal": ["CAN", "CARDBOARD", "PET", "PET"],
        "pack_size_internal": ["250ML", "1500ML", "1500ML", "1500ML"],
        "units_per_package_internal": ["X1", "X1", "X4", "X1"],
        "sku": ["250MLCAN 6X4P FUZETEA PCH HIB",
                "1.5LGTB X8 FUZETEA GREEN",
                "1.5LNRP 4P COCA-COLA",
                "1.5LNRP X6 FTA OR ZSUG"]
    }
    return pd.DataFrame(data)


# -----------------------------
# Filters
# -----------------------------
@pytest.fixture
def filters():
    # List all keys that your FILTER_LIST expects
    filter_keys = [
        "customer",
        "product_sku_code",
        "top_brand",
        "flavor_internal",
        "pack_type_internal",
        "pack_size_internal",
        "units_per_package_internal",
    ]

    # Start with default "----- SELECT -----" for all keys
    filters_dict = {key: "----- SELECT -----" for key in filter_keys}

    # Update the ones you actually want to filter
    """
    filters_dict.update({
        "customer": "L2_ALBERT HEIJN",
        "product_sku_code": "208289",
        "top_brand": "FUZE TEA",
    })
    """

    return filters_dict

# -----------------------------
# Test process_data
# -----------------------------
def test_process_data(fake_df, filters):
    with patch("dashboard.utils.data_tools.load_data", return_value=fake_df):
        result = dt.process_data("ignored.xlsx", filters)
        assert not result.empty
        assert "top_brand" in result.columns


# -----------------------------
# Test get_kpi_data
# -----------------------------
def test_get_kpi_data(fake_df, filters):
    with patch("dashboard.utils.data_tools.load_data", return_value=fake_df):
        total, pct_change = dt.get_kpi_data("ignored.xlsx", filters, "2022-01-01", "2022-12-31")
        assert isinstance(total, np.integer)
        assert isinstance(pct_change, (int, float))


# -----------------------------
# Test add_categories (mock classify_unit if needed)
# -----------------------------
def test_add_categories(fake_df):
    fake_df['unit_cat'] = fake_df['units_per_package_internal'].str.extract(r'X(\d+)').astype(int)

    result = dt.add_categories(fake_df)

    expected_cols = ["unit_cat", "brand_cat", "flavor_cat", "size_cat"]

    for col in expected_cols:
        assert col in result.columns

    # unit_cat should contain category labels
    assert result["unit_cat"].dtype == object
    assert result["unit_cat"].isin(["S", "M", "L", "XL"]).all()

# -----------------------------
# test_process_categories
# -----------------------------

def test_process_categories(fake_df):
    fake_df['date'] = pd.date_range('2023-11-28', periods=len(fake_df))
    fake_df['unit_cat'] = fake_df['units_per_package_internal'].str.extract(r'X(\d+)').astype(int)
    fake_df['brand_cat'] = 'Misc'
    fake_df['flavor_cat'] = 'Misc'
    fake_df['size_cat'] = 'L'
    fake_df['product_sku_code'] = [1,1,2,2]

    dummy_df = fake_df.rename(columns={"date": "ds", "nielsen_total_volume": "y"})

    class DummyModel:
        def predict(self, df_pred):
            # Ensure the columns process_categories expects exist
            return pd.DataFrame({
                "yhat": df_pred.get("y", 0),
                "yhat_lower": df_pred.get("y", 0),
                "yhat_upper": df_pred.get("y", 0),
                "promotion_indicator": df_pred.get("promotion_indicator", 0),
                "bfs_other_share_delta_lag": 0,
                "bfs_other_share_delta_pred": 0,
                "bfu_other_share_delta_lag": 0,
                "bfu_other_share_delta_pred": 0,
                "bfus_other_share_delta_lag": 0,
                "bfus_other_share_delta_pred": 0,
            }, index=df_pred.index)

    with patch("dashboard.utils.data_tools.run_prophet_model", return_value=(DummyModel(), dummy_df)), \
        patch("dashboard.utils.data_tools.st.cache_data", lambda x: x), \
        patch("dashboard.utils.data_tools.st.spinner", lambda text=None: contextlib.nullcontext()):
        result = dt.process_categories(1, fake_df)

    # Check columns that process_categories produces
    for col in ["residual", "promotion_indicator"]:
        assert col in result.columns

# -----------------------------
# test_get_forecast_df
# -----------------------------

def test_get_forecast_df(fake_df, filters):
    fake_df['date'] = pd.date_range('2023-11-28', periods=len(fake_df))
    dummy_df = fake_df.rename(columns={"date": "ds", "nielsen_total_volume": "y"})

    class DummyModel:
        def predict(self, df_pred):
            # Must return 'yhat', 'yhat_lower', 'yhat_upper' for process_categories
            return pd.DataFrame({
                "yhat": df_pred.get("y", 0),
                "yhat_lower": df_pred.get("y", 0),
                "yhat_upper": df_pred.get("y", 0)
            }, index=df_pred.index)

    with patch("dashboard.utils.data_tools.run_prophet_model", return_value=(DummyModel(), dummy_df)), \
         patch("dashboard.utils.data_tools.load_data", return_value=fake_df):
        forecast_df = dt.get_forecast_df("ignored.xlsx", filters, pd.Timestamp("2022-12-01"), set())

    # Use actual column names produced by get_forecast_df
    for col in ["forecast", "lower", "upper"]:
        assert col in forecast_df.columns