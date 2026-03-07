import pandas as pd
import numpy as np
import streamlit as st
from prophet import Prophet


@st.cache_data
def run_prophet_model(df: pd.DataFrame):
    promo_weeks = df[df["promotion_indicator"] == 1]

    holidays_df = pd.DataFrame(
        {
            "holiday": "promo",
            "ds": pd.to_datetime(promo_weeks["date"]),
            "lower_window": 0,
            "upper_window": 0,
        }
    )

    prophet_df = pd.DataFrame(
        {"ds": pd.to_datetime(df["date"]), "y": df["nielsen_total_volume"]}
    )

    model = Prophet(
        holidays=holidays_df,
        yearly_seasonality=True,
        weekly_seasonality=False,
        daily_seasonality=False,
    )
    model.fit(prophet_df)

    forecast = model.predict(prophet_df)
    # forecast['yhat'] = total prediction
    # forecast['yhat'] - forecast['promo'] = seasonality
    # forecast['promo'] = promotion
    return forecast
