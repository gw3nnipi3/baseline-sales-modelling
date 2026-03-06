import streamlit as st
import pandas as pd
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
    print("---------- PROCESS DATE ----------")
    print(df.tail())
    print("---------- PROCESS DATE ----------")
    df["date"] = pd.to_datetime(df["yearweek"].astype(str) + "-1", format="%G%V-%u")
    df = df.sort_values("date", ascending=True)

    return df


def get_valid_options(filename: str, filters: dict[str, str]) -> dict[str, list[str]]:
    df = load_data(filename)

    for key in FILTER_LIST:
        if filters[key] != "----- SELECT -----":
            df = df[df[key].astype(str) == filters[key]]

    # print("------PROCESS DATA-----")
    ## print(filters)

    # print(df.tail())
    # print("------PROCESS DATA-----")

    valid_options = dict()
    for key in filters:
        valid_options[key] = df[key].unique().astype(str).tolist()
        valid_options[key].sort()
        valid_options[key] = ["----- SELECT -----"] + valid_options[key]
    return valid_options


def process_data(filename: str, filter: dict[str, str]):
    og_df = load_data(filename)
    df = og_df.copy()
    # ---------- cumulate data ----------
    for key in FILTER_LIST:
        if filter[key] == "----- SELECT -----":
            continue

        match_value = filter[key]
        if key == "product_sku_code":
            match_value = int(match_value)
        df = df[df[key] == match_value]

    df = df.groupby(by=["date"], as_index=False).sum()
    print("||||||| PROCESS DATA |||||||")
    print(df.tail())
    print(df.columns)
    print("||||||| PROCESS DATA |||||||")
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

    prev_range = df[df["date"].between(prev_sd, prev_ed)]["nielsen_total_volume"].sum()

    pct_change = 0
    if prev_range != 0:
        pct_change = (this_range - prev_range) / prev_range
    return this_range, pct_change
