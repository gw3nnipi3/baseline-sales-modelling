import streamlit as st
import pandas as pd
from src.models.prophet_model import run_prophet_model
from prophet.diagnostics import cross_validation, performance_metrics
from utils.global_const import (
    WIDGET_COLUMN_COUNT,
    WIDGET_DISPLAY_TYPE,
    WIDGET_SETTING,
    FILTER_LIST,
)


@st.cache_data
def load_data(filename: str):
    df = pd.DataFrame()
    if filename.endswith(".csv"):
        df = pd.read_csv(f"data/{filename}")
    elif filename.endswith(".xlsx"):
        df = pd.read_excel(f"data/{filename}")
    else:
        st.error("Invalid File Format")

    # ---------- process date ----------
    # print("---------- PROCESS DATE ----------")
    # print(df.tail())
    # print("---------- PROCESS DATE ----------")
    df["date"] = pd.to_datetime(
        df["yearweek"].astype(str) + "-1", format="%G%V-%u")
    df = df.sort_values("date", ascending=True)

    # ------------ clean data ------------
    all_dates = pd.DataFrame({"date": pd.date_range(
        start=df["date"].min(), end=df["date"].max(), freq="W-MON"
    )})
    all_products = pd.DataFrame(
        {"product_sku_code": df["product_sku_code"].unique()})

    cleaned_df = all_dates.merge(all_products, how="cross")

    complete_df = cleaned_df.merge(
        df, on=["date", "product_sku_code"], how="left")

    target_cols = complete_df.columns.difference(
        ["product_sku_code", "date", "nielsen_total_volume", "promotion_indicator"])

    lookup_table = df.drop_duplicates(
        "product_sku_code").set_index("product_sku_code")

    for col in target_cols:
        complete_df[col] = complete_df[col].fillna(
            complete_df["product_sku_code"].map(lookup_table[col]))
    complete_df["nielsen_total_volume"] = complete_df["nielsen_total_volume"].fillna(
        0)
    complete_df["promotion_indicator"] = complete_df["promotion_indicator"].fillna(
        0)

    print("--------------- COMPLETE DATA ---------------")
    print(complete_df.tail())
    # print(complete_df[["product_sku_code", "nielsen_total_volume"]].tail)
    print("--------------- COMPLETE DATA ---------------")

    return complete_df


def get_valid_options(
        filename: str,
        filters: dict[str, str]
) -> dict[str, list[str]]:
    df = load_data(filename)

    for key in FILTER_LIST:
        if filters[key] != "----- SELECT -----":
            df = df[df[key].astype(str) == filters[key]]

    # print("------PROCESS DATA-----")
    # print(filters)

    # print(df.tail())
    # print("------PROCESS DATA-----")

    valid_options = dict()
    for key in filters:
        valid_options[key] = df[key].unique().astype(str).tolist()
        valid_options[key].sort()
        valid_options[key] = ["----- SELECT -----"] + valid_options[key]
    return valid_options


def process_data(filename: str, filters: dict[str, str]):
    df = load_data(filename)
    # ---------- cumulate data ----------
    for key in FILTER_LIST:
        if filters[key] == "----- SELECT -----":
            continue

        match_value = filters[key]
        if key == "product_sku_code":
            match_value = int(match_value)
        df = df[df[key] == match_value]

    df = df.drop(columns=["product_sku_code"])
    df = df.groupby(by=["date"], as_index=False).sum()
    # print("||||||| PROCESS DATA |||||||")
    # print(df.tail())
    # print(df.columns)
    # print("||||||| PROCESS DATA |||||||")
    return df


def get_kpi_data(
    filename: str, filters: dict[str, str], start_date: str, end_date: str
):
    df = process_data(filename, filters)

    sd = pd.to_datetime(start_date)
    ed = pd.to_datetime(end_date)

    this_range = df[df["date"].between(sd, ed)]["nielsen_total_volume"].sum()

    min_date = df["date"].min()
    delta = ed - sd
    prev_ed = sd - pd.Timedelta(weeks=1)
    prev_ed = prev_ed if prev_ed >= min_date else min_date
    prev_sd = prev_ed - delta
    prev_sd = prev_sd if prev_sd >= min_date else min_date

    prev_range = df[df["date"].between(
        prev_sd, prev_ed)]["nielsen_total_volume"].sum()

    pct_change = 0
    if prev_range != 0:
        pct_change = (this_range - prev_range) / prev_range
    return this_range, pct_change


def get_forecast_df(
    filename: str, filters: dict[str, str], target_date: pd.Timestamp
):
    df = process_data(filename, filters)
    model, prophet_df = run_prophet_model(df)
    prophet_df["ds"] = pd.to_datetime(prophet_df["ds"])
    target_date = pd.to_datetime(target_date)

    current_max = prophet_df["ds"].max()

    new_dates = pd.date_range(
        start=current_max + pd.Timedelta(weeks=1),
        end=target_date,
        freq="W-MON"
    )

    future_df = pd.DataFrame({"ds": new_dates, "promotion_indicator": 0})
    pred = model.predict(future_df)

    history = pd.DataFrame({
        "date": prophet_df["ds"],
        "actual": prophet_df["y"],
        "forecast": None,
        "lower": None,
        "upper": None,
    })

    forecast = pd.DataFrame({
        "date": new_dates,
        "actual": None,
        "forecast": pred["yhat"],
        "lower": pred["yhat_lower"],
        "upper": pred["yhat_upper"],
    })

    final_df = pd.concat([history, forecast], ignore_index=True)

    return final_df


def get_pred_obs_df(
    filename: str, filters: dict[str, str], start_date: str, end_date: str
):
    df = process_data(filename, filters)
    model, prophet_df = run_prophet_model(df)
    forecast = model.predict(prophet_df)
    forecast = forecast.reset_index()

    sd = pd.to_datetime(start_date)
    ed = pd.to_datetime(end_date)
    print("-------------------- FORECAST --------------------")
    print(forecast.tail())
    print("-------------------- FORECAST --------------------")
    forecast = forecast[forecast["ds"].between(sd, ed)]
    # forecast['yhat'] = total prediction
    # forecast['yhat'] - forecast['extra_regressors_additive'] = seasonality
    # forecast['extra_regressors_additive'] = promotion
    return forecast


@st.cache_data
def get_performance_metrics(
    filename: str, filters: dict[str, str]
) -> pd.DataFrame:
    df = process_data(filename, filters)
    model, prophet_df = run_prophet_model(df)

    df_cv = cross_validation(
        model,
        initial="366 days",
        period="90 days",
        horizon="180 days",
        parallel="processes",
    )

    # df_metrics = performance_metrics(df_cv)
    return df_cv
