import pandas as pd
import numpy as np
import streamlit as st
from prophet import Prophet


@st.cache_resource
def run_prophet_model(df: pd.DataFrame):

    model = Prophet(
        yearly_seasonality=True,
        weekly_seasonality=False,
        daily_seasonality=False,
        seasonality_mode="multiplicative"
    )

    model.add_regressor("promotion_indicator")

    prophet_df = pd.DataFrame(
        {"ds": pd.to_datetime(df["date"]), "y": df["nielsen_total_volume"]}
    )

    prophet_df = pd.concat([prophet_df, df["promotion_indicator"]], axis=1)

    model.fit(prophet_df)

    # forecast['yhat'] = total prediction
    # forecast['yhat'] - forecast['promo'] = seasonality
    # forecast['promo'] = promotion

    print("&&&&&&&&&&&&&&&&&&&&& RUN PROPHET MODEL &&&&&&&&&&&&&&&&&&&&&")
    # print(forecast.columns)
    print("&&&&&&&&&&&&&&&&&&&&& RUN PROPHET MODEL &&&&&&&&&&&&&&&&&&&&&")
    return model, prophet_df
