import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Any
from datetime import date
from utils.global_const import *


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
    df["date"] = pd.to_datetime(df["yearweek"].astype(str) + "-1", format="%G%V-%u")
    df = df.sort_values("date", ascending=True)

    return df


def process_data(filename: str, product_sku_code: int | None, customer: str | None):
    df = load_data(filename)
    # ---------- cumulate data ----------
    if product_sku_code and customer:
        df = df[
            (df["product_sku_code"] == product_sku_code) & (df["customer"] == customer)
        ]
    elif product_sku_code and not customer:
        df = df[df["product_sku_code"] == product_sku_code]
        df = df.groupby(by=["date"]).sum()
    elif not product_sku_code and customer:
        df = df[df["customer"] == customer]
        df = df.drop(columns="product_sku_code").groupby(by=["date"]).sum()
    else:
        df = df.groupby(by=["date"]).sum()

    print("------PROCESS DATA-----")
    # print(final_display.tail())
    print(df["nielsen_total_volume"].tail())
    print("------PROCESS DATA-----")
    return df


def get_valid_options(filename: str, filters: dict[str, str]) -> dict[str, list[str]]:
    filter_list = [
        "WIDGET_INDEX",
        "WIDGET_TITLE",
        "DATA_SOURCE",
        "DISPLAY_TYPE",
        "MODEL_TYPE",  # for the future
        "FILTER_TYPE",
        "FILTERS",
    ]

    df = load_data(filename)
    # if filter_type == "Concise":
    #     for key in FILTER_LIST:
    #         if filters[key] != "----- SELECT -----":
    #             df = df[df[key] == filters[key]]

    # elif filter_type == "Verbose":
    #     for key in FILTER_LIST:
    #         if filters[key] != "----- SELECT -----":
    #             df = df[df[key] == filters[key]]

    # else:
    #     print("INVALID FILTER TYPE")

    for key in FILTER_LIST:
        if filters[key] != "----- SELECT -----":
            df = df[df[key].astype(str) == filters[key]]

    print("------PROCESS DATA-----")
    # print(filters)

    print(df.tail())
    print("------PROCESS DATA-----")

    valid_options = dict()
    for key in filters:
        valid_options[key] = df[key].unique().astype(str).tolist()
        valid_options[key] = ["----- SELECT -----"] + valid_options[key]
    return valid_options
