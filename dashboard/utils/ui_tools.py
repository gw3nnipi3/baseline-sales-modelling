import streamlit as st
import pandas as pd
from typing import Any
from utils.data_tools import *
from utils.global_const import *
import ast

# NOTE: Widget render function


def renderWidget(widget: dict[str, Any]):
    data_source = widget["DATA_SOURCE"]
    display_type = widget["DISPLAY_TYPE"]
    widget_idx = widget["WIDGET_INDEX"]

    # NOTE: REVAMPED RENDER WIGET
    df = pd.DataFrame({})
    df = load_data(data_source)

    widget["FILTERS"] = (
        {key: "----- SELECT -----" for key in FILTER_LIST}
        if not widget["FILTERS"]
        else widget["FILTERS"]
    )

    with st.popover("Options"):
        filter_selection = "Concise"
        filter_selection = st.pills(
            "Filter Type",
            ["Concise", "Verbose"],
            selection_mode="single",
            default="Concise",
            key=f"{widget_idx}_filter_selection",
        )

        valid_options = get_valid_options(data_source, widget["FILTERS"])

        print("-------------------------- RENDER WIDGET --------------------------")
        print(widget)
        print("-------------------------- RENDER WIDGET --------------------------")
        if filter_selection == "Concise":
            for key in FILTER_LIST:
                if key not in ["product_sku_code", "customer"]:
                    continue

                current_value = widget["FILTERS"][key]
                print(key, current_value)
                safe_index = 0
                if current_value in valid_options[key]:
                    safe_index = valid_options[key].index(current_value)
                else:
                    safe_index = 0

                widget["FILTERS"][key] = st.selectbox(
                    key,
                    valid_options[key],
                    key=f"{widget_idx}_{key}",
                    index=safe_index,
                )

                valid_options = get_valid_options(data_source, widget["FILTERS"])

            # print("-------------------------- AFT SELECT --------------------------")
            # valid_options = get_valid_options(
            #     data_source, widget["FILTER_TYPE"], widget["FILTERS"]
            # )
            # print("-------------------------- AFT SELECT --------------------------")
        elif filter_selection == "Verbose":
            for key in FILTER_LIST:
                if key in ["product_sku_code", "customer"]:
                    continue

                current_value = widget["FILTERS"][key]
                print(key, current_value)
                safe_index = 0
                if current_value in valid_options[key]:
                    safe_index = valid_options[key].index(current_value)
                else:
                    safe_index = 0

                widget["FILTERS"][key] = st.selectbox(
                    key,
                    valid_options[key],
                    key=f"{widget_idx}_{key}",
                    index=safe_index,
                )

                valid_options = get_valid_options(data_source, widget["FILTERS"])

                # print(
                #     "-------------------------- AFT SELECT II --------------------------"
                # )
                # valid_options = get_valid_options(
                #     data_source, widget["FILTER_TYPE"], widget["FILTERS"]
                # )

                # print(
                #     "-------------------------- AFT SELECT II --------------------------"
                # )
        else:
            st.write("Select Filter Type to Continue")

        if st.button("Clear Option", key=f"{widget_idx}_clear_btn"):
            widget["FILTERS"] = {key: "----- SELECT -----" for key in FILTER_LIST}
            st.rerun()

    # NOTE:---------------------

    # product_sku_code, customer = (
    #     widget.get("PRODUCT_SKU_CODE", None),
    #     widget.get("", None),
    # )
    # default_idx = (
    #     0 if product_sku_code not in sku_codes else sku_codes.index(product_sku_code)
    # )

    # product_sku_code = st.selectbox(
    #     "Product Code",
    #     sku_codes,
    #     key=f"{widget_idx}_sku",
    #     index=default_idx,
    # )
    # widget["PRODUCT_SKU_CODE"] = product_sku_code

    # # print("+++++++++++")
    # # print(widget["WIDGET_INDEX"])
    # # print(st.session_state.widgets)
    # # print("+++++++++++")
    # df = process_data(data_source, product_sku_code, customer)

    # match display_type:
    #     case "Line":
    #         _ = st.line_chart(df["nielsen_total_volume"])
    #     case "Bar":
    #         _ = st.bar_chart(df["nielsen_total_volume"])
    #     case "Scatter":
    #         _ = st.scatter_chart(df["nielsen_total_volume"])
    #     case _:
    #         pass


def renderAll():
    widgetCols = st.columns(WIDGET_COLUMN_COUNT)
    for i, widget in enumerate(st.session_state.widgets):
        col = i % WIDGET_COLUMN_COUNT

        with widgetCols[col]:
            renderWidget(widget)
            print("|||||||||| RENDER ALL ||||||||||")
            print(widget)
            print("|||||||||| RENDER ALL ||||||||||")


def saveConfig(data_source: str, display_type: str, widget: dict[str, Any] = dict()):
    w = dict()
    for s in WIDGET_SETTING:
        w[s] = widget.get(s, None)

    w["DATA_SOURCE"] = widget.get("DATA_SOURCE", data_source)
    w["DISPLAY_TYPE"] = widget.get("DISPLAY_TYPE", display_type)

    index = 0
    if not widget or not widget.get("WIDGET_INDEX", None):
        st.session_state.widget_index += 1
        index = st.session_state.widget_index
    else:
        index = widget["WIDGET_INDEX"]

    w["WIDGET_INDEX"] = index

    st.session_state.widgets.append(w)


# NOTE: Layout Function
def exportLayout():
    data = {"DATA_SOURCE": [], "DISPLAY_TYPE": []}
    for widget in st.session_state.widgets:
        for s in WIDGET_SETTING:
            data[s] = data.get(s, [])
            data[s].append(widget.get(s, None))

    df = pd.DataFrame(data)
    return df.to_csv().encode("utf-8")


def importLayout(csvLayout):
    if csvLayout is not None:
        st.session_state.widgets = []
        dfLayout = pd.read_csv(csvLayout, converters={"FILTERS": ast.literal_eval})
        dfLayout = dfLayout.sort_values(by="WIDGET_INDEX")

        for i in range(len(dfLayout)):
            widget = dict()
            for s in WIDGET_SETTING:
                widget[s] = dfLayout[s].iloc[i]

            saveConfig(widget["DATA_SOURCE"], widget["DISPLAY_TYPE"], widget)
        st.session_state.widget_index = dfLayout["WIDGET_INDEX"].max()
