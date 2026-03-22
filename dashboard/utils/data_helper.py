import streamlit as st
import pandas as pd
from src.models.prophet_model import run_prophet_model
from utils.global_const import (
    FLAVOR_MAPPING,
    BRAND_MAPPING,
    MATCH_CAT,
)


def classify_size(size_str):
    size = int("".join(filter(str.isdigit, size_str)))

    if size <= 375:
        return "S"
    elif size <= 850:
        return "M"
    elif size <= 1500:
        return "L"
    else:
        return "XL"


def classify_unit(unit_str):
    unit = int("".join(filter(str.isdigit, unit_str)))

    if unit <= 1:
        return "S"
    elif unit <= 9:
        return "M"
    elif unit <= 18:
        return "L"
    else:
        return "XL"


def classify_flavor(flavor_str):
    return FLAVOR_MAPPING.get(flavor_str, "Misc")


def classify_brand(brand_str):
    return BRAND_MAPPING.get(brand_str, "Misc")


@st.cache_data
def add_categories(df):
    df["brand_cat"] = df["top_brand"].apply(classify_brand)
    df["flavor_cat"] = df["flavor_internal"].apply(classify_flavor)
    df["size_cat"] = df["pack_size_internal"].apply(classify_size)
    df["unit_cat"] = df["units_per_package_internal"].apply(classify_unit)

    df.drop(columns=["top_brand",
                     "flavor_internal",
                     "pack_size_internal",
                     "units_per_package_internal"])
    return df


@st.cache_data
def process_categories(sku: int, df: pd.DataFrame):

    sku_row = df[df["product_sku_code"] == sku].iloc[0]

    results = {}

    sku_df = df[(df["product_sku_code"] == sku)].groupby(
        "date", as_index=False).sum()
    sku_model, sku_prophet_df = run_prophet_model(sku_df)
    pred_sku = sku_model.predict(sku_prophet_df)
    pred_sku.index = pd.to_datetime(sku_prophet_df['ds'])

    actual_volume = sku_df.set_index("date")["nielsen_total_volume"]
    results["residual"] = pred_sku["yhat"] - actual_volume

    results["promotion_indicator"] = sku_df.set_index("date")[
        "promotion_indicator"]

    for name, cols in MATCH_CAT.items():

        mask = pd.Series(True, index=df.index)
        for col in cols:
            mask &= (df[col] == sku_row[col])

        cat_weekly = df[mask].groupby("date")["nielsen_total_volume"].sum()
        others_weekly = (
            df[mask & (df["product_sku_code"] != sku)].
            groupby("date")["nielsen_total_volume"].sum()
        )
        current_share = (others_weekly / cat_weekly).fillna(0)
        # results[f"{name}_other_share_lag"] = current_share.shift(1)
        results[f"{name}_other_share_delta_lag"] = current_share.shift(
            1) - current_share.shift(2)

        group_df = df[mask].groupby("date", as_index=False).sum()
        group_model, group_prophet_df = run_prophet_model(group_df)
        pred_cat = group_model.predict(group_prophet_df)

        pred_cat.index = pd.to_datetime(group_prophet_df['ds'])

        pred_weekly = pred_cat["yhat"]
        pred_others_weekly = pred_cat["yhat"] - pred_sku["yhat"]
        pred_share = (pred_others_weekly / pred_weekly).fillna(0)

        # results[f"{name}_other_share_pred"] = pred_share
        results[f"{name}_other_share_delta_pred"] = pred_share - \
            pred_share.shift(1)

    return pd.DataFrame(results)
    # return results
