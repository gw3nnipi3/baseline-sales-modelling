import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
import pandas as pd
from pathlib import Path
from typing import Any
import ast
from utils.global_const import (
    WIDGET_SETTING,
    WIDGET_DISPLAY_TYPE,
    WIDGET_COLUMN_COUNT,
    PLACHOLDER_STR,
    FILTER_LIST,
)
from utils.widget_helpers import (
    widgetOptionFilter,
    widgetOptionDate,
    widgetCannibalOption,
    createKPI,
    createForecast,
    createPredObs,
    createBacktest,
    createDecomposition,
)


def match_and_render(widget):
    display_type = widget["DISPLAY_TYPE"]
    match display_type:
        case "KPI":
            createKPI(widget)
            pass
        case "Forecast":
            createForecast(widget)
            pass
        case "Predicted Vs. Observed":
            createPredObs(widget)
            pass
        case "Backtest Performance":
            createBacktest(widget)
            pass
        case "Decomposition":
            createDecomposition(widget)
            pass
        case _:
            st.success(f"widget display for {display_type}")
            pass

# NOTE: Widget render function


@st.fragment
def renderWidget(widget: dict[str, Any]):
    widget_idx = widget["WIDGET_INDEX"]
    widget_title = widget["WIDGET_TITLE"]

    widget["FILTERS"] = (
        {key: PLACHOLDER_STR for key in FILTER_LIST}
        if not widget["FILTERS"]
        else widget["FILTERS"]
    )

    # NOTE: REVAMPED RENDER WIGET
    title_container = st.empty()
    title_container.title(f"{widget_title}")
    col = st.columns(2)
    widget_display_slot = st.empty()

    with col[0].popover("Change Title"):
        new_title = st.text_input("New Title", widget["WIDGET_TITLE"])
        widget["WIDGET_TITLE"] = new_title
        title_container.title(new_title)

    with col[1].popover("Select Product"):
        # Insert Option Code HERE
        widgetOptionFilter(widget)

        # Insert Date Code HERE
        widgetOptionDate(widget)

        widgetCannibalOption(widget)

        cols = st.columns(2)
        if cols[0].button("Clear Option", key=f"{widget_idx}_clear_btn"):
            widgetOptionFilter(widget, toClear=True)
            widgetOptionDate(widget, toClear=True)
            widgetCannibalOption(widget, toClear=True)

        if cols[1].button("Confirm Config", key=f"{widget_idx}_confirm_config_btn"):
            st.toast("Configuration Confirmed!")

    with widget_display_slot.container():
        match_and_render(widget)

    if st.button("Delete Widget", key=f"{widget_idx}_delte_widget"):
        st.session_state["widgets"].remove(widget)
        st.rerun()
    # NOTE:--------New Widget Render END-------------


def renderAll():
    widgetCols = st.columns(WIDGET_COLUMN_COUNT)
    for i, widget in enumerate(st.session_state.widgets):
        col = i % WIDGET_COLUMN_COUNT

        with widgetCols[col]:
            renderWidget(widget)
            print("|||||||||| RENDER ALL ||||||||||")
            print(widget)
            print("|||||||||| RENDER ALL ||||||||||")


@ st.fragment
def addWidget():
    with st.popover("+ Add Widget"):
        datasetPath = Path("data/")
        datasets = [f.name for f in datasetPath.iterdir() if f.is_file()]
        datasets.insert(0, "Pick Dataset")

        widgetTitle = st.text_input(
            "Widget Title", f"Widget #{st.session_state.widget_index + 1}"
        )
        dataSource = st.selectbox("Data Source", datasets, 0)
        displayType = st.selectbox("Display Type", WIDGET_DISPLAY_TYPE, 0)

        if dataSource == "Pick Dataset":
            st.error("Choose a valid dataset")

        else:
            if st.button("Save & Add"):
                saveConfig(
                    data_source=dataSource,
                    display_type=displayType,
                    widget_title=widgetTitle,
                )
                st.rerun()


def saveConfig(
    widget_title: str,
    data_source: str,
    display_type: str,
    widget: dict[str, Any] = dict()
):
    w = dict()
    for s in WIDGET_SETTING:
        w[s] = widget.get(s, None)

    w["DATA_SOURCE"] = widget.get("DATA_SOURCE", data_source)
    w["DISPLAY_TYPE"] = widget.get("DISPLAY_TYPE", display_type)
    w["WIDGET_TITLE"] = widget.get("WIDGET_TITLE", widget_title)

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


def safeParse(val):
    if pd.isna(val) or val == "" or val is None:
        return None
    try:
        return ast.literal_eval(str(val))
    except (ValueError, SyntaxError):
        return val


def importLayout(csvLayout):
    if csvLayout is None:
        return

    st.session_state.widgets = []
    dfLayout = pd.read_csv(csvLayout)
    dfLayout = dfLayout.reindex(columns=WIDGET_SETTING)

    # for key in WIDGET_SETTING:
    #    if key not in dfLayout.columns:
    #        dfLayout[key] = None
    # print(dfLayout.tail())

    cols_to_convert = ["FILTERS", "PROMOTION_WINDOWS"]
    # this is for backward compatibility
    for col in cols_to_convert:
        dfLayout[col] = dfLayout[col].apply(safeParse)

    dfLayout = dfLayout.sort_values(by="WIDGET_INDEX")

    for i in range(len(dfLayout)):
        widget = dict()
        for s in WIDGET_SETTING:
            widget[s] = dfLayout[s].iloc[i]

        saveConfig(
            data_source=widget["DATA_SOURCE"],
            display_type=widget["DISPLAY_TYPE"],
            widget_title=widget["WIDGET_TITLE"],
            widget=widget,
        )
    st.session_state.widget_index = dfLayout["WIDGET_INDEX"].max()
    st.session_state.widget_index = dfLayout["WIDGET_INDEX"].max()
