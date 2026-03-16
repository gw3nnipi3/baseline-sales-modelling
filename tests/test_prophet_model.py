import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
import pandas as pd
import numpy as np
from prophet import Prophet

from src.models.prophet_model import run_prophet_model

def make_sample_data(n=10):
    dates = pd.date_range(start="2023-01-01", periods=n, freq="W")
    nielsen_total_volume = np.random.randint(100, 500, size=n)
    promotion_indicator = np.random.randint(0, 2, size=n)
    df = pd.DataFrame({
        "date": dates,
        "nielsen_total_volume": nielsen_total_volume,
        "promotion_indicator": promotion_indicator
    })
    return df


def test_run_prophet_model_returns_types():
    df = make_sample_data()
    model, prophet_df = run_prophet_model(df)

    # Check that the model is a Prophet instance
    assert isinstance(model, Prophet), "Returned model should be a Prophet instance"

    # Check that the dataframe is a pandas DataFrame
    assert isinstance(prophet_df, pd.DataFrame), "Returned prophet_df should be a DataFrame"

    # Check columns
    expected_cols = {"ds", "y", "promotion_indicator"}
    assert expected_cols.issubset(prophet_df.columns), "prophet_df missing expected columns"

    # Check row count
    assert len(prophet_df) == len(df), "prophet_df should have same number of rows as input df"


def test_run_prophet_model_empty_dataframe():
    df = pd.DataFrame(columns=["date", "nielsen_total_volume", "promotion_indicator"])
    with pytest.raises(ValueError):
        run_prophet_model(df)