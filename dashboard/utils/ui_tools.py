import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Any
from datetime import date

# NOTE: Widget render function
widgetType = ["Line", "Bar", "Scatter"]
widgetSettings = [
    "WIDGET_INDEX",
    "DATA_SOURCE",
    "DISPLAY_TYPE",
    "PRODUCT_SKU_CODE",
    "START_DATE",
    "END_DATE",
]


def renderWidget(widget: dict[str, Any]):
    data_source = widget["DATA_SOURCE"]
    display_type = widget["DISPLAY_TYPE"]

    df = pd.DataFrame({})
    if data_source.endswith(".csv"):
        df = pd.read_csv(f"data/{data_source}")
    elif data_source.endswith(".xlsx"):
        df = pd.read_excel(f"data/{data_source}")
    else:
        st.error("invalid file format")

    product_sku_code = widget.get("PRODUCT_SKU_CODE", None)
    sku_codes = df["product_sku_code"].unique().tolist()
    default_idx = (
        0 if product_sku_code not in sku_codes else sku_codes.index(product_sku_code)
    )
    product_sku_code = st.selectbox(
        "Product Code",
        sku_codes,
        key=f"{widget['WIDGET_INDEX']}_sku",
        index=default_idx,
    )

    print("-----------")
    print(widget["WIDGET_INDEX"])
    print(st.session_state.widgets)
    print("-----------")
    st.session_state.widgets[widget["WIDGET_INDEX"]]["PRODUCT_SKU_CODE"] = (
        product_sku_code
    )
    df = df[df["product_sku_code"] == product_sku_code]
    df = df.set_index("yearweek")[["nielsen_total_volume"]]

    match display_type:
        case "Line":
            _ = st.line_chart(df)
        case "Bar":
            _ = st.bar_chart(df)
        case "Scatter":
            _ = st.scatter_chart(df)
        case _:
            pass


def renderAll():
    widgetCols = st.columns(3)
    for i, widget in enumerate(st.session_state.widgets):
        col = i % 3
        # if not w:
        #     break
        with widgetCols[col]:
            print("------------------------")
            print(widget)
            print(widget["WIDGET_INDEX"])
            print("------------------------")
            renderWidget(widget)


def saveConfig(data_source: str, display_type: str, widget: dict[str, Any] = dict()):
    w = dict()
    for s in widgetSettings:
        w[s] = widget.get(s, None)

    w["DATA_SOURCE"] = widget.get("DATA_SOURCE", data_source)
    w["DISPLAY_TYPE"] = widget.get("DISPLAY_TYPE", display_type)

    w["WIDGET_INDEX"] = st.session_state.widget_index
    st.session_state.widget_index += 1

    st.session_state.widgets.append(w)


# NOTE: Layout Function
# @st.cache_data
def exportLayout(widgets: list[dict[str, Any]]):
    data = {"DATA_SOURCE": [], "DISPLAY_TYPE": []}
    for widget in widgets:
        for s in widgetSettings:
            data[s] = data.get(s, [])
            data[s].append(widget.get(s, None))

    df = pd.DataFrame(data)
    return df.to_csv().encode("utf-8")


def importLayout(csvLayout):
    if csvLayout is not None:
        st.session_state.widgets = []
        dfLayout = pd.read_csv(csvLayout)
        dfLayout = dfLayout.sort_values(by="WIDGET_INDEX")

        for i in range(len(dfLayout)):
            widget = dict()
            for s in widgetSettings:
                widget[s] = dfLayout[s].iloc[i]

            saveConfig(widget["DATA_SOURCE"], widget["DISPLAY_TYPE"], widget)
        st.session_state.widget_index = dfLayout["WIDGET_INDEX"].max()
